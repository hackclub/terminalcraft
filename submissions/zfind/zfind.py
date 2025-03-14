from textual.app import App, ComposeResult, SystemCommand
from textual.containers import Vertical, ScrollableContainer
from textual.widgets import Button, Static, Input
from textual.screen import Screen
from typing import Iterable
from rich import print
import pyperclip
import os
import re
import uuid
import configparser
import platform

CONFIG_PATH = "config.ini"
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

if platform.system() == 'Windows':
    HISTORY_PATH = os.path.expandvars(r"%appdata%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt")
else:
    HISTORY_PATH = os.path.expanduser(config.get("Settings", "history_file", fallback="~/.zsh_history"))

class ZshHistoryApp(App):
    CSS_PATH = "styles.tcss"

    def __init__(self):
        super().__init__()
        self.commands = self.load_history()

    def load_history(self):
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as file:
                lines = file.readlines()
                commands = [re.sub(r"^: \d+:\d+;", "", line.strip()) for line in lines]
                return list(dict.fromkeys(reversed(commands)))
        except FileNotFoundError:
            return ["[History file not found]"]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("Zfind", classes="header"),
            Static("Press 'q' to quit, 'c' to clear search", classes="header-shortcuts"),
            Static("Search:", classes="header"),
            Input(placeholder="Type to filter...", id="search", classes="input"),
            ScrollableContainer(id="command_list"),
            Static("Waiting for command...", id="status", classes="status"),
        )

    def on_mount(self) -> None:
        self.update_command_list(self.commands)

    def update_command_list(self, filtered_commands):
        container = self.query_one("#command_list", ScrollableContainer)
        filtered_commands = filtered_commands[:]
        container.remove_children(tuple(container.children))
        buttons = [Button(cmd, id=f"cmd_{uuid.uuid4()}") for cmd in filtered_commands]
        container.mount(*buttons)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        command = event.button.label
        pyperclip.copy(command)
        all_widgets = self.query("Static")
        print("All Static widgets:", [widget.id for widget in all_widgets if widget.id])
        try:
            status_widget = self.query_one("#status", Static)
            status_widget.update(f"Copied: {command}")
            print(f"Updated status widget: Copied '{command}'")
        except Exception as e:
            print("Error updating status widget:", e)

    def on_input_changed(self, event: Input.Changed) -> None:
        query = event.value.lower()
        filtered = [cmd for cmd in self.commands if query in cmd.lower()]
        self.update_command_list(filtered)

    BINDINGS = [
        ("q", "quit", "Quit the application"),
        ("c", "clear_search", "Clear the search input"),
        ("h", "change_history_file", "Change the history file"),
        ("escape", "exit_search", "Exit the search input")
    ]

    def action_quit(self) -> None:
        self.exit()

    def action_clear_search(self) -> None:
        self.query_one("#search", Input).value = ""
        self.update_command_list(self.commands)

    def action_change_history_file(self) -> None:
        if platform.system() in ['Linux', 'Darwin']:  # Only apply to macOS or Linux users
            self.change_history_file()

    def action_exit_search(self) -> None:
        self.query_one("#search", Input).blur()

    def change_history_file(self) -> None:
        global HISTORY_PATH
        current_history_file = HISTORY_PATH
        if current_history_file == os.path.expanduser("~/.zsh_history"):
            new_history_file = os.path.expanduser("~/.bash_history")
        else:
            new_history_file = os.path.expanduser("~/.zsh_history")

        config["Settings"] = {"history_file": new_history_file}
        with open(CONFIG_PATH, "w") as configfile:
            config.write(configfile)
        HISTORY_PATH = new_history_file
        self.commands = self.load_history()
        self.update_command_list(self.commands)
        self.query_one("#status", Static).update(f"Switched to {new_history_file}")

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)
        if platform.system() in ['Linux', 'Darwin']:  # Only apply to macOS or Linux users
            yield SystemCommand("Change History File", "Change the history file being used", self.action_change_history_file)

    def notify(self, message: str) -> None:
        print(f"[bold magenta]{message}[/bold magenta]")

if __name__ == "__main__":
    ZshHistoryApp().run()
