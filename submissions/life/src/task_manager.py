# Task Manager Module
# This module provides a task management system with calendar view and task tracking functionality
# It uses a JSON file as a simple database to store tasks

import json
import os
from datetime import datetime, date
from textual.widgets import DataTable, Button, Input, Static, Label
from textual.containers import Container
from rich.table import Table
import calendar

# my version of a database because I dont want to learn a database
# Define the path to store habits in the /data folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Get terminalCraft directory
DATA_DIR = os.path.join(BASE_DIR, "data")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Validates if a given date string is in the correct format (YYYY-MM-DD)
def validate_date(date_str):
    if not date_str or date_str == "N/A":
        return True
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# loading all of the tasks from the "database" because I still refuse to learn a database
def load_tasks():
    # if the file exists open it else create it
    if not os.path.exists(TASKS_FILE):
        return []
    # reading the file
    with open(TASKS_FILE, "r") as file:
        return json.load(file)

# opening the file to write in it so that you can finish or add new tasks
def save_tasks(tasks):
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)

# creating a calendar view
def generate_calendar_view(year, month, tasks):
    first_weekday, days_in_month = calendar.monthrange(year, month)
    prev_month_days = calendar.monthrange(year, month - 1 if month > 1 else 12)[1]
    task_dict = {}
    for task in tasks:
        if task["due"] != "N/A":
            try:
                due_date = datetime.strptime(task["due"], "%Y-%m-%d")
                if due_date.year == year and due_date.month == month:
                    task_dict.setdefault(due_date.day, []).append(task["completed"])
            except ValueError:
                continue

    # Create calendar table
    table = Table(title=f"{calendar.month_name[month]} {year}")
    table.add_column("Mon")
    table.add_column("Tue")
    table.add_column("Wed")
    table.add_column("Thu")
    table.add_column("Fri")
    table.add_column("Sat")
    table.add_column("Sun")
    weeks = []
    week = []

    # Fill in previous month's days
    for i in range(first_weekday):
        week.append(f"[dim]{prev_month_days - first_weekday + i + 1}")

    # Fill in current month's days
    for day in range(1, days_in_month + 1):
        if day in task_dict:
            if all(task_dict[day]):
                week.append(f"[bold green]{day}")
            else:
                week.append(f"[bold red]{day}*")
        else:
            week.append(str(day))

        if len(week) == 7:
            weeks.append(week)
            week = []

    # Fill in next month's days
    next_month_day = 1
    while len(week) < 7:
        week.append(f"[dim]{next_month_day}")
        next_month_day += 1
    weeks.append(week)

    # Add all weeks to the table
    for week in weeks:
        table.add_row(*week)

    return table

# Main Task Manager Application Container
class TaskManagerApp(Container):
    def __init__(self):
        super().__init__()
        self.current_year = datetime.today().year
        self.current_month = datetime.today().month

    # Creates the UI layout with all necessary widgets
    def compose(self):
        yield Static("Task Manager", classes="title")
        yield Input(placeholder="Enter task...")
        yield Input(placeholder="Enter due date (YYYY-MM-DD)...", id="due_input")
        yield Button("Add Task", id="add_button")
        yield Button("Complete Task", id="complete_button")
        yield Button("Delete Task", id="delete_button")
        yield Button("Previous Month", id="prev_month")
        yield Button("Next Month", id="next_month")
        yield DataTable(id="task_table")
        yield Label("", id="calendar_view")

    # Initializes the application when mounted
    def on_mount(self):
        first = True
        self.update_calendar()
        self.load_tasks_into_table(first)
        self.update_calendar()

    # Loads tasks into the DataTable widget
    def load_tasks_into_table(self, first):
        self.update_calendar()
        table = self.query_one("#task_table", DataTable)
        table.clear()
        # if it is the first time that it is running then it prints the column headers, if not then it skipps this.
        if first:
            # the column headers for the tasks. There are issues with this i think but i really could't be bothered to fix them as it does not crash i think. I want to make this the longest comment I have ever written and I think I have done it
            table.add_columns("#", "Task", "Status", "Due Date")
        tasks = load_tasks()
        # loop to get the stuff and add them to the table from the "database"
        for i, task in enumerate(tasks, 1):
            status = "✔" if task["completed"] else "✘"
            due = task.get("due", "N/A")
            table.add_row(str(i), task["task"], status, due)
        self.update_calendar()

    # Updates the calendar view with current tasks
    def update_calendar(self):
        tasks = load_tasks()
        calendar_table = generate_calendar_view(self.current_year, self.current_month, tasks)
        calendar_label = self.query_one("#calendar_view", Label)
        calendar_label.update(calendar_table)

    # Handles button press events
    def on_button_pressed(self, event: Button.Pressed):
        task_input = self.query_one(Input)
        due_input = self.query_one("#due_input", Input)
        table = self.query_one("#task_table", DataTable)
        tasks = load_tasks()

        if event.button.id == "add_button":
            if task_input.value.strip():
                due_date = due_input.value.strip()
                if not validate_date(due_date):
                    self.notify("Invalid date format! Use YYYY-MM-DD", title="Error")
                    return

                tasks.append({
                    "task": task_input.value,
                    "completed": False,
                    "added": str(datetime.now()),
                    "due": due_date or "N/A"
                })
                task_input.value = ""
                due_input.value = ""
                # fixing the issue with the column headers showing up multiple times, this isnt the first and so it is false
                first = False
                save_tasks(tasks)
                self.load_tasks_into_table(first)
                self.update_calendar()

        elif event.button.id == "complete_button":
            if table.cursor_row is not None and 0 <= table.cursor_row < len(tasks):
                tasks[table.cursor_row]["completed"] = True
                first = False
                save_tasks(tasks)
                self.load_tasks_into_table(first)
                self.update_calendar()

        elif event.button.id == "delete_button":
            if table.cursor_row is not None and 0 <= table.cursor_row < len(tasks):
                tasks.pop(table.cursor_row)
                first = False
                save_tasks(tasks)
                self.load_tasks_into_table(first)
                self.update_calendar()

        elif event.button.id == "prev_month":
            if self.current_month == 1:
                self.current_month = 12
                self.current_year -= 1
            else:
                self.current_month -=1
            self.update_calendar()

        elif event.button.id == "next_month":
            if self.current_month == 12:
                self.current_month = 2
                self.current_year += 1
            else:
                self.current_month += 1
            self.update_calendar()
