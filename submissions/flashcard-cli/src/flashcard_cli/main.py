import typer
from rich.console import Console
from flashcard_cli.data import load_flashcards, save_flashcard
from flashcard_cli.tui import FlashcardApp

app = typer.Typer(no_args_is_help=True)
console = Console()

@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context):
    """
    Display the manage screen if no subcommand is passed.
    """
    if ctx.invoked_subcommand is None:
        manage()

@app.command()
def add():
    """
    Adds a new flashcard using a Textual UI.
    """
    app_instance = FlashcardApp(initial_screen="add_flashcard")
    app_instance.run()

@app.command()
def start():
    """
    Starts the flashcard learning session.
    """
    app_instance = FlashcardApp(initial_screen="start")
    app_instance.run()

# flashcard mannage commands
@app.command()
def manage():
    """
    Flash Cards Edit And Delete Commands with terminal UI
        - Show Screen Listed with id all card as table
        - can use updown arow ans switch eac and when select item (card)
        - selected card and press 'e' can edit and press 'del' can delete falshcard
        - screen had header contet centr and footer
        - header include appname date like basic data
        - center add selct  listed cards
        - footer include key guide
    """
    app_instance = FlashcardApp(initial_screen="main")
    app_instance.run()
   

def main():
    app()

if __name__ == "__main__":
    main()
