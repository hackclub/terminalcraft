import os
import shutil
import platform
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.prompt import Prompt
from rich.tree import Tree
import time

class StorageAnalyzer:
    def __init__(self):
        self.console = Console()
        self.system = platform.system()

    def format_bytes(self, bytes_val):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f} PB"

    def get_disk_usage(self):
        disks = []
        if self.system == "Windows":
            import string
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    try:
                        total, used, free = shutil.disk_usage(drive)
                        disks.append({
                            'path': drive,
                            'total': total,
                            'used': used,
                            'free': free,
                            'percent': (used / total) * 100
                        })
                    except:
                        pass
        else:
            for mount in ['/'] + ['/home', '/tmp', '/var']:
                if os.path.exists(mount):
                    try:
                        total, used, free = shutil.disk_usage(mount)
                        disks.append({
                            'path': mount,
                            'total': total,
                            'used': used,
                            'free': free,
                            'percent': (used / total) * 100
                        })
                    except:
                        pass
        return disks

    def show_disk_usage(self):
        self.console.print("\n[bold cyan]Disk Usage Analysis[/bold cyan]")
        
        disks = self.get_disk_usage()
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Drive/Mount", style="cyan")
        table.add_column("Total", justify="right")
        table.add_column("Used", justify="right")
        table.add_column("Free", justify="right")
        table.add_column("Usage %", justify="right")
        table.add_column("Status", justify="center")

        for disk in disks:
            status = "🔴" if disk['percent'] > 90 else "🟡" if disk['percent'] > 75 else "🟢"
            table.add_row(
                disk['path'],
                self.format_bytes(disk['total']),
                self.format_bytes(disk['used']),
                self.format_bytes(disk['free']),
                f"{disk['percent']:.1f}%",
                status
            )

        self.console.print(table)

    def find_large_files(self, path, min_size_mb=100):
        large_files = []
        min_size = min_size_mb * 1024 * 1024
        
        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        size = os.path.getsize(file_path)
                        if size > min_size:
                            large_files.append({
                                'path': file_path,
                                'size': size,
                                'name': file
                            })
                    except (OSError, PermissionError):
                        continue
                        
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
        except (OSError, PermissionError):
            pass
            
        return sorted(large_files, key=lambda x: x['size'], reverse=True)[:20]

    def show_large_files(self):
        path = Prompt.ask(
            "\n[bold]Enter path to scan[/bold]", 
            default="/" if self.system != "Windows" else "C:\\"
        )
        
        min_size = Prompt.ask(
            "[bold]Minimum file size (MB)[/bold]", 
            default="100"
        )
        
        try:
            min_size = int(min_size)
        except ValueError:
            min_size = 100

        self.console.print(f"\n[bold yellow]Scanning {path} for files larger than {min_size}MB...[/bold yellow]")
        
        with self.console.status("[bold green]Scanning..."):
            large_files = self.find_large_files(path, min_size)

        if not large_files:
            self.console.print(f"[green]No files larger than {min_size}MB found[/green]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("File Name", style="cyan", max_width=40)
        table.add_column("Size", justify="right")
        table.add_column("Path", style="dim", max_width=60)

        for file_info in large_files:
            table.add_row(
                file_info['name'],
                self.format_bytes(file_info['size']),
                file_info['path']
            )

        panel = Panel(table, title="[bold]Large Files Found[/bold]", border_style="yellow")
        self.console.print(panel)

    def get_directory_size(self, path):
        total = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    try:
                        filepath = os.path.join(dirpath, filename)
                        total += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        continue
        except (OSError, PermissionError):
            pass
        return total

    def show_directory_analysis(self):
        path = Prompt.ask(
            "\n[bold]Enter directory path[/bold]", 
            default="/" if self.system != "Windows" else "C:\\"
        )
        
        if not os.path.exists(path):
            self.console.print("[red]Path does not exist![/red]")
            return

        self.console.print(f"\n[bold yellow]Analyzing directory: {path}[/bold yellow]")
        
        subdirs = []
        try:
            with self.console.status("[bold green]Calculating sizes..."):
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        size = self.get_directory_size(item_path)
                        subdirs.append({'name': item, 'size': size, 'path': item_path})
        except PermissionError:
            self.console.print("[red]Permission denied![/red]")
            return

        subdirs.sort(key=lambda x: x['size'], reverse=True)

        if not subdirs:
            self.console.print("[yellow]No subdirectories found[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Directory", style="cyan")
        table.add_column("Size", justify="right")
        table.add_column("Path", style="dim", max_width=50)

        for subdir in subdirs[:15]:
            table.add_row(
                subdir['name'],
                self.format_bytes(subdir['size']),
                subdir['path']
            )

        panel = Panel(table, title="[bold]Directory Sizes[/bold]", border_style="blue")
        self.console.print(panel)

    def show_storage_menu(self):
        menu_text = """
[bold green]1.[/bold green] Show Disk Usage
[bold green]2.[/bold green] Find Large Files
[bold green]3.[/bold green] Directory Analysis
[bold red]0.[/bold red] Back to Main Menu
        """
        
        panel = Panel(
            menu_text.strip(),
            title="[bold]Storage Analyzer[/bold]",
            border_style="cyan"
        )
        self.console.print(panel)

    def run(self):
        while True:
            self.console.clear()
            self.show_storage_menu()
            
            choice = Prompt.ask(
                "\n[bold]Select option[/bold]",
                choices=["0", "1", "2", "3"],
                default="0"
            )
            
            if choice == "0":
                break
            elif choice == "1":
                self.show_disk_usage()
            elif choice == "2":
                self.show_large_files()
            elif choice == "3":
                self.show_directory_analysis()
            
            if choice != "0":
                input("\nPress Enter to continue...")