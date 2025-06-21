#!/usr/bin/env python3

import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.prompt import Prompt
import time

try:
    from storage_analyzer import StorageAnalyzer
    from network_analyzer import NetworkAnalyzer
    from task_manager import TaskManager
    from system_monitor import SystemMonitor
except ImportError as e:
    print(f"Missing module: {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

class SystemAnalyzer:
    def __init__(self):
        self.console = Console()
        self.storage = StorageAnalyzer()
        self.network = NetworkAnalyzer()
        self.tasks = TaskManager()
        self.monitor = SystemMonitor()

    def show_banner(self):
        banner = Text("SYSTEM ANALYZER", style="bold cyan")
        subtitle = Text("Cross-platform system analysis tool", style="dim")
        
        panel = Panel(
            Align.center(banner + "\n" + subtitle),
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(panel)
        self.console.print()

    def show_main_menu(self):
        menu_text = """
[bold green]1.[/bold green] Storage Analyzer
[bold green]2.[/bold green] Network Analyzer  
[bold green]3.[/bold green] Task Manager
[bold green]4.[/bold green] System Monitor
[bold green]5.[/bold green] Run All Diagnostics
[bold red]0.[/bold red] Exit
        """
        
        panel = Panel(
            menu_text.strip(),
            title="[bold]Main Menu[/bold]",
            border_style="green"
        )
        self.console.print(panel)

    def run_all_diagnostics(self):
        self.console.print("\n[bold yellow]Running comprehensive system analysis...[/bold yellow]")
        
        with self.console.status("[bold green]Analyzing storage..."):
            time.sleep(1)
            self.storage.show_disk_usage()
        
        with self.console.status("[bold green]Checking network..."):
            time.sleep(1)
            self.network.show_network_info()
        
        with self.console.status("[bold green]Getting system info..."):
            time.sleep(1)
            self.monitor.show_system_info()
        
        self.console.print("\n[bold green]✓ Diagnostic complete![/bold green]")
        input("\nPress Enter to continue...")

    def run(self):
        while True:
            self.console.clear()
            self.show_banner()
            self.show_main_menu()
            
            choice = Prompt.ask(
                "\n[bold]Select option[/bold]",
                choices=["0", "1", "2", "3", "4", "5"],
                default="0"
            )
            
            if choice == "0":
                self.console.print("\n[bold green]Goodbye![/bold green]")
                break
            elif choice == "1":
                self.storage.run()
            elif choice == "2":
                self.network.run()
            elif choice == "3":
                self.tasks.run()
            elif choice == "4":
                self.monitor.run()
            elif choice == "5":
                self.run_all_diagnostics()

if __name__ == "__main__":
    try:
        analyzer = SystemAnalyzer()
        analyzer.run()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)