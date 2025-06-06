import json
import os
from datetime import datetime

MOOD_FILE = "data/moods.json"

def load_moods():
    if not os.path.exists(MOOD_FILE):
        return []
    with open(MOOD_FILE, "r") as file:
        return json.load(file)

def save_moods(moods):
    with open(MOOD_FILE, "w") as file:
        json.dump(moods, file, indent=4)

def log_mood(moods):
    date = datetime.today().strftime("%Y-%m-%d")
    mood = input("How are you feeling today? (happy, sad, anxious, etc): ")
    reason = input("Why do you feel this way? ")
    moods.append({"date": date, "mood": mood, "reason": reason})
    print("Mood saved for today! 💾")

def view_moods(moods):
    if not moods:
        print("No moods logged yet.")
        return
    print("\n📅 Mood Logs:")
    for entry in moods[-10:]:  # Show the last 10 entries
        print(f"{entry['date']}: {entry['mood'].title()} - {entry['reason']}")

def mood_logger():
    moods = load_moods()
    while True:
        print("\n== Mood Logger ==")
        print("1. Log Today's Mood")
        print("2. View Last 10 Mood Entries")
        print("3. Back to Main Menu")
        choice = input("Choose an option: ")

        if choice == "1":
            log_mood(moods)
            save_moods(moods)
        elif choice == "2":
            view_moods(moods)
        elif choice == "3":
            break
        else:
            print("Invalid choice.")
