from textual.app import ComposeResult
from textual.containers import Center, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static

from postperson import Binding


class UnsavedExitConfirmation(ModalScreen):
    CSS_PATH = "css/unsaved_exit_confirmation.tcss"

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Close"),
        Binding("y", "yes", "Yes"),
        Binding("n", "no", "No"),
    ]

    def __init__(self, action: str = "quit") -> None:
        self.action = action

        super().__init__()

    def compose(self) -> ComposeResult:
        with Static(classes="confirmation-box"):
            with Center():
                yield Label(
                    "You have unsaved changes. Are you sure you want to exit?", 
                    id="confirmation"
                )
            with Center():
                with Horizontal(id="button-row"):
                    yield Button("No", id="no")
                    yield Button("Yes", id="yes")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            await self.action_yes()
        else:
            self.action_no()

    async def action_yes(self) -> None:
        self.app.pop_screen()
        if self.action == "quit":
            await self.app.action_quit()
        else:
            self.app.pop_screen()

    def action_no(self) -> None:
        self.app.pop_screen()


class DeleteConfirmation(ModalScreen):
    CSS_PATH = "css/delete_confirmation.tcss"

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Close"),
    ]

    def compose(self) -> ComposeResult:
        with Static(classes="confirmation-box"):
            with Center():
                yield Label(
                    "Are you sure you want to delete this request?", 
                    id="confirmation"
                )
            with Center():
                with Horizontal(id="button-row"):
                    yield Button("No", id="no")
                    yield Button("Yes", id="yes")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")


class ErrorModal(ModalScreen):
    CSS_PATH = "css/error_modal.tcss"

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Close"),
    ]

    def __init__(self, message: str) -> None:
        self.message = message

        super().__init__()

    def compose(self) -> ComposeResult:
        with Static(classes="error-box"):
            with Center():
                yield Label("[red][b]Error![/][/]", id="title")
            with Center():
                yield Label(self.message, id="error")
            with Center():
                yield Button("Close", id="close")

    async def on_button_pressed(self, _: Button.Pressed) -> None:
        self.app.pop_screen()
