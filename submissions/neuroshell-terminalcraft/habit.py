import json
import os
from datetime import datetime

HABIT_FILE = "data/habits.json"

def load_habits():
    if not os.path.exists(HABIT_FILE):
        return {}
    with open(HABIT_FILE, "r") as file:
        return json.load(file)

def save_habits(habits):
    with open(HABIT_FILE, "w") as file:
        json.dump(habits, file, indent=4)

def show_habits(habits):
    if not habits:
        print("No habits found. Add one!")
        return
    print("\nYour Habits:")
    for i, (habit, info) in enumerate(habits.items(), start=1):
        print(f"{i}. {habit} - Last done: {info['last_done']} | Streak: {info['streak']}")

def add_habit(habits):
    name = input("Enter the name of the new habit: ")
    if name in habits:
        print("Habit already exists.")
        return
    habits[name] = {"streak": 0, "last_done": "Never"}
    print("Habit added!")

def mark_done(habits):
    show_habits(habits)
    choice = input("Enter the name of the habit you completed: ")
    if choice in habits:
        today = datetime.today().strftime("%Y-%m-%d")
        if habits[choice]["last_done"] == today:
            print("You've already marked this habit today!")
        else:
            habits[choice]["streak"] += 1
            habits[choice]["last_done"] = today
            print("Nice work! ✅")
    else:
        print("Habit not found.")

def habit_tracker():
    habits = load_habits()
    while True:
        print("\n== Habit Tracker ==")
        print("1. View Habits")
        print("2. Add Habit")
        print("3. Mark Habit as Done")
        print("4. Back to Main Menu")
        choice = input("Choose an option: ")

        if choice == "1":
            show_habits(habits)
        elif choice == "2":
            add_habit(habits)
            save_habits(habits)
        elif choice == "3":
            mark_done(habits)
            save_habits(habits)
        elif choice == "4":
            break
        else:
            print("Invalid choice.")
