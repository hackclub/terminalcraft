import time
import threading
import subprocess
import sys
import os
import pygame
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static, Input, Button
from rich.text import Text

pygame.mixer.init()

# Timer Class for Pomodoro functionality
class Timer:
    def __init__(self, work_duration=25, break_duration=5):
        self.work_duration = work_duration  # Work time in minutes
        self.break_duration = break_duration  # Break time in minutes
        self.running = False
        self.timer_thread = None
        self.time_left = self.work_duration * 60  # Time in seconds

    def update_durations(self, work_duration, break_duration):
        """Update the work and break durations dynamically."""
        self.work_duration = work_duration
        self.break_duration = break_duration

    def start_work(self):
        self.time_left = self.work_duration * 60  # Reset time for work
        self.running = True
        if not self.timer_thread or not self.timer_thread.is_alive():
            self.timer_thread = threading.Thread(target=self.run_timer)
            self.timer_thread.start()

    def start_break(self):
        self.time_left = self.break_duration * 60  # Reset time for break
        self.running = True
        if not self.timer_thread or not self.timer_thread.is_alive():
            self.timer_thread = threading.Thread(target=self.run_timer)
            self.timer_thread.start()

    def stop(self):
        self.running = False
        self.time_left = 0

    def run_timer(self):
        while self.running and self.time_left > 0:
            time.sleep(1)
            self.time_left -= 1
        self.running = False
        self.play_notification_sound()

    def get_time_left(self):
        minutes, seconds = divmod(self.time_left, 60)
        return f"{minutes:02}:{seconds:02}"
    
    def play_notification_sound(self):
        """Play a sound when the timer ends (cross-platform)."""
        try:
            pygame.mixer.music.load("time_done.mp3")  # Path to your MP3 file
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():  # Wait for music to finish playing
                time.sleep(0.1)  # This avoids blocking the main thread
        except Exception as e:
            print(f"Error playing sound: {e}")


# Custom Clock Animation
class ClockStatic(Static):
    def render(self) -> Text:
        """Update time dynamically."""
        return Text(datetime.now().strftime("%H:%M:%S"), style="bold cyan")


# Main App class
class PromodoTimer(App):
    CSS_PATH = "style.tcss"  # External CSS for styling

    def __init__(self):
        super().__init__()
        self.timer = Timer()

    def compose(self) -> ComposeResult:
        """Define the UI layout using the compose() method."""
        yield Container(
            ClockStatic(id="clock"),
            Static("⏳ Pomodoro Timer", classes="title"),
            Static(self.timer.get_time_left(), id="timer_display"),
            Input(placeholder="Work Duration (min)", id="work_input"),
            Input(placeholder="Break Duration (min)", id="break_input"),
            Button("Set Durations", id="set_durations"),
            Button("Start Work", id="start_work"),
            Button("Start Break", id="start_break"),
            Button("Stop Timer", id="stop_timer"),
        )

    async def on_mount(self) -> None:
        """Called when the app starts up."""
        self.set_interval(1, self.update_timer_display)

    async def on_button_pressed(self, event):
        """Handle button press events."""
        button_id = event.button.id

        if button_id == "set_durations":
            await self.update_durations()
        elif button_id == "start_work":
            self.timer.start_work()
        elif button_id == "start_break":
            self.timer.start_break()
        elif button_id == "stop_timer":
            self.timer.stop()

        await self.update_timer_display()

    async def update_durations(self):
        """Update work and break durations from user input."""
        work_input = self.query_one("#work_input", Input).value
        break_input = self.query_one("#break_input", Input).value

        try:
            work_time = int(work_input) if work_input else self.timer.work_duration
            break_time = int(break_input) if break_input else self.timer.break_duration

            if work_time > 0 and break_time > 0:
                self.timer.update_durations(work_time, break_time)
                self.query_one("#timer_display", Static).update(Text("Durations Set ✅", style="bold green"))
            else:
                self.query_one("#timer_display", Static).update(Text("Invalid Time ⛔", style="bold red"))
        except ValueError:
            self.query_one("#timer_display", Static).update(Text("Invalid Input ⛔", style="bold red"))

    async def update_timer_display(self):
        """Update timer every second."""
        timer_display = self.query_one("#timer_display", Static)
        timer_display.update(Text(self.timer.get_time_left(), style="bold yellow"))


if __name__ == "__main__":
    app = PromodoTimer()
    app.run()
