import time
import os
from datetime import datetime
import threading

TASKS_FILE = "tasks.txt"
LOG_FILE = "log.txt"
DEBUG = False  # Set to False for full Pomodoro duration

stop_flag = threading.Event()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def save_tasks(tasks):
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        for task in tasks:
            f.write(f"{task}\n")

def log_session(task_name, duration):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now()} - {task_name} - {duration} min\n")

def show_stats():
    if not os.path.exists(LOG_FILE):
        print("No stats available.")
        time.sleep(2)
        return

    sessions = {}
    total_time = 0
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if '-' not in line:
                continue
            parts = line.strip().split(' - ')
            if len(parts) != 3:
                continue
            _, task, minutes_str = parts
            try:
                minutes = int(minutes_str.strip().split()[0])
                total_time += minutes
                sessions[task] = sessions.get(task, 0) + minutes
            except ValueError:
                continue

    print("\n== Pomodoro Stats ==")
    print(f"Total focus time: {total_time} minutes")
    print("\nTime spent per task:")
    for task, minutes in sessions.items():
        print(f"- {task}: {minutes} minutes")
    safe_input("\nPress Enter to continue...")

def pomodoro(task):
    global stop_flag
    stop_flag.clear()
    print(f"Starting Pomodoro for: {task}")
    duration_minutes = 25 if not DEBUG else 0.2
    duration_seconds = int(duration_minutes * 60)

    def input_listener():
        safe_input("\nPress Enter at any time to stop the timer early...\n")
        stop_flag.set()

    listener_thread = threading.Thread(target=input_listener)
    listener_thread.daemon = True
    listener_thread.start()

    for elapsed in range(duration_seconds):
        if stop_flag.is_set():
            print("\nPomodoro stopped early.")
            log_session(task, int(elapsed / 60))
            return
        remaining = duration_seconds - elapsed
        mins, secs = divmod(remaining, 60)
        percent = int((elapsed / duration_seconds) * 100)
        bar = '#' * (percent // 10) + '-' * (10 - percent // 10)
        print(f"Time remaining: {mins:02d}:{secs:02d}  Progress: [{bar}] {percent}%", end='\r')
        time.sleep(1)

    print("\nPomodoro complete! Take a 5 minute break.")
    log_session(task, int(duration_minutes))

def safe_input(prompt):
    try:
        return input(prompt)
    except OSError:
        print("Input is not available in this environment.")
        return None

def main_menu():
    while True:
        clear()
        print("== TermTime ==")
        tasks = load_tasks()
        for idx, task in enumerate(tasks):
            print(f"{idx + 1}. {task}")

        print("\n[a] Add Task  [d] Delete Task  [p] Pomodoro  [s] Stats  [q] Quit")
        choice = safe_input("> ")
        if choice is None:
            break
        choice = choice.strip().lower()

        if choice == 'a':
            task = safe_input("Enter new task: ")
            if task:
                task = task.strip()
                if task:
                    tasks.append(task)
                    save_tasks(tasks)
        elif choice == 'd':
            index_input = safe_input("Task number to delete: ")
            if index_input is not None:
                try:
                    index = int(index_input.strip()) - 1
                    if 0 <= index < len(tasks):
                        del tasks[index]
                        save_tasks(tasks)
                except ValueError:
                    print("Invalid input.")
                    time.sleep(2)
        elif choice == 'p':
            index_input = safe_input("Task number to start Pomodoro: ")
            if index_input is not None:
                try:
                    index = int(index_input.strip()) - 1
                    if 0 <= index < len(tasks):
                        pomodoro(tasks[index])
                        safe_input("Press Enter to continue...")
                except ValueError:
                    print("Invalid input.")
                    time.sleep(2)
        elif choice == 's':
            show_stats()
        elif choice == 'q':
            break
        else:
            safe_input("Invalid choice. Press Enter to continue...")

if __name__ == "__main__":
    main_menu()
