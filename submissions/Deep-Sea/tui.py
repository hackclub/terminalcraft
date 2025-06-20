import time
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, RichLog, Static, Input
from main import Game
class GameTUI(App):
    """A Textual user interface for the game."""
    CSS_PATH = "tui.css"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Vertical():
            with Horizontal(id="main-container"):
                yield RichLog(id="log", markup=True)
                yield Static(id="status", markup=True)
            yield Input(placeholder="Enter command...", id="command-input")
        yield Footer()
    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.game = Game()
        self.minigame_start_time = 0
        self.log_widget = self.query_one(RichLog)
        self.status_widget = self.query_one(Static)
        self.input_widget = self.query_one(Input)
        initial_messages = self.game.start_game()
        for msg in initial_messages:
            self.log_widget.write(msg)
        self.update_status_widget()
        self.game_tick_timer = self.set_interval(1, self.game_tick)
        self.input_widget.focus()
    def game_tick(self) -> None:
        """Update the game state periodically."""
        if not self.game.is_running:
            self.game_tick_timer.pause()
            return
        messages = self.game.update()
        for msg in messages:
            self.log_widget.write(msg)
        self.update_status_widget()
    def update_status_widget(self) -> None:
        """Update the status widget with the latest game state."""
        report = self.game.get_status_report()
        self.status_widget.update("\n".join(report))
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user command input."""
        command = event.value
        self.input_widget.clear()
        if not self.game.is_running:
            self.log_widget.write("[bold red]Game over. No further commands.[/bold red]")
            return
        if self.game.minigame_active:
            time_taken = time.time() - self.minigame_start_time
            messages = self.game.process_minigame_input(command, time_taken)
        else:
            messages = self.game.process_command(command)
        for msg in messages:
            self.log_widget.write(msg)
        self.update_status_widget()
        if self.game.minigame_active and self.minigame_start_time == 0:
            self.minigame_start_time = time.time()
        elif not self.game.minigame_active:
            self.minigame_start_time = 0
        if not self.game.is_running:
            self.log_widget.write("[bold red]GAME OVER[/bold red]")
            self.input_widget.disabled = True
    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark
if __name__ == "__main__":
    app = GameTUI()
    app.run()