# demo_web_deployment.py

import ast
import os
import random

from textual.app import App, ComposeResult
from textual.containers import Container, VerticalGroup
from textual.widgets import Header, Footer, Static, Input, Button

class Flashcard(VerticalGroup):
    def compose(self) -> ComposeResult:
        """Create child widgets of a flashcard."""
        yield Static("", id="flashcard")
        yield Input(placeholder="Enter parameters (comma separated)", id="answer_input")
        yield Container(
            Button("Submit", id="submit_button"),
            Button("Next", id="next_button"),
            id="button_container"
        )
        yield Static("", id="feedback")

class FlashcardApp(App):
    CSS = """
    Screen {
        align: center middle;
        padding: 2;
    }
    #flashcard {
        height: auto;
        border: round cornflowerblue;
        padding: 1 2;
        margin-bottom: 1;
    }
    #feedback {
        height: auto;
        margin-top: 1;
    }
    #button_container {
        layout: horizontal;
    }
    Button {
        background: darkblue;
        color: white;
        border: round white;
        padding: 1 2;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.flashcards = self.scan_directory()
        self.current_card = None

    def scan_directory(self, directory="."):
        """Recursively scan the directory for Python files and extract function definitions with parameters."""
        all_functions = []
        current_file = os.path.basename(__file__)
        for root, dirs, files in os.walk(directory):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in {"venv", "node_modules", ".git"}]
            for file in files:
                if file.endswith(".py") and file != current_file:
                    file_path = os.path.join(root, file)
                    all_functions.extend(self.extract_functions(file_path))
        return all_functions

    def extract_functions(self, file_path):
        """Parse a Python file and extract function definitions with their parameters (excluding functions with no parameters)."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source, filename=file_path)
        except Exception:
            return []
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                arg_names = [arg.arg for arg in node.args.args]
                if not arg_names:
                    continue  # Skip functions with no parameters
                functions.append({
                    "name": node.name,
                    "args": arg_names,
                    "file": file_path
                })
        return functions

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(Flashcard())
        yield Footer()

    def on_mount(self):
        self.load_new_flashcard()

    def load_new_flashcard(self):
        """Load a new flashcard and clear the input and feedback."""
        if not self.flashcards:
            flashcard_text = "No flashcards available in this directory."
            self.query_one("#flashcard", Static).update(flashcard_text)
            return
        self.current_card = random.choice(self.flashcards)
        flashcard_text = (
            f"[b]Function:[/b] '{self.current_card['name']}'\n"
            f"[b]Defined in:[/b] {self.current_card['file']}"
        )
        self.query_one("#flashcard", Static).update(flashcard_text)
        self.query_one("#feedback", Static).update("")
        self.query_one("#answer_input", Input).value = ""

    async def handle_submit(self):
        answer_widget = self.query_one("#answer_input", Input)
        user_input = answer_widget.value.strip()
        user_args = [arg.strip() for arg in user_input.split(",") if arg.strip()]
        actual_args = self.current_card['args']
        if set(user_args) == set(actual_args):
            feedback = "[green]Correct![/green]"
        else:
            feedback = f"[red]Incorrect.[/red] Actual parameters: {', '.join(actual_args)}"
        self.query_one("#feedback", Static).update(feedback)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit_button":
            await self.handle_submit()
        elif event.button.id == "next_button":
            self.load_new_flashcard()

if __name__ == "__main__":
    FlashcardApp().run()
