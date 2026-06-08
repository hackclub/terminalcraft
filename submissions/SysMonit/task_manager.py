import psutil
import time
import signal
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.layout import Layout

class TaskManager:
    def __init__(self):
        self.console = Console()

    def format_bytes(self, bytes_val):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f}{unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f}TB"

    def get_processes(self, sort_by='cpu'):
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'username']):
            try:
                proc_info = proc.info
                proc_info['memory_mb'] = proc.memory_info().rss / 1024 / 1024
                processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if sort_by == 'cpu':
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        elif sort_by == 'memory':
            processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
        elif sort_by == 'name':
            processes.sort(key=lambda x: x['name'] or '')
        
        return processes

    def show_processes(self, sort_by='cpu', limit=20):
        processes = self.get_processes(sort_by)
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("PID", justify="right", style="cyan")
        table.add_column("Name", style="green", max_width=25)
        table.add_column("CPU%", justify="right")
        table.add_column("Memory%", justify="right")
        table.add_column("Memory", justify="right")
        table.add_column("Status", justify="center")
        table.add_column("User", style="dim", max_width=15)

        for proc in processes[:limit]:
            cpu_color = "red" if (proc['cpu_percent'] or 0) > 80 else "yellow" if (proc['cpu_percent'] or 0) > 50 else "white"
            mem_color = "red" if (proc['memory_percent'] or 0) > 80 else "yellow" if (proc['memory_percent'] or 0) > 50 else "white"
            
            status_icon = {
                'running': '🟢',
                'sleeping': '🟡',
                'stopped': '🔴',
                'zombie': '💀'
            }.get(proc['status'], '⚪')
            
            table.add_row(
                str(proc['pid']),
                proc['name'] or 'Unknown',
                f"[{cpu_color}]{proc['cpu_percent']:.1f}%[/{cpu_color}]" if proc['cpu_percent'] else "0.0%",
                f"[{mem_color}]{proc['memory_percent']:.1f}%[/{mem_color}]" if proc['memory_percent'] else "0.0%",
                self.format_bytes(proc['memory_mb'] * 1024 * 1024),
                f"{status_icon} {proc['status']}",
                proc['username'] or 'Unknown'
            )

        return table

    def show_process_list(self):
        sort_options = {'1': 'cpu', '2': 'memory', '3': 'name'}
        
        self.console.print("\n[bold cyan]Process List[/bold cyan]")
        sort_choice = Prompt.ask(
            "[bold]Sort by[/bold] ([green]1[/green]) CPU [green]2[/green]) Memory [green]3[/green]) Name",
            choices=["1", "2", "3"],
            default="1"
        )
        
        sort_by = sort_options[sort_choice]
        table = self.show_processes(sort_by)
        
        panel = Panel(table, title=f"[bold]Processes (sorted by {sort_by.upper()})[/bold]", border_style="green")
        self.console.print(panel)

    def kill_process(self):
        pid = Prompt.ask("\n[bold]Enter PID to terminate[/bold]")
        
        try:
            pid = int(pid)
            process = psutil.Process(pid)
            process_name = process.name()
            
            if Confirm.ask(f"[red]Terminate process '{process_name}' (PID: {pid})?[/red]"):
                process.terminate()
                
                try:
                    process.wait(timeout=3)
                    self.console.print(f"[green]✓ Process {process_name} (PID: {pid}) terminated[/green]")
                except psutil.TimeoutExpired:
                    process.kill()
                    self.console.print(f"[yellow]⚠ Process {process_name} (PID: {pid}) force killed[/yellow]")
                    
        except ValueError:
            self.console.print("[red]Invalid PID![/red]")
        except psutil.NoSuchProcess:
            self.console.print("[red]Process not found![/red]")
        except psutil.AccessDenied:
            self.console.print("[red]Access denied! Try running as administrator/root[/red]")
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")

    def show_system_resources(self):
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Resource", style="cyan")
        table.add_column("Usage", justify="right")
        table.add_column("Total", justify="right")
        table.add_column("Available", justify="right")
        table.add_column("Percent", justify="right")

        cpu_color = "red" if cpu_percent > 80 else "yellow" if cpu_percent > 60 else "green"
        mem_color = "red" if memory.percent > 80 else "yellow" if memory.percent > 60 else "green"
        swap_color = "red" if swap.percent > 80 else "yellow" if swap.percent > 60 else "green"

        table.add_row(
            "CPU",
            f"[{cpu_color}]{cpu_percent:.1f}%[/{cpu_color}]",
            f"{psutil.cpu_count()} cores",
            "-",
            f"[{cpu_color}]{cpu_percent:.1f}%[/{cpu_color}]"
        )
        
        table.add_row(
            "Memory",
            self.format_bytes(memory.used),
            self.format_bytes(memory.total),
            self.format_bytes(memory.available),
            f"[{mem_color}]{memory.percent:.1f}%[/{mem_color}]"
        )
        
        if swap.total > 0:
            table.add_row(
                "Swap",
                self.format_bytes(swap.used),
                self.format_bytes(swap.total),
                self.format_bytes(swap.free),
                f"[{swap_color}]{swap.percent:.1f}%[/{swap_color}]"
            )

        panel = Panel(table, title="[bold]System Resources[/bold]", border_style="blue")
        self.console.print(panel)

    def show_top_processes(self, duration=10):
        self.console.print(f"\n[bold yellow]Real-time process monitor ({duration}s)[/bold yellow]")
        self.console.print("[dim]Press Ctrl+C to stop[/dim]")
        
        try:
            with Live(self.show_processes(), refresh_per_second=2) as live:
                start_time = time.time()
                while time.time() - start_time < duration:
                    time.sleep(0.5)
                    live.update(self.show_processes())
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Monitoring stopped[/yellow]")

    def search_processes(self):
        search_term = Prompt.ask("\n[bold]Enter process name to search[/bold]").lower()
        
        matching_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                if search_term in proc.info['name'].lower():
                    proc_info = proc.info
                    proc_info['memory_mb'] = proc.memory_info().rss / 1024 / 1024
                    matching_processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if not matching_processes:
            self.console.print(f"[yellow]No processes found matching '{search_term}'[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("PID", justify="right", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("CPU%", justify="right")
        table.add_column("Memory%", justify="right")
        table.add_column("Status", justify="center")

        for proc in matching_processes:
            status_icon = {
                'running': '🟢',
                'sleeping': '🟡',
                'stopped': '🔴',
                'zombie': '💀'
            }.get(proc['status'], '⚪')
            
            table.add_row(
                str(proc['pid']),
                proc['name'],
                f"{proc['cpu_percent']:.1f}%" if proc['cpu_percent'] else "0.0%",
                f"{proc['memory_percent']:.1f}%" if proc['memory_percent'] else "0.0%",
                f"{status_icon} {proc['status']}"
            )

        panel = Panel(table, title=f"[bold]Processes matching '{search_term}'[/bold]", border_style="green")
        self.console.print(panel)

    def show_task_menu(self):
        menu_text = """
[bold green]1.[/bold green] Process List
[bold green]2.[/bold green] System Resources
[bold green]3.[/bold green] Real-time Monitor
[bold green]4.[/bold green] Search Processes
[bold green]5.[/bold green] Kill Process
[bold red]0.[/bold red] Back to Main Menu
        """
        
        panel = Panel(
            menu_text.strip(),
            title="[bold]Task Manager[/bold]",
            border_style="cyan"
        )
        self.console.print(panel)

    def run(self):
        while True:
            self.console.clear()
            self.show_task_menu()
            
            choice = Prompt.ask(
                "\n[bold]Select option[/bold]",
                choices=["0", "1", "2", "3", "4", "5"],
                default="0"
            )
            
            if choice == "0":
                break
            elif choice == "1":
                self.show_process_list()
            elif choice == "2":
                self.show_system_resources()
            elif choice == "3":
                self.show_top_processes()
            elif choice == "4":
                self.search_processes()
            elif choice == "5":
                self.kill_process()
            
            if choice != "0":
                input("\nPress Enter to continue...")