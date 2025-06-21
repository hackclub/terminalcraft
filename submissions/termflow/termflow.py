import json
import shlex
import subprocess
from pathlib import Path
from typing import List, Dict
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel

console = Console()

class TermFlow:
    def __init__(self):
        self.commands: List[str] = []
        self.file_path: Path = None

    def add_command(self):
        cmd = Prompt.ask("Enter a shell command to add (leave blank to stop)")
        if cmd.strip():
            self.commands.append(cmd.strip())
            console.print(f"[green]Added command:[/] {cmd}")
            return True
        return False

    def list_commands(self):
        if not self.commands:
            console.print("[yellow]No commands added yet.[/]")
            return
        table = Table(title="Current Workflow Commands")
        table.add_column("#", justify="right")
        table.add_column("Command", justify="left")
        for idx, cmd in enumerate(self.commands, 1):
            table.add_row(str(idx), cmd)
        console.print(table)

    def save_workflow(self):
        if not self.commands:
            console.print("[red]No commands to save.[/]")
            return
        path_str = Prompt.ask("Enter filename to save workflow", default="workflow.json")
        path = Path(path_str)
        data = {"commands": self.commands}
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            console.print(f"[green]Workflow saved to {path}[/]")
            self.file_path = path
        except Exception as e:
            console.print(f"[red]Failed to save file: {e}[/]")

    def load_workflow(self):
        path_str = Prompt.ask("Enter filename to load workflow from", default="workflow.json")
        path = Path(path_str)
        if not path.exists():
            console.print(f"[red]File {path} does not exist.[/]")
            return
        try:
            with open(path, "r") as f:
                data = json.load(f)
            cmds = data.get("commands", [])
            if not isinstance(cmds, list) or not all(isinstance(c, str) for c in cmds):
                console.print("[red]Invalid workflow format.[/]")
                return
            self.commands = cmds
            console.print(f"[green]Loaded workflow with {len(cmds)} commands.[/]")
            self.file_path = path
        except Exception as e:
            console.print(f"[red]Failed to load file: {e}[/]")

    def run_commands(self):
        if not self.commands:
            console.print("[yellow]No commands to run.[/]")
            return
        console.print(Panel("[bold yellow]Running Workflow Commands[/]"))
        for idx, cmd in enumerate(self.commands, 1):
            console.print(f"[cyan]Step {idx}:[/] {cmd}")
            try:
                process = subprocess.Popen(
                    shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False
                )
                stdout, stderr = process.communicate()
                success = process.returncode == 0
                if stdout:
                    console.print(f"[white]{stdout.decode(errors='ignore')}[/]")
                if stderr:
                    console.print(f"[red]{stderr.decode(errors='ignore')}[/]")
                if success:
                    console.print(f"[green]Step {idx} succeeded.[/]\n")
                else:
                    console.print(f"[red]Step {idx} failed with exit code {process.returncode}.[/]\n")
                    break  # stop on failure
            except Exception as e:
                console.print(f"[red]Error running command: {e}[/]")
                break

    def clear_commands(self):
        if Confirm.ask("Clear all commands from workflow?"):
            self.commands = []
            self.file_path = None
            console.print("[green]Workflow cleared.[/]")

    def main_loop(self):
        console.print(Panel("[bold magenta]Welcome to TermFlow Workflow Automator[/]\nBuild, save, load, and run terminal workflows"))
        while True:
            action = Prompt.ask(
                "Choose action",
                choices=["add", "list", "run", "save", "load", "clear", "quit"],
                default="add",
            )
            if action == "add":
                while self.add_command():
                    pass
            elif action == "list":
                self.list_commands()
            elif action == "run":
                self.run_commands()
            elif action == "save":
                self.save_workflow()
            elif action == "load":
                self.load_workflow()
            elif action == "clear":
                self.clear_commands()
            elif action == "quit":
                console.print("[bold]Have a nice day! Thanks for using TermFlow! I like trains![/]")
                break


if __name__ == "__main__":
    TermFlow().main_loop()
