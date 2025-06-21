import time
import random
import json
import os
import csv
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, field
import uuid
import sys
import logging
from queue import Queue
import shutil
import os

# Configure logging
logging.basicConfig(filename='task_manager.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    priority: str = "low"
    due_date: str = datetime.now().isoformat()
    category: str = "general"
    completed: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    progress: int = 0  # 0-100%
    effort_hours: float = 1.0
    dependencies: List[str] = field(default_factory=list)
    recurring: str = "none"  # 'daily', 'weekly', 'none'

@dataclass
class User:
    username: str
    password_hash: str  # Use proper hashing in production
    tasks: List[Task] = field(default_factory=list)

class TaskManager:
    def __init__(self):
        self.users = self._load_users()
        self.current_user = self._authenticate()
        self.undo_stack = []
        self.notification_queue = Queue()
        self.categories = set(t.category for t in self.current_user.tasks)
        self.version = "2.0"

    def _load_users(self) -> Dict[str, User]:
        try:
            if os.path.exists("users.json"):
                with open("users.json", "r") as f:
                    data = json.load(f)
                    return {u["username"]: User(u["username"], u["password_hash"], [Task(**task) for task in u.get("tasks", [])]) for u in data}
            else:
                return {"default": User("default", "default123")}
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding users.json: {e}")
            return {"default": User("default", "default123")}
        except Exception as e:
            logging.error(f"Error loading users: {e}")
            return {"default": User("default", "default123")}

    def _save_users(self):
        try:
            with open("users.json", "w") as f:
                json.dump([{"username": u.username, "password_hash": u.password_hash, "tasks": [vars(t) for t in u.tasks]} for u in self.users.values()], f, indent=2)
            shutil.copy("users.json", f"backup_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        except Exception as e:
            logging.error(f"Error saving users: {e}")

    def _load_tasks(self) -> List[Task]:
        return self.current_user.tasks

    def _save_tasks(self):
        self._save_users()
        self._backup_tasks()

    def _backup_tasks(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"backup_tasks_{timestamp}.json", "w") as f:
            json.dump([vars(t) for t in self.current_user.tasks], f, indent=2)

    def _authenticate(self) -> User:
        username = input(f"{YELLOW}Enter username: {RESET}")
        password = input(f"{YELLOW}Enter password: {RESET}")
        user = self.users.get(username)
        if user and user.password_hash == password:
            return user
        print(f"{RED}Invalid credentials. Using default user.{RESET}")
        return self.users.get("default", User("default", "default123"))

    def display_tasks(self, page: int = 1, page_size: int = 5):
        os.system('cls' if os.name == 'nt' else 'clear')
        tasks = self._load_tasks()
        if not tasks:
            print(f"{YELLOW}No tasks available.{RESET}")
            return
        total_pages = (len(tasks) + page_size - 1) // page_size
        start = (page - 1) * page_size
        end = start + page_size
        paginated_tasks = tasks[start:end]
        total_tasks = len(tasks)

        print(f"{BLUE}┌{'─' * 80}┐{RESET}")
        print(f"{BLUE}│ Total Tasks: {total_tasks:<73}│{RESET}")
        for task in paginated_tasks:
            status = f"{GREEN}✓{RESET}" if task.completed else f"{RED}✗{RESET}"
            progress_bar = f"{CYAN}[{'█' * (task.progress // 5)}{' ' * (20 - task.progress // 5)}] {task.progress}%{RESET}"
            print(f"{BLUE}│ [{status}] {task.title[:25]:<25} | {task.priority[:10]:<10} | {task.due_date[:10]:<10} | {progress_bar:<22} | ID: {task.id} │{RESET}")
        print(f"{BLUE}└{'─' * 80}┘{RESET}")
        print(f"{YELLOW}Page {page}/{total_pages} (p=prev, n=next, d=details, q=quit){RESET}")

    def add_task(self):
        print(f"{GREEN}Selected: Add Task{RESET}")
        try:
            task_data = {
                "title": input(f"{YELLOW}Enter task title: {RESET}").strip() or "Untitled",
                "description": input(f"{YELLOW}Enter description: {RESET}").strip(),
                "priority": input(f"{YELLOW}Enter priority (low/medium/high): {RESET}").lower() or "low",
                "due_date": input(f"{YELLOW}Enter due date (YYYY-MM-DD): {RESET}") or datetime.now().isoformat(),
                "category": input(f"{YELLOW}Enter category: {RESET}").strip() or "general",
                "progress": int(input(f"{YELLOW}Enter progress (0-100): {RESET}") or 0),
                "effort_hours": float(input(f"{YELLOW}Enter effort hours: {RESET}") or 1.0),
                "dependencies": input(f"{YELLOW}Enter dependent task IDs (comma-separated): {RESET}").split(",") if input(f"{YELLOW}Add dependencies? (y/n): {RESET}").lower() == "y" else [],
                "recurring": input(f"{YELLOW}Recur (none/daily/weekly): {RESET}").lower() or "none"
            }
            if not (0 <= task_data["progress"] <= 100 and task_data["priority"] in ["low", "medium", "high"] and task_data["recurring"] in ["none", "daily", "weekly"]):
                raise ValueError("Invalid input: Check progress, priority, or recurrence.")
            task = Task(**task_data)
            self.current_user.tasks.append(task)
            self._save_tasks()
            print(f"{GREEN}Task created successfully!{RESET}")
        except ValueError as e:
            print(f"{RED}Error: {e}{RESET}")
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        os.system('cls' if os.name == 'nt' else 'clear')

    def edit_task(self):
        print(f"{GREEN}Selected: Edit Task{RESET}")
        self.display_tasks()
        task_id = input(f"{YELLOW}Enter task ID to edit: {RESET}")
        task = next((t for t in self.current_user.tasks if t.id == task_id), None)
        if task:
            try:
                task.title = input(f"{YELLOW}Enter new title ({task.title}): {RESET}") or task.title
                task.description = input(f"{YELLOW}Enter new description ({task.description}): {RESET}") or task.description
                task.priority = input(f"{YELLOW}Enter new priority ({task.priority}): {RESET}") or task.priority
                task.due_date = input(f"{YELLOW}Enter new due date ({task.due_date}): {RESET}") or task.due_date
                task.category = input(f"{YELLOW}Enter new category ({task.category}): {RESET}") or task.category
                task.progress = int(input(f"{YELLOW}Enter new progress ({task.progress}): {RESET}") or task.progress)
                task.effort_hours = float(input(f"{YELLOW}Enter new effort hours ({task.effort_hours}): {RESET}") or task.effort_hours)
                if input(f"{YELLOW}Update dependencies? (y/n): {RESET}").lower() == "y":
                    task.dependencies = input(f"{YELLOW}Enter new dependent task IDs: {RESET}").split(",")
                task.recurring = input(f"{YELLOW}Enter new recurrence ({task.recurring}): {RESET}") or task.recurring
                self._save_tasks()
                print(f"{GREEN}Task updated successfully!{RESET}")
            except ValueError as e:
                print(f"{RED}Error: Invalid input. {e}{RESET}")
        else:
            print(f"{RED}Task not found.{RESET}")
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        os.system('cls' if os.name == 'nt' else 'clear')

    def delete_task(self):
        print(f"{GREEN}Selected: Delete Task{RESET}")
        self.display_tasks()
        task_id = input(f"{YELLOW}Enter task ID to delete: {RESET}")
        task_to_delete = next((t for t in self.current_user.tasks if t.id == task_id), None)
        if task_to_delete:
            self.undo_stack.append(task_to_delete)
            self.current_user.tasks[:] = [t for t in self.current_user.tasks if t.id != task_id]
            self._save_tasks()
            print(f"{GREEN}Task deleted successfully! Undo available.{RESET}")
        else:
            print(f"{RED}Task not found.{RESET}")
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        os.system('cls' if os.name == 'nt' else 'clear')

    def undo_delete(self):
        if self.undo_stack:
            task = self.undo_stack.pop()
            self.current_user.tasks.append(task)
            self._save_tasks()
            print(f"{GREEN}Last deletion undone!{RESET}")
        else:
            print(f"{YELLOW}No actions to undo.{RESET}")
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        os.system('cls' if os.name == 'nt' else 'clear')

    def toggle_complete(self):
        print(f"{GREEN}Selected: Toggle Completion{RESET}")
        self.display_tasks()
        task_id = input(f"{YELLOW}Enter task ID to toggle: {RESET}")
        task = next((t for t in self.current_user.tasks if t.id == task_id), None)
        if task:
            task.completed = not task.completed
            self._save_tasks()
            print(f"{GREEN}Task completion toggled!{RESET}")
        else:
            print(f"{RED}Task not found.{RESET}")
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        os.system('cls' if os.name == 'nt' else 'clear')

    def filter_tasks(self):
        print(f"{GREEN}Selected: Filter Tasks{RESET}")
        category = input(f"{YELLOW}Enter category: {RESET}")
        filtered = [t for t in self.current_user.tasks if category.lower() in t.category.lower()]
        self.display_tasks(page=1, tasks=filtered)
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        os.system('cls' if os.name == 'nt' else 'clear')

    def sort_tasks(self):
        print(f"{GREEN}Selected: Sort Tasks{RESET}")
        sort_by = input(f"{YELLOW}Sort by (priority/due_date/created_at): {RESET}").lower()
        if sort_by == "priority":
            self.current_user.tasks.sort(key=lambda t: {"high": 0, "medium": 1, "low": 2}.get(t.priority.lower(), 3))
        elif sort_by == "due_date":
            self.current_user.tasks.sort(key=lambda t: datetime.fromisoformat(t.due_date))
        else:
            self.current_user.tasks.sort(key=lambda t: t.created_at)
        self._save_tasks()
        self.display_tasks()
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        os.system('cls' if os.name == 'nt' else 'clear')

    def search_tasks(self):
        print(f"{GREEN}Selected: Search Tasks{RESET}")
        keyword = input(f"{YELLOW}Enter keyword: {RESET}")
        start = input(f"{YELLOW}Start date (YYYY-MM-DD, blank for none): {RESET}")
        end = input(f"{YELLOW}End date (YYYY-MM-DD, blank for none): {RESET}")
        results = [t for t in self.current_user.tasks if keyword.lower() in t.title.lower() or keyword.lower() in t.description.lower() and
                   (not start or datetime.fromisoformat(t.due_date) >= datetime.fromisoformat(start)) and
                   (not end or datetime.fromisoformat(t.due_date) <= datetime.fromisoformat(end))]
        self.display_tasks(page=1, tasks=results)
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        os.system('cls' if os.name == 'nt' else 'clear')

    def export_tasks(self):
        print(f"{GREEN}Selected: Export Tasks{RESET}")
        fmt = input(f"{YELLOW}Format (json/csv): {RESET}").lower()
        filename = input(f"{YELLOW}Enter filename: {RESET}") or f"tasks_{datetime.now().strftime('%Y%m%d')}"
        tasks = [vars(t) for t in self.current_user.tasks]
        if fmt == "csv":
            with open(f"{filename}.csv", "w", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=tasks[0].keys())
                writer.writeheader()
                writer.writerows(tasks)
        else:
            with open(f"{filename}.json", "w") as f:
                json.dump(tasks, f, indent=2)
        print(f"{GREEN}Exported to {filename}.{fmt}{RESET}")
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        os.system('cls' if os.name == 'nt' else 'clear')

    def import_tasks(self):
        print(f"{GREEN}Selected: Import Tasks{RESET}")
        filename = input(f"{YELLOW}Enter filename (.json/.csv): {RESET}")
        if filename.endswith(".csv"):
            with open(filename, "r") as f:
                reader = csv.DictReader(f)
                self.current_user.tasks.extend([Task(**{k: v for k, v in row.items() if k in Task.__dataclass_fields__}) for row in reader])
        elif filename.endswith(".json"):
            with open(filename, "r") as f:
                self.current_user.tasks.extend([Task(**data) for data in json.load(f)])
        self._save_tasks()
        print(f"{GREEN}Imported from {filename}{RESET}")
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_dashboard(self):
        print(f"{GREEN}Selected: Show Dashboard{RESET}")
        tasks = self._load_tasks()
        total = len(tasks)
        completed = sum(1 for t in tasks if t.completed)
        overdue = sum(1 for t in tasks if not t.completed and datetime.fromisoformat(t.due_date) < datetime.now())
        high_priority_overdue = sum(1 for t in tasks if t.priority == "high" and not t.completed and datetime.fromisoformat(t.due_date) < datetime.now())
        print(f"{CYAN}Total Tasks: {total}{RESET}")
        print(f"{CYAN}Completed: {completed} ({completed/total*100:.1f}%){RESET}")
        print(f"{CYAN}Overdue: {overdue} (High Priority: {high_priority_overdue}){RESET}")
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        os.system('cls' if os.name == 'nt' else 'clear')

    def manage_categories(self):
        print(f"{GREEN}Selected: Manage Categories{RESET}")
        action = input(f"{YELLOW}Add/remove category? (a/r): {RESET}")
        if action == "a":
            new_cat = input(f"{YELLOW}Enter new category: {RESET}")
            self.categories.add(new_cat)
            self._save_tasks()
            print(f"{GREEN}Category {new_cat} added.{RESET}")
        elif action == "r":
            cat = input(f"{YELLOW}Enter category to remove: {RESET}")
            if cat in self.categories:
                self.categories.remove(cat)
                self._save_tasks()
                print(f"{GREEN}Category {cat} removed.{RESET}")
            else:
                print(f"{RED}Category not found.{RESET}")
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        os.system('cls' if os.name == 'nt' else 'clear')

    def generate_wave_pattern(self, width, height, frame):
        pattern = []
        colors = [CYAN, MAGENTA, BLUE]
        for y in range(height):
            row = ""
            for x in range(width):
                offset = (x + frame) % width
                wave = int(5 + 4 * random.uniform(0.8, 1.2) * (1 + abs((offset - width // 2) / (width // 4))))
                char = f"{random.choice(colors)}#{RESET}" if y < wave < y + 1 else " "
                row += char
            pattern.append(row)
        return pattern

    def idle_animation(self, last_input_time, queue):
        width, height = os.get_terminal_size()
        frame = 0
        while queue.empty() and time.time() - last_input_time < 15:
            if sys.stdin.read(1):
                queue.put(True)
                break
            os.system('cls' if os.name == 'nt' else 'clear')
            pattern = self.generate_wave_pattern(width, height, frame)
            for y, row in enumerate(pattern):
                if y < height:
                    print(row[:width])
            frame += 1
            time.sleep(0.1)
        os.system('cls' if os.name == 'nt' else 'clear')

    def notify_tasks(self):
        while True:
            for task in [t for t in self.current_user.tasks if not t.completed]:
                due = datetime.fromisoformat(task.due_date)
                if (due - datetime.now()).total_seconds() <= 3600:
                    self.notification_queue.put(f"{RED}Alert: Task '{task.title}' due in 1 hour!{RESET}")
            time.sleep(300)

    def animated_header(self):
        frames = ["|", "/", "-", "\\"]
        for _ in range(5):
            for frame in frames:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"{RED}╔════════════════════════════════════════════╗{RESET}")
                print(f"{RED}║    {YELLOW}ADVANCED TASK MANAGER CLI {CYAN}v{self.version} {frame}{RESET}    {RED}║{RESET}")
                print(f"{RED}╠════════════════════════════════════════════╣{RESET}")
                print(f"{RED}║ {CYAN}Efficient. Organized. Productive.{RESET} {RED}║{RESET}")
                print(f"{RED}╚════════════════════════════════════════════╝{RESET}")
                sys.stdout.flush()
                time.sleep(0.2)

    def loading_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        bar_length = 50
        for i in range(bar_length + 1):
            os.system('cls' if os.name == 'nt' else 'clear')
            percentage = (i / bar_length) * 100
            filled = int(i)
            bar = f"{CYAN}[{'█' * filled}{' ' * (bar_length - filled)}] {percentage:.0f}%{RESET}"
            print(f"{YELLOW}Loading...{RESET}")
            print(bar)
            sys.stdout.flush()
            time.sleep(0.05)  # Adjust speed of loading bar
        os.system('cls' if os.name == 'nt' else 'clear')

    def run(self):
        tasks = self._load_tasks()
        last_input_time = time.time()
        queue = Queue()
        notify_thread = threading.Thread(target=self.notify_tasks, daemon=True)
        notify_thread.start()

        self.loading_screen()  # Add loading screen before menu
        self.animated_header()
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{RED}╔════════════════════════════════════════════╗{RESET}")
            print(f"{RED}║    {YELLOW}ADVANCED TASK MANAGER CLI v{self.version}{RESET}    {RED}║{RESET}")
            print(f"{RED}╠════════════════════════════════════════════╣{RESET}")
            print(f"{RED}║ {CYAN}Efficient. Organized. Productive.{RESET} {RED}║{RESET}")
            print(f"{RED}╚════════════════════════════════════════════╝{RESET}")
            print(f"{BLUE}1. Add Task{RESET}")
            print(f"{BLUE}2. Edit Task{RESET}")
            print(f"{BLUE}3. Delete Task{RESET}")
            print(f"{BLUE}4. Undo Delete{RESET}")
            print(f"{BLUE}5. Toggle Completion{RESET}")
            print(f"{BLUE}6. Filter Tasks{RESET}")
            print(f"{BLUE}7. Sort Tasks{RESET}")
            print(f"{BLUE}8. Search Tasks{RESET}")
            print(f"{BLUE}9. Export Tasks{RESET}")
            print(f"{BLUE}10. Import Tasks{RESET}")
            print(f"{BLUE}11. Show Dashboard{RESET}")
            print(f"{BLUE}12. Manage Categories{RESET}")
            print(f"{BLUE}13. Display All Tasks{RESET}")
            print(f"{BLUE}14. Exit{RESET}")

            while not queue.empty():
                print(self.notification_queue.get())

            if time.time() - last_input_time > 15:
                self.idle_animation(last_input_time, queue)

            choice = input(f"{YELLOW}Enter your choice (1-14): {RESET}")
            last_input_time = time.time()

            if choice == "1":
                self.add_task()
            elif choice == "2":
                self.edit_task()
            elif choice == "3":
                self.delete_task()
            elif choice == "4":
                self.undo_delete()
            elif choice == "5":
                self.toggle_complete()
            elif choice == "6":
                self.filter_tasks()
            elif choice == "7":
                self.sort_tasks()
            elif choice == "8":
                self.search_tasks()
            elif choice == "9":
                self.export_tasks()
            elif choice == "10":
                self.import_tasks()
            elif choice == "11":
                self.show_dashboard()
            elif choice == "12":
                self.manage_categories()
            elif choice == "13":
                page = 1
                while True:
                    self.display_tasks(page)
                    nav = input(f"{YELLOW}Navigate (p=prev, n=next, d=details, q=quit): {RESET}")
                    if nav == "p" and page > 1:
                        page -= 1
                    elif nav == "n" and page * 5 < len(self.current_user.tasks):
                        page += 1
                    elif nav == "d":
                        task_id = input(f"{YELLOW}Enter task ID for details: {RESET}")
                        task = next((t for t in self.current_user.tasks if t.id == task_id), None)
                        if task:
                            print(f"{CYAN}Details for {task.title}: {task.description}{RESET}")
                            input(f"{YELLOW}Press Enter to continue...{RESET}")
                    elif nav == "q":
                        break
                    else:
                        print(f"{RED}Invalid navigation.{RESET}")
                input(f"{YELLOW}Press Enter to continue...{RESET}")
                os.system('cls' if os.name == 'nt' else 'clear')
            elif choice == "14":
                print(f"{GREEN}Selected: Exit{RESET}")
                print(f"{YELLOW}Exiting...{RESET}")
                break
            else:
                print(f"{RED}Invalid choice. Please try again.{RESET}")
                time.sleep(1)

            changed = False
            for task in [t for t in self.current_user.tasks if t.recurring != "none"]:
                if task.completed and datetime.now() > datetime.fromisoformat(task.due_date):
                    new_task = Task(**vars(task))
                    new_task.id = str(uuid.uuid4())
                    new_task.completed = False
                    new_task.due_date = (datetime.fromisoformat(task.due_date) + timedelta(days=1 if task.recurring == "daily" else 7)).isoformat()
                    self.current_user.tasks.append(new_task)
                    task.completed = False
                    changed = True
            if changed:
                self._save_tasks()

if __name__ == "__main__":
    manager = TaskManager()
    manager.run()