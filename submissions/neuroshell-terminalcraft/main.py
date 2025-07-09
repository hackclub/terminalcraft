import time
import os
import habit
import mood
import focus

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def main_menu():
    while True:
        clear()
        print("🧠 Welcome to NeuroShell")
        print("========================")
        print("1. Habit Tracker")
        print("2. Mood Logger")
        print("3. Focus Timer")
        print("4. Exit")
        choice = input("Select an option (1-4): ")

        if choice == "1":
            habit.habit_tracker()
        elif choice == "2":
            mood.mood_logger()
        elif choice == "3":
            focus.focus_timer()
        elif choice == "4":
            print("Goodbye! 🧠")
            break
        else:
            print("Invalid choice.")
            time.sleep(1)

if __name__ == "__main__":
    main_menu()
