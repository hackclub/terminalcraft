from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Input, Button, Static, ProgressBar
from textual.containers import Vertical, Center, Horizontal
from textual.screen import Screen
from textual.binding import Binding
from textual.widgets import Label

from flashcard_cli.data import con, load_flashcards
from flashcard_cli.db import add_flashcard, delete_flashcard, edit_card

class AddFlashcardScreen(Screen):
    """Screen for adding a new flashcard."""

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Question:"),
            Input(placeholder="Enter the question", id="question"),
            Label("Answer:"),
            Input(placeholder="Enter the answer", id="answer"),
            Button("Save", variant="primary", id="save"),
            Button("Cancel", id="cancel"),
            id="add_dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            question = self.query_one("#question", Input).value
            answer = self.query_one("#answer", Input).value
            if question and answer:
                if add_flashcard(con, question, answer):
                    self.app.notify("Flashcard saved successfully!", title="Success", severity="information")
                    self.app.exit()
                else:
                    self.app.notify("Failed to save flashcard.", title="Error", severity="error")
            else:
                self.app.notify("Question and Answer are required.", title="Validation Error", severity="error")
        elif event.button.id == "cancel":
            self.app.exit()


class EditScreen(Screen):
    """Screen for editing a flashcard."""

    def __init__(self, card_id: int, question: str, answer: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.card_id = card_id
        self.question = question
        self.answer = answer

    def compose(self) -> ComposeResult:
        yield Vertical(
            Input(self.question, id="question"),
            Input(self.answer, id="answer"),
            Button("Save", variant="primary", id="save"),
            Button("Cancel", id="cancel"),
            id="edit_dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            new_question = self.query_one("#question", Input).value
            new_answer = self.query_one("#answer", Input).value
            self.dismiss((self.card_id, new_question, new_answer))
        else:
            self.dismiss()


class MainScreen(Screen):
    """Main screen for managing flashcards."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("e", "edit_card", "Edit"),
        Binding("d", "delete_card", "Delete"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flashcards = load_flashcards()

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="flashcard_table")
        yield Footer()

    def on_mount(self) -> None:
        self.update_table()

    def update_table(self):
        self.flashcards = load_flashcards()
        table = self.query_one("#flashcard_table", DataTable)
        table.clear()
        table.add_columns("ID", "Question", "Answer")
        for card in self.flashcards:
            table.add_row(str(card["id"]), card["question"], card["answer"])

    def action_quit(self) -> None:
        self.app.exit()

    def action_edit_card(self) -> None:
        table = self.query_one(DataTable)
        if table.cursor_row >= 0:
            row_key = table.get_row_at(table.cursor_row)[0]
            card_id = int(row_key)
            
            card = next((c for c in self.flashcards if c["id"] == card_id), None)

            if card:
                def update_card(result):
                    if result:
                        card_id, new_question, new_answer = result
                        edit_card(con, card_id, new_question, new_answer)
                        self.update_table()

                self.app.push_screen(EditScreen(card_id, card["question"], card["answer"]), update_card)

    def action_delete_card(self) -> None:
        table = self.query_one(DataTable)
        if table.cursor_row >= 0:
            row_key = table.get_row_at(table.cursor_row)[0]
            card_id = int(row_key)
            delete_flashcard(con, card_id)
            self.update_table()


class AnswerScreen(Screen):
    """Screen to display the answer in a popup."""
    def __init__(self, answer: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.answer = answer

    def compose(self) -> ComposeResult:
        yield Center(
            Vertical(
                Label("Answer"),
                Static(self.answer, id="answer_text"),
                Button("OK", variant="primary", id="ok_button"),
                id="answer_dialog",
            )
        )

    def on_mount(self) -> None:
        self.query_one("#answer_dialog").styles.border = ("heavy", "green")
        self.query_one("#answer_dialog").styles.width = "60%"
        self.query_one("#answer_dialog").styles.height = "auto"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

class CorrectnessScreen(Screen):
    """Screen to ask the user if they were correct."""
    def compose(self) -> ComposeResult:
        yield Center(
            Vertical(
                Label("Did you get it right?"),
                Button("Yes", variant="success", id="yes_button"),
                Button("No", variant="error", id="no_button"),
                id="correctness_dialog",
            )
        )

    def on_mount(self) -> None:
        self.query_one("#correctness_dialog").styles.border = ("heavy", "white")
        self.query_one("#correctness_dialog").styles.width = "40%"
        self.query_one("#correctness_dialog").styles.height = "auto"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes_button":
            self.dismiss(True)
        else:
            self.dismiss(False)

class StartScreen(Screen):
    """The flashcard learning screen."""

    BINDINGS = [
        Binding("f", "flip_card", "Flip"),
        Binding("n", "next_card", "Next"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flashcards = load_flashcards()
        self.current_card_index = 0
        self.correct_answers = 0
        self.showing_question = True

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="main-content"):
            with Center(id="card-container"):
                yield Static(id="card_text", classes="card")
            with Vertical(id="controls", classes="controls"):
                yield ProgressBar(id="progress", total=len(self.flashcards) if self.flashcards else 1, show_eta=False)
                with Horizontal(id="action-buttons", classes="button-row"):
                    yield Button("Flip", variant="default", id="flip")
                    yield Button("Next", variant="primary", id="next")
                with Horizontal(id="feedback-buttons", classes="button-row"):
                    yield Button("Correct", variant="success", id="correct")
                    yield Button("Incorrect", variant="error", id="incorrect")
        yield Footer()

    def on_mount(self) -> None:
        # App-level styling
        self.screen.styles.background = "#001233"
        self.screen.styles.overflow = "hidden"

        # Layout
        self.query_one("#main-content").styles.height = "100%"
        self.query_one("#card-container").styles.height = "7fr" # 70% of space
        self.query_one("#controls").styles.height = "3fr" # 30% of space
        self.query_one("#controls").styles.padding = (1, 4)
        self.query_one(".button-row").styles.align = ("center", "middle")
        self.query_one(".button-row").styles.height = "auto"
        self.query_one("#progress").styles.margin_bottom = 1

        # Card
        card = self.query_one("#card_text")
        card.styles.height = "90%"
        card.styles.width = "90%"
        card.styles.border = ("round", "#0077b6")
        card.styles.text_align = "center"
        card.styles.content_align = ("center", "middle")
        card.styles.color = "black"
        card.styles.padding = 2

        self.show_card()

    def show_card(self):
        card = self.query_one("#card_text")
        action_buttons = self.query_one("#action-buttons")
        feedback_buttons = self.query_one("#feedback-buttons")

        if not self.flashcards:
            card.update("No flashcards found. Press 'q' to quit and add some.")
            self.query_one("#progress").update(total=1, progress=0)
            action_buttons.styles.display = "none"
            feedback_buttons.styles.display = "none"
            return

        card_data = self.flashcards[self.current_card_index]
        if self.showing_question:
            card.update(f"[b]Question[/b]\n\n{card_data['question']}")
            card.styles.background = "#e0e0ff"  # Light blue
            action_buttons.styles.display = "block"
            feedback_buttons.styles.display = "none"
        else:
            card.update(f"[b]Answer[/b]\n\n{card_data['answer']}")
            card.styles.background = "#d0ffd0"  # Light green
            action_buttons.styles.display = "none"
            feedback_buttons.styles.display = "block"

    def action_flip_card(self) -> None:
        if not self.flashcards:
            return
        self.showing_question = not self.showing_question
        self.show_card()

    def action_next_card(self) -> None:
        if not self.flashcards:
            return
        self.current_card_index = (self.current_card_index + 1) % len(self.flashcards)
        self.showing_question = True
        self.show_card()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "correct":
            self.correct_answers += 1
            self.query_one("#progress").advance()
            self.action_next_card()
        elif event.button.id == "incorrect":
            self.action_next_card()
        elif event.button.id == "flip":
            self.action_flip_card()
        elif event.button.id == "next":
            self.action_next_card()

    def action_quit(self) -> None:
        self.app.exit()

class FlashcardApp(App):
    """A Textual app."""

    SCREENS = {
        "main": MainScreen,
        "add_flashcard": AddFlashcardScreen,
        "edit_flashcard": EditScreen,
        "answer_screen": AnswerScreen,
        "correctness_screen": CorrectnessScreen,
        "start": StartScreen,
    }

    def __init__(self, initial_screen: str = "main", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_screen = initial_screen

    def on_mount(self) -> None:
        self.push_screen(self.initial_screen)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

if __name__ == "__main__":
    app = FlashcardApp()
    app.run()
