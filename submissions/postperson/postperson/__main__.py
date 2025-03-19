from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input

from postperson.validators import FilePathValidator
from postperson.widgets import ErrorWidget
from postperson.session import Session
from postperson import Binding


class PostPerson(App):
    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    CSS_PATH = "css/main.tcss"

    def on_mount(self) -> None:
        self.theme = "catppuccin-mocha"

    def compose(self) -> ComposeResult:
        yield Header()

        # Maybe I should make a custom widget class which merges Input and ErrotWidget and do a `yield from` on that
        yield Input(
            "Create Session",
            validators=[
                FilePathValidator(),
            ],
            validate_on=['submitted']
        )
        yield ErrorWidget()

        yield Footer()

    @on(Input.Submitted)
    def show_invalid_reasons(self, event: Input.Changed) -> None:
        if not event.validation_result:
            return

        error_widget = self.query_one("ErrorWidget")

        # I'm only doing this because pyright won't shut up
        if not isinstance(error_widget, ErrorWidget):
            return

        if event.validation_result.is_valid:
            self.push_screen(Session(event.value))
        else:
            reason = "" if len((reasons := event.validation_result.failure_descriptions)) == 0 else reasons[0]
            error_widget.update(reason)


if __name__ == "__main__":
    PostPerson().run()

