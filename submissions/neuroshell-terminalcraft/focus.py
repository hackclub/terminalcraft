import time
import json
import os
from datetime import datetime

FOCUS_FILE = "data/focus_sessions.json"

def load_sessions():
    if not os.path.exists(FOCUS_FILE):
        return []
    with open(FOCUS_FILE, "r") as file:
        return json.load(file)

def save_sessions(sessions):
    with open(FOCUS_FILE, "w") as file:
        json.dump(sessions, file, indent=4)

def countdown(duration):
    for remaining in range(duration, 0, -1):
        mins, secs = divmod(remaining, 60)
        timer_display = f"{mins:02}:{secs:02}"
        print(f"\r⏳ Time Left: {timer_display}", end="")
        time.sleep(1)
    print("\n⏰ Time's up!")

def start_session(sessions, session_type, duration_minutes):
    print(f"\n🧠 Starting {session_type} session for {duration_minutes} minutes...")
    countdown(duration_minutes * 60)
    sessions.append({
        "date": datetime.today().strftime("%Y-%m-%d"),
        "type": session_type,
        "duration_minutes": duration_minutes
    })
    save_sessions(sessions)
    print(f"✅ {session_type} session completed and logged!")

def view_sessions(sessions):
    if not sessions:
        print("No sessions logged yet.")
        return
    print("\n📜 Focus Sessions History:")
    for entry in sessions[-10:]:
        print(f"{entry['date']} - {entry['type'].title()} for {entry['duration_minutes']} minutes")

def focus_timer():
    sessions = load_sessions()
    while True:
        print("\n== Focus Timer ==")
        print("1. Start Work Session (25 min)")
        print("2. Start Short Break (5 min)")
        print("3. Start Long Break (15 min)")
        print("4. View Session History")
        print("5. Back to Main Menu")
        choice = input("Choose an option: ")

        if choice == "1":
            start_session(sessions, "work", 25)
        elif choice == "2":
            start_session(sessions, "short break", 5)
        elif choice == "3":
            start_session(sessions, "long break", 15)
        elif choice == "4":
            view_sessions(sessions)
        elif choice == "5":
            break
        else:
            print("Invalid choice.")
