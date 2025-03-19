# Focus Timer Module
# This module provides a simple timer application for focus sessions
# It allows users to set a timer in minutes and provides start, pause, and reset functionality
import os
from datetime import datetime
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Input, Static
from textual.containers import VerticalScroll, Container

# Timer Application
# Provides a simple interface for setting one timer at a time
class TimerApp(Container):

    # Initialize the timer application
    # Sets up default values
    def __init__(self):
        super().__init__()
        self.timer = None
        self.remaining_time = 0
        self.running = False

    # Creates the UI layout with all necessary widgets
    def compose(self) -> ComposeResult:
        yield Static("Timer App", classes="title")
        yield Input(placeholder="Enter time in minutes", id="time-input")
        yield Static("00:00", id="timer-display")
        yield Button("Start", id="start")
        yield Button("Pause", id="pause")
        yield Button("Reset", id="reset")

    # Formats the remaining time into MM:SS format
    def format_time(self) -> str:
        minutes, seconds = divmod(self.remaining_time, 60)
        return f"{minutes:02}:{seconds:02}"

    # Updates the timer display with the current remaining time
    def update_display(self):
        self.query_one("#timer-display", Static).update(self.format_time())

    # Handles button press events
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "start":
            self.start_timer()
        elif event.button.id == "pause":
            self.pause_timer()
        elif event.button.id == "reset":
            self.reset_timer()

    # Starts the timer with the specified duration
    # Validates input and shows error if invalid
    def start_timer(self):
        if not self.running:
            input_widget = self.query_one("#time-input", Input)
            try:
                self.remaining_time = int(input_widget.value) * 60
            except ValueError:
                self.notify("Invalid input! Enter a number.", title="Error")
                return
            self.running = True
            self.timer = self.set_interval(1, self.tick)
            self.update_display()

    # Pauses the currently running timer
    def pause_timer(self):
        if self.running and self.timer:
            self.running = False
            self.timer.stop()

    # Resets the timer to its initial state
    def reset_timer(self):
        if self.timer:
            self.timer.stop()
        self.running = False
        self.remaining_time = 0
        self.update_display()

    # Decrements the timer by one second
    # Stops the timer and notifies when time is up
    def tick(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.update_display()
        else:
            self.timer.stop()
            self.running = False
            self.notify("Time's up!", title="Timer Done")

if __name__ == "__main__":
    TimerApp().run()
