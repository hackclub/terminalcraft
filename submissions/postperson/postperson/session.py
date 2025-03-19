from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Header

from pathlib import Path
import json

from postperson import Binding
from postperson.widgets import RequestHolder
from postperson.modals import UnsavedExitConfirmation


class Session(Screen):
    DEFAULT_CSS = """
    Session {
        overflow: hidden;
    }
    """

    BINDINGS = [
        Binding("escape", "return", "Back"),
        Binding("s", "save", "Save"),
        Binding("q", "quit", "Back"),
    ]

    def __init__(self, source_file: str) -> None:
        self.source_file = source_file
        if not Path(source_file).exists():
            with open(source_file, "w") as f:
                f.write("[]")

        with open(source_file, "r") as f:
            data = f.read()
            self.data = json.loads(data)

            if not isinstance(self.data, list):
                raise ValueError("Data must be a list")

        self.unsaved_edit = False

        super().__init__()

    def on_mount(self) -> None:
        self.sub_title = self.source_file

    def compose(self) -> ComposeResult:
        self.request_holder = RequestHolder(self.data)

        yield Header()
        yield Button("Add Request", id="add-request", action="add_request")
        yield self.request_holder
        yield Footer()

    def action_save(self) -> None:
        self.data = self.request_holder.compile()
        with open(self.source_file, "w") as f:
            f.write(json.dumps(self.data, indent=4))

        self.notify("Saved")
        self.unsaved_edit = False
        self.refresh()

    def action_return(self) -> None:
        if self.unsaved_edit:
            self.app.push_screen(UnsavedExitConfirmation(action="back"))
        else:
            self.app.pop_screen()

    async def action_quit(self) -> None:
        if self.unsaved_edit:
            self.app.push_screen(UnsavedExitConfirmation())
        else:
            await self.app.action_quit()

    def action_add_request(self) -> None:
        self.data.append({})
        self.request_holder.update(self.data)
        self.unsaved_edit = True


