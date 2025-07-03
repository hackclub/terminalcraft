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
        self.save_dir = Path.home() / "TermFlow"
        self.save_dir.mkdir(exist_ok=True)
        self.description: str = ""
        self.workflows_file = self.save_dir / "workflows.json"
        if not self.workflows_file.exists():
            with open(self.workflows_file, "w") as f:
                json.dump({}, f)

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
        table = Table(title="Current Workflow Commands", show_lines=True)
        table.add_column("#", justify="right", style="cyan")
        table.add_column("Command", justify="left", style="white")
        for idx, cmd in enumerate(self.commands, 1):
            table.add_row(str(idx), cmd)
        console.print(table)

    def save_workflow(self):
        if not self.commands:
            console.print("[red]No commands to save.[/]")
            return
        name = Prompt.ask("Enter a name for this workflow (no extension needed)").strip()
        if not self.description:
            self.description = Prompt.ask("Enter a description for this workflow", default="No description")
        else:
            if Confirm.ask(f"Current description: '{self.description}'. Change it?", default=False):
                self.description = Prompt.ask("Enter a description for this workflow", default=self.description)
        try:
            with open(self.workflows_file, "r") as f:
                workflows = json.load(f)
        except Exception:
            workflows = {}
        key = next((k for k in workflows if k.strip().lower() == name.lower()), name)
        workflows[key] = {
            "description": self.description,
            "commands": self.commands
        }
        try:
            with open(self.workflows_file, "w") as f:
                json.dump(workflows, f, indent=2)
            console.print(f"[green]Workflow '{key}' saved to {self.workflows_file}")
            self.file_path = self.workflows_file
        except Exception as e:
            console.print(f"[red]Failed to save workflow: {e}[/]")

    def load_workflow(self):
        self.files(show_delete=False)
        name = Prompt.ask("Enter workflow name to load (no extension needed)").strip()
        try:
            with open(self.workflows_file, "r") as f:
                workflows = json.load(f)
        except Exception as e:
            console.print(f"[red]Failed to read workflows: {e}[/]")
            return
        key = next((k for k in workflows if k.strip().lower() == name.lower()), None)
        if not key:
            console.print(f"[red]Workflow '{name}' does not exist in {self.workflows_file}.[/]")
            return
        wf = workflows[key]
        cmds = wf.get("commands", [])
        desc = wf.get("description", "No description")
        if not isinstance(cmds, list) or not all(isinstance(c, str) for c in cmds):
            console.print("[red]Invalid workflow format.[/]")
            return
        self.commands = cmds
        self.description = desc
        console.print(f"[green]Loaded workflow '{key}' with {len(cmds)} commands.[/]")
        console.print(Panel(f"[bold]Description:[/] {self.description}", title="Workflow Description"))
        self.file_path = self.workflows_file

    def files(self, show_delete=True):
        try:
            with open(self.workflows_file, "r") as f:
                workflows = json.load(f)
        except Exception:
            workflows = {}
        if not workflows:
            console.print(f"[yellow]No saved workflows in {self.workflows_file}.[/]")
            return
        table = Table(title=f"Saved Workflows in {self.workflows_file}", show_lines=True)
        table.add_column("#", justify="right", style="cyan")
        table.add_column("Workflow Name", justify="left", style="white")
        table.add_column("Description", justify="left", style="magenta")
        for idx, (name, wf) in enumerate(workflows.items(), 1):
            desc = wf.get("description", "")
            table.add_row(str(idx), name, desc)
        console.print(table)
        if show_delete and Confirm.ask("Do you want to delete a workflow?", default=False):
            del_name = Prompt.ask("Enter workflow name to delete").strip()
            key = next((k for k in workflows if k.strip().lower() == del_name.lower()), None)
            if key:
                del workflows[key]
                with open(self.workflows_file, "w") as f:
                    json.dump(workflows, f, indent=2)
                console.print(f"[green]Deleted workflow '{key}'")
            else:
                console.print(f"[red]Workflow '{del_name}' does not exist.[/]")

    def run_commands(self):
        if not self.commands:
            console.print("[yellow]No commands to run.[/]")
            return
        console.print(Panel(f"[bold yellow]Running Workflow Commands[/]\n[bold]Description:[/] {self.description}"))
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
        if Confirm.ask("Clear all commands from workflow?", default=False):
            self.commands = []
            self.file_path = None
            self.description = ""
            console.print("[green]Workflow cleared.[/]")

    def about(self):
        console.print(Panel("""
[bold magenta]TermFlow[/] - Terminal Workflow Automator\n\nMade by GitHub user jeninh for Hack Club's terminalcraft.
        """, title="About TermFlow"))

    def help(self):
        help_text = """
[bold cyan]TermFlow Help[/]

[bold]add[/]:    Add one or more shell commands to your workflow.
[bold]list[/]:   List the current workflow commands.
[bold]run[/]:    Run all commands in the current workflow, stopping on error.
[bold]save[/]:   Save the current workflow to a file in ~/TermFlow.
[bold]load[/]:   Load a workflow from a file in ~/TermFlow.
[bold]clear[/]:  Clear all commands from the current workflow.
[bold]files[/]:  Show all saved workflow files in ~/TermFlow.
[bold]about[/]:  Show information about TermFlow.
[bold]help[/]:   Show this help message.
[bold]quit[/]:   Exit TermFlow.
        """
        console.print(Panel(help_text, title="Help"))

    def tutorial(self):
        tutorial_text = """
[bold magenta]TermFlow Tutorial[/]

1. [bold]add[/]: Add commands to your workflow, one at a time. Each command is a shell command you want to automate.
2. [bold]save[/]: Save your current workflow. You'll be prompted for a description and filename.
3. [bold]files[/]: View all saved workflows, their descriptions, and optionally delete them.
4. [bold]load[/]: Load a saved workflow by filename. The description will be shown.
5. [bold]list[/]: See the commands in your current workflow.
6. [bold]run[/]: Run all commands in your current workflow, stopping if any command fails.
7. [bold]clear[/]: Clear your current workflow (commands and description).
8. [bold]about[/] or [bold]help[/]: See info or a summary of commands.

[bold yellow]Tip:[/] You can use [bold]up/down arrows[/] to repeat previous commands in your terminal.
"""
        console.print(Panel(tutorial_text, title="Tutorial"))

    def main_loop(self):
        console.print(Panel("[bold magenta]Welcome to TermFlow Workflow Automator[/]\nBuild, save, load, and run terminal workflows"))
        actions = {
            "add": self.add_command,
            "list": self.list_commands,
            "run": self.run_commands,
            "save": self.save_workflow,
            "load": self.load_workflow,
            "clear": self.clear_commands,
            "files": self.files,
            "about": self.about,
            "help": self.help,
            "tutorial": self.tutorial,
            "quit": None
        }
        while True:
            console.print("\n[bold]Available actions:[/]")
            console.print("[magenta]Type 'help' to see all commands.[/]")
            action = Prompt.ask(
                "Choose action",
                choices=list(actions.keys()),
                default=None,
                show_choices=False
            )
            if action == "quit":
                console.print("[bold]Goodbye![/]")
                break
            func = actions.get(action)
            if func:
                if action == "add":
                    while self.add_command():
                        pass
                elif action == "files":
                    self.files()
                else:
                    func()


if __name__ == "__main__":
    TermFlow().main_loop()
