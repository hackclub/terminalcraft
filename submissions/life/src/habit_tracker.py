# Habit Tracker Module
# This module provides a habit tracking system that allows users to create, complete, and delete habits
# Habits are reset daily and stored in a JSON file
import os
import json
from datetime import datetime, date
from textual.widgets import Button, Input, Static, DataTable
from textual.containers import Container

# Define the path to store habits in the /data folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Get terminalCraft directory
DATA_DIR = os.path.join(BASE_DIR, "data")
HABITS_FILE = os.path.join(DATA_DIR, "habits.json")

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Loads habits from the JSON file
# Resets habit completion status if it's a new day
def load_habits():
    if not os.path.exists(HABITS_FILE):
        return {"last_reset": str(date.today()), "habits": []}
    with open(HABITS_FILE, "r") as file:
        data = json.load(file)

    if data["last_reset"] != str(date.today()):
        for habit in data["habits"]:
            habit["completed"] = False
        data["last_reset"] = str(date.today())
        save_habits(data)

    return data

# Saves habits to the JSON file
def save_habits(data):
    with open(HABITS_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Habit Tracker Application Container
class HabitTrackerApp(Container):

    # Initialize the habit tracker application
    def __init__(self):
        super().__init__()
        self.data = load_habits()

    # Creates the UI layout with all necessary widgets
    def compose(self):
        yield Static("Habit Tracker", classes="title")
        yield Input(placeholder="Enter habit name", id="habit-input")
        yield Button("Add Habit", id="add")
        yield Button("Mark as Completed", id="complete")
        yield Button("Delete Habit", id="delete")
        yield DataTable(id="habit-table")

    # Loads habits into the table
    def on_mount(self):
        self.load_habits_into_table(True)

    # Loads habits into the DataTable widget
    def load_habits_into_table(self, first):
        table = self.query_one("#habit-table", DataTable)
        table.clear()
        if first:
            table.add_columns("#", "Habit", "Completed")
        for i, habit in enumerate(self.data["habits"], 1):
            status = "✔" if habit["completed"] else "✘"
            table.add_row(str(i), habit["name"], status)

    # Handles button press events
    def on_button_pressed(self, event: Button.Pressed):
        habit_input = self.query_one("#habit-input", Input)
        table = self.query_one("#habit-table", DataTable)

        # Add new habit
        if event.button.id == "add":
            if habit_input.value.strip():
                self.data["habits"].append({"name": habit_input.value, "completed": False})
                save_habits(self.data)
                habit_input.value = ""
                self.load_habits_into_table(False)

        # Mark selected habit as completed
        elif event.button.id == "complete":
            if table.cursor_row is not None and 0 <= table.cursor_row < len(self.data["habits"]):
                self.data["habits"][table.cursor_row]["completed"] = True
                save_habits(self.data)
                self.load_habits_into_table(False)

        # Delete selected habit
        elif event.button.id == "delete":
            if table.cursor_row is not None and 0 <= table.cursor_row < len(self.data["habits"]):
                self.data["habits"].pop(table.cursor_row)
                save_habits(self.data)
                self.load_habits_into_table(False)
