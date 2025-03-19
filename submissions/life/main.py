# Main Application Module
# This module serves as the entry point for the Life application
# It provides the main menu and navigation between different features
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static
from textual import css

from src.focus_timer import TimerApp
from src.habit_tracker import HabitTrackerApp
from src.task_manager import TaskManagerApp

# Main container for the application menu
class MainContainer(Vertical):
    CSS = """
    Vertical{
        background: $surface;
        color: $text;
        padding: 1;
        height: 100%;
    }

    .title {
        content-align: center middle;
        height: 3;
        text-style: bold;
        color: $accent;
        text-align: center;
        padding: 1;
    }

    Button {
        width: 100%;
        margin: 1;
        height: 3;
    }
    """

    # Creates the main menu layout
    def compose(self) -> ComposeResult:
        yield Static("Welcome to Life! Choose an option", classes="title")
        yield Button("Focus Timer", id="focus_timer")
        yield Button("Habit Tracker", id="habit_tracker")
        yield Button("Task Manager", id="task_manager")
        yield Button("Quit", id="quit")

# Screen for the Focus Timer feature
class TimerScreen(Screen):

    # Initialize the timer screen
    def __init__(self):
        super().__init__()
        self.timer_app = TimerApp()

    # Creates the timer screen layout
    def compose(self) -> ComposeResult:
        yield Header()
        yield self.timer_app
        yield Button("Back", id="back")
        yield Footer()

    # Handles button press events
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "back":
            self.app.pop_screen()

# Screen for the Habit Tracker feature
class HabitTrackerScreen(Screen):

    # Initialize the habit tracker screen
    def __init__(self):
        super().__init__()
        self.habit_tracker_app = HabitTrackerApp()

    # Creates the habit tracker screen layout
    def compose(self) -> ComposeResult:
        yield Header()
        yield self.habit_tracker_app
        yield Button("Back", id="back")
        yield Footer()

    # Handles button press events
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "back":
            self.app.pop_screen()

# Screen for the Task Manager feature
class TaskManagerScreen(Screen):

    # Initialize the task manager screen
    def __init__(self):
        super().__init__()
        self.task_manager_app = TaskManagerApp()

    # Creates the task manager screen layout
    def compose(self) -> ComposeResult:
        yield Header()
        yield self.task_manager_app
        yield Button("Back", id="back")
        yield Footer()

    # Handles button press events
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "back":
            self.app.pop_screen()

# Manages the overall application state and navigation
class Life(App):
    CSS = """
    App {
        background: $surface;
        color: $text;
    }
    """

    # Creates the main application layout
    def compose(self) -> ComposeResult:
        yield Header()
        yield MainContainer()
        yield Footer()

    # Handles button press events for navigation
    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "focus_timer":
                self.push_screen(TimerScreen())
            case "habit_tracker":
                self.push_screen(HabitTrackerScreen())
            case "task_manager":
                self.push_screen(TaskManagerScreen())
            case "quit":
                self.exit()

if __name__ == "__main__":
    app = Life()
    app.run()
