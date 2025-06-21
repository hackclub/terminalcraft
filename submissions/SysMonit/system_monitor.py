import psutil
import platform
import time
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.columns import Columns
from rich.live import Live
import json

class SystemMonitor:
    def __init__(self):
        self.console = Console()

    def format_bytes(self, bytes_val):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f} PB"

    def get_system_info(self):
        uname = platform.uname()
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        
        return {
            'system': uname.system,
            'node': uname.node,
            'release': uname.release,
            'version': uname.version,
            'machine': uname.machine,
            'processor': uname.processor,
            'boot_time': boot_time,
            'uptime': datetime.now() - boot_time
        }

    def show_system_info(self):
        self.console.print("\n[bold cyan]System Information[/bold cyan]")
        
        info = self.get_system_info()
        
        table = Table(show_header=False, box=None)
        table.add_column("Property", style="bold cyan", width=15)
        table.add_column("Value", style="white")

        table.add_row("System:", info['system'])
        table.add_row("Node Name:", info['node'])
        table.add_row("Release:", info['release'])
        table.add_row("Machine:", info['machine'])
        table.add_row("Processor:", info['processor'] if info['processor'] else 'Unknown')
        table.add_row("Boot Time:", info['boot_time'].strftime('%Y-%m-%d %H:%M:%S'))
        table.add_row("Uptime:", str(info['uptime']).split('.')[0])

        panel = Panel(table, title="[bold]System Details[/bold]", border_style="blue")
        self.console.print(panel)

    def get_cpu_info(self):
        cpu_freq = psutil.cpu_freq()
        cpu_count_physical = psutil.cpu_count(logical=False)
        cpu_count_logical = psutil.cpu_count(logical=True)
        
        return {
            'physical_cores': cpu_count_physical,
            'logical_cores': cpu_count_logical,
            'max_frequency': cpu_freq.max if cpu_freq else 0,
            'min_frequency': cpu_freq.min if cpu_freq else 0,
            'current_frequency': cpu_freq.current if cpu_freq else 0,
            'cpu_usage': psutil.cpu_percent(interval=1),
            'per_cpu_usage': psutil.cpu_percent(interval=1, percpu=True)
        }

    def show_cpu_info(self):
        self.console.print("\n[bold cyan]CPU Information[/bold cyan]")
        
        cpu_info = self.get_cpu_info()
        
        main_table = Table(show_header=False, box=None)
        main_table.add_column("Property", style="bold cyan", width=20)
        main_table.add_column("Value", style="white")

        main_table.add_row("Physical Cores:", str(cpu_info['physical_cores']))
        main_table.add_row("Logical Cores:", str(cpu_info['logical_cores']))
        
        if cpu_info['max_frequency']:
            main_table.add_row("Max Frequency:", f"{cpu_info['max_frequency']:.2f} MHz")
            main_table.add_row("Min Frequency:", f"{cpu_info['min_frequency']:.2f} MHz")
            main_table.add_row("Current Frequency:", f"{cpu_info['current_frequency']:.2f} MHz")
        
        usage_color = "red" if cpu_info['cpu_usage'] > 80 else "yellow" if cpu_info['cpu_usage'] > 60 else "green"
        main_table.add_row("Overall Usage:", f"[{usage_color}]{cpu_info['cpu_usage']:.1f}%[/{usage_color}]")

        per_cpu_table = Table(show_header=True, header_style="bold magenta")
        per_cpu_table.add_column("Core", justify="center", style="cyan")
        per_cpu_table.add_column("Usage", justify="right")

        for i, usage in enumerate(cpu_info['per_cpu_usage']):
            color = "red" if usage > 80 else "yellow" if usage > 60 else "green"
            per_cpu_table.add_row(f"Core {i}", f"[{color}]{usage:.1f}%[/{color}]")

        cpu_panel = Panel(main_table, title="[bold]CPU Details[/bold]", border_style="green")
        usage_panel = Panel(per_cpu_table, title="[bold]Per-Core Usage[/bold]", border_style="green")
        
        self.console.print(Columns([cpu_panel, usage_panel]))

    def get_memory_info(self):
        virtual_mem = psutil.virtual_memory()
        swap_mem = psutil.swap_memory()
        
        return {
            'total': virtual_mem.total,
            'available': virtual_mem.available,
            'used': virtual_mem.used,
            'free': virtual_mem.free,
            'percent': virtual_mem.percent,
            'swap_total': swap_mem.total,
            'swap_used': swap_mem.used,
            'swap_free': swap_mem.free,
            'swap_percent': swap_mem.percent
        }

    def show_memory_info(self):
        self.console.print("\n[bold cyan]Memory Information[/bold cyan]")
        
        mem_info = self.get_memory_info()
        
        ram_table = Table(show_header=False, box=None)
        ram_table.add_column("Property", style="bold cyan", width=15)
        ram_table.add_column("Value", style="white")

        mem_color = "red" if mem_info['percent'] > 80 else "yellow" if mem_info['percent'] > 60 else "green"
        
        ram_table.add_row("Total RAM:", self.format_bytes(mem_info['total']))
        ram_table.add_row("Available:", self.format_bytes(mem_info['available']))
        ram_table.add_row("Used:", self.format_bytes(mem_info['used']))
        ram_table.add_row("Free:", self.format_bytes(mem_info['free']))
        ram_table.add_row("Usage:", f"[{mem_color}]{mem_info['percent']:.1f}%[/{mem_color}]")

        ram_panel = Panel(ram_table, title="[bold]RAM[/bold]", border_style="blue")

        if mem_info['swap_total'] > 0:
            swap_table = Table(show_header=False, box=None)
            swap_table.add_column("Property", style="bold cyan", width=15)
            swap_table.add_column("Value", style="white")

            swap_color = "red" if mem_info['swap_percent'] > 80 else "yellow" if mem_info['swap_percent'] > 60 else "green"
            
            swap_table.add_row("Total Swap:", self.format_bytes(mem_info['swap_total']))
            swap_table.add_row("Used:", self.format_bytes(mem_info['swap_used']))
            swap_table.add_row("Free:", self.format_bytes(mem_info['swap_free']))
            swap_table.add_row("Usage:", f"[{swap_color}]{mem_info['swap_percent']:.1f}%[/{swap_color}]")

            swap_panel = Panel(swap_table, title="[bold]Swap[/bold]", border_style="yellow")
            self.console.print(Columns([ram_panel, swap_panel]))
        else:
            self.console.print(ram_panel)

    def get_disk_info(self):
        disk_usage = []
        disk_io = psutil.disk_io_counters(perdisk=True)
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info = {
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'file_system': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': (usage.used / usage.total) * 100
                }
                disk_usage.append(disk_info)
            except PermissionError:
                continue
        
        return disk_usage, disk_io

    def show_disk_info(self):
        self.console.print("\n[bold cyan]Disk Information[/bold cyan]")
        
        disk_usage, disk_io = self.get_disk_info()
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Device", style="cyan")
        table.add_column("Mountpoint", style="green")
        table.add_column("File System", style="dim")
        table.add_column("Total", justify="right")
        table.add_column("Used", justify="right")
        table.add_column("Free", justify="right")
        table.add_column("Usage%", justify="right")

        for disk in disk_usage:
            usage_color = "red" if disk['percent'] > 90 else "yellow" if disk['percent'] > 75 else "green"
            
            table.add_row(
                disk['device'],
                disk['mountpoint'],
                disk['file_system'],
                self.format_bytes(disk['total']),
                self.format_bytes(disk['used']),
                self.format_bytes(disk['free']),
                f"[{usage_color}]{disk['percent']:.1f}%[/{usage_color}]"
            )

        panel = Panel(table, title="[bold]Disk Usage[/bold]", border_style="green")
        self.console.print(panel)

    def show_sensors_info(self):
        self.console.print("\n[bold cyan]Sensors Information[/bold cyan]")
        
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                temp_table = Table(show_header=True, header_style="bold magenta")
                temp_table.add_column("Sensor", style="cyan")
                temp_table.add_column("Temperature", justify="right")
                temp_table.add_column("High", justify="right")
                temp_table.add_column("Critical", justify="right")

                for name, entries in temps.items():
                    for entry in entries:
                        temp_color = "red" if entry.current > 80 else "yellow" if entry.current > 60 else "green"
                        temp_table.add_row(
                            f"{name} ({entry.label or 'N/A'})",
                            f"[{temp_color}]{entry.current:.1f}°C[/{temp_color}]",
                            f"{entry.high:.1f}°C" if entry.high else "N/A",
                            f"{entry.critical:.1f}°C" if entry.critical else "N/A"
                        )

                temp_panel = Panel(temp_table, title="[bold]Temperature Sensors[/bold]", border_style="red")
                self.console.print(temp_panel)
            else:
                self.console.print("[yellow]No temperature sensors found[/yellow]")

        except AttributeError:
            self.console.print("[yellow]Temperature sensors not supported on this platform[/yellow]")

        try:
            fans = psutil.sensors_fans()
            if fans:
                fan_table = Table(show_header=True, header_style="bold magenta")
                fan_table.add_column("Fan", style="cyan")
                fan_table.add_column("Speed (RPM)", justify="right")

                for name, entries in fans.items():
                    for entry in entries:
                        fan_table.add_row(
                            f"{name} ({entry.label or 'N/A'})",
                            f"{entry.current} RPM"
                        )

                fan_panel = Panel(fan_table, title="[bold]Fan Sensors[/bold]", border_style="blue")
                self.console.print(fan_panel)

        except AttributeError:
            pass

    def show_realtime_monitor(self, duration=30):
        self.console.print(f"\n[bold yellow]Real-time System Monitor ({duration}s)[/bold yellow]")
        self.console.print("[dim]Press Ctrl+C to stop[/dim]")
        
        def create_monitor_layout():
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            cpu_color = "red" if cpu_percent > 80 else "yellow" if cpu_percent > 60 else "green"
            mem_color = "red" if memory.percent > 80 else "yellow" if memory.percent > 60 else "green"
            
            monitor_table = Table(show_header=True, header_style="bold magenta")
            monitor_table.add_column("Resource", style="cyan", width=15)
            monitor_table.add_column("Usage", justify="right", width=15)
            monitor_table.add_column("Status", justify="center", width=10)
            
            monitor_table.add_row(
                "CPU",
                f"[{cpu_color}]{cpu_percent:.1f}%[/{cpu_color}]",
                "🔴" if cpu_percent > 80 else "🟡" if cpu_percent > 60 else "🟢"
            )
            
            monitor_table.add_row(
                "Memory",
                f"[{mem_color}]{memory.percent:.1f}%[/{mem_color}]",
                "🔴" if memory.percent > 80 else "🟡" if memory.percent > 60 else "🟢"
            )
            
            return Panel(
                monitor_table,
                title=f"[bold]System Monitor - {datetime.now().strftime('%H:%M:%S')}[/bold]",
                border_style="green"
            )
        
        try:
            with Live(create_monitor_layout(), refresh_per_second=2) as live:
                start_time = time.time()
                while time.time() - start_time < duration:
                    time.sleep(0.5)
                    live.update(create_monitor_layout())
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Monitoring stopped[/yellow]")

    def show_monitor_menu(self):
        menu_text = """
[bold green]1.[/bold green] System Information
[bold green]2.[/bold green] CPU Information
[bold green]3.[/bold green] Memory Information
[bold green]4.[/bold green] Disk Information
[bold green]5.[/bold green] Sensors Information
[bold green]6.[/bold green] Real-time Monitor
[bold red]0.[/bold red] Back to Main Menu
        """
        
        panel = Panel(
            menu_text.strip(),
            title="[bold]System Monitor[/bold]",
            border_style="cyan"
        )
        self.console.print(panel)

    def run(self):
        while True:
            self.console.clear()
            self.show_monitor_menu()
            
            choice = Prompt.ask(
                "\n[bold]Select option[/bold]",
                choices=["0", "1", "2", "3", "4", "5", "6"],
                default="0"
            )
            
            if choice == "0":
                break
            elif choice == "1":
                self.show_system_info()
            elif choice == "2":
                self.show_cpu_info()
            elif choice == "3":
                self.show_memory_info()
            elif choice == "4":
                self.show_disk_info()
            elif choice == "5":
                self.show_sensors_info()
            elif choice == "6":
                self.show_realtime_monitor()
            
            if choice != "0":
                input("\nPress Enter to continue...")