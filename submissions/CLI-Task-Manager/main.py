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
import re

# Configures logging
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
    description: str = ""  # It Now supports Markdown
    priority: str = "low"
    due_date: str = datetime.now().isoformat()
    category: str = "general"
    completed: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    progress: int = 0  # 0%-100%
    effort_hours: float = 1.0
    dependencies: List[str] = field(default_factory=list)
    recurring: str = "none"  # 'daily', 'weekly', OR 'none'

@dataclass
class User:
    username: str
    password_hash: str  # Use proper hashing in production
    tasks: List[Task] = field(default_factory=list)
    points: int = 0  # For gamification
    avatar: str = ""  # Custom ASCII avatar
    milestone_history: List[Dict] = field(default_factory=list)  # Track milestones and task points

class TaskManager:
    def __init__(self):
        self.users = self._load_users()
        self.current_user = self._authenticate()
        self.undo_stack = []
        self.notification_queue = Queue()
        self.categories = set(t.category for t in self.current_user.tasks)
        self.shared_tasks_file = "shared_tasks.json"  # Collaborative mode file
        self.cloud_tasks_file = "cloud_tasks.json"  # Simulated local cloud sync file
        self.version = "2.9"

    def _load_users(self) -> Dict[str, User]:
        try:
            if os.path.exists("users.json"):
                with open("users.json", "r") as f:
                    data = json.load(f)
                    return {u["username"]: User(u["username"], u["password_hash"], [Task(**task) for task in u.get("tasks", [])], u.get("points", 0), u.get("avatar", ""), u.get("milestone_history", [])) for u in data}
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
                json.dump([{"username": u.username, "password_hash": u.password_hash, "tasks": [vars(t) for t in u.tasks], "points": u.points, "avatar": u.avatar, "milestone_history": u.milestone_history} for u in self.users.values()], f, indent=2)
            shutil.copy("users.json", f"backup_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        except Exception as e:
            logging.error(f"Error saving users: {e}")

    def _load_tasks(self) -> List[Task]:
        return self.current_user.tasks

    def _save_tasks(self):
        self._save_users()
        self._backup_tasks()
        self._sync_shared_tasks()  # Syncs with shared file

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

    def _sync_shared_tasks(self):
        if os.path.exists(self.shared_tasks_file):
            try:
                with open(self.shared_tasks_file, "r") as f:
                    shared_tasks = [Task(**task) for task in json.load(f)]
                task_dict = {t.id: t for t in self.current_user.tasks}
                for task in shared_tasks:
                    task_dict[task.id] = task
                self.current_user.tasks = list(task_dict.values())
                self._save_tasks()
            except Exception as e:
                logging.error(f"Error syncing shared tasks: {e}")

    def _save_shared_tasks(self):
        with open(self.shared_tasks_file, "w") as f:
            json.dump([vars(t) for t in self.current_user.tasks], f, indent=2)

    def _sync_cloud_tasks(self):
        if os.path.exists(self.cloud_tasks_file):
            try:
                with open(self.cloud_tasks_file, "r") as f:
                    cloud_tasks = [Task(**task) for task in json.load(f)]
                task_dict = {t.id: t for t in self.current_user.tasks}
                for task in cloud_tasks:
                    task_dict[task.id] = task
                self.current_user.tasks = list(task_dict.values())
                self._save_tasks()
            except Exception as e:
                logging.error(f"Error syncing cloud tasks: {e}")
        else:
            self._save_cloud_tasks()

    def _save_cloud_tasks(self):
        with open(self.cloud_tasks_file, "w") as f:
            json.dump([vars(t) for t in self.current_user.tasks], f, indent=2)

    # Placeholder for future API sync (kept in standby)
    # def _sync_with_api(self):
    #     # Future implementation: Use requests library for API calls
    #     # Example: POST to cloud endpoint, handle auth tokens
    #     pass

    def _render_markdown(self, text):
        # Basic Markdown rendering: bold (**text**), italics (*text*), headers (# text)
        text = re.sub(r'\*\*(.*?)\*\*', f"{CYAN}\\1{RESET}", text)  # Bold
        text = re.sub(r'\*(.*?)\*', f"{MAGENTA}\\1{RESET}", text)  # Italics
        text = re.sub(r'^#\s(.*?)$', f"{YELLOW}\\1{RESET}", text, flags=re.MULTILINE)  # Header
        return text

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
            rendered_desc = self._render_markdown(task.description[:20]) if task.description else "No description"
            print(f"{BLUE}│ [{status}] {task.title[:25]:<25} | {task.priority[:10]:<10} | {task.due_date[:10]:<10} | {progress_bar:<22} | ID: {task.id} │{RESET}")
            print(f"{BLUE}│ Description: {rendered_desc:<65}│{RESET}")
        print(f"{BLUE}└{'─' * 80}┘{RESET}")
        print(f"{YELLOW}Page {page}/{total_pages} (p=prev, n=next, d=details, q=quit){RESET}")

    def add_task(self):
        print(f"{GREEN}Selected: Add Task{RESET}")
        try:
            # AI Suggestion for title
            category = input(f"{YELLOW}Enter category: {RESET}").strip() or "general"
            suggested_title = self._suggest_title(category)
            title = input(f"{YELLOW}Enter task title (suggestion: {suggested_title}): {RESET}").strip() or suggested_title or "Untitled"

            # AI Suggestion for description
            suggested_desc = self._suggest_description(category, title)
            description = input(f"{YELLOW}Enter description (Markdown OK, suggestion: {suggested_desc}): {RESET}").strip() or suggested_desc

            task_data = {
                "title": title,
                "description": description,
                "priority": input(f"{YELLOW}Enter priority (low/medium/high): {RESET}").lower() or "low",
                "due_date": input(f"{YELLOW}Enter due date (YYYY-MM-DD): {RESET}") or datetime.now().isoformat(),
                "category": category,
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

            # AI Suggestion for the entire task
            suggested_task = self._suggest_full_task(category, task_data)
            print(f"{CYAN}AI Suggestion for Task Details: {suggested_task['title']}, Description: {suggested_task['description']}, Priority: {suggested_task['priority']}, Due Date: {suggested_task['due_date']}, Progress: {suggested_task['progress']}%{RESET}")
            if input(f"{YELLOW}Accept AI suggestion and edit details? (y/n): {RESET}").lower() == "y":
                try:
                    task.title = input(f"{YELLOW}Enter new title ({suggested_task['title']}): {RESET}") or suggested_task['title']
                    task.description = input(f"{YELLOW}Enter new description (Markdown OK, {suggested_task['description']}): {RESET}") or suggested_task['description']
                    task.priority = input(f"{YELLOW}Enter new priority ({suggested_task['priority']}): {RESET}") or suggested_task['priority']
                    task.due_date = input(f"{YELLOW}Enter new due date ({suggested_task['due_date']}): {RESET}") or suggested_task['due_date']
                    task.progress = int(input(f"{YELLOW}Enter new progress ({suggested_task['progress']}): {RESET}") or suggested_task['progress'])
                    task.effort_hours = float(input(f"{YELLOW}Enter new effort hours ({task.effort_hours}): {RESET}") or task.effort_hours)
                    if input(f"{YELLOW}Update dependencies? (y/n): {RESET}").lower() == "y":
                        task.dependencies = input(f"{YELLOW}Enter new dependent task IDs: {RESET}").split(",")
                    task.recurring = input(f"{YELLOW}Enter new recurrence ({task.recurring}): {RESET}") or task.recurring
                    self._save_tasks()
                    print(f"{GREEN}Task updated with AI suggestions!{RESET}")
                except ValueError as e:
                    print(f"{RED}Error: Invalid input. {e}{RESET}")
            else:
                print(f"{GREEN}Returning to main menu...{RESET}")
                return  # Exit to main menu if 'n' is given

        except ValueError as e:
            print(f"{RED}Error: {e}{RESET}")
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        os.system('cls' if os.name == 'nt' else 'clear')

    def _suggest_title(self, category):
        # Simple AI-like suggestion based on category
        suggestions = {
            "work": "Complete Project Report",
            "personal": "Plan Weekend Trip",
            "general": "New Task Item",
            "study": "Review Chapter 5"
        }
        return suggestions.get(category.lower(), "New Task")

    def _suggest_description(self, category, title):
        # Simple AI-like suggestion based on category and title
        if "report" in title.lower() or "work" in category.lower():
            return "Prepare detailed **report** with data analysis. *Due by end of day.*"
        elif "trip" in title.lower() or "personal" in category.lower():
            return "Plan itinerary and book tickets. *Include destinations.*"
        elif "study" in category.lower():
            return "Read and summarize key points. #StudyNotes"
        return "Add task details here. *Optional Markdown support.*"

    def _suggest_full_task(self, category, task_data):
        # Suggest a full task based on category and current data
        suggested_title = self._suggest_title(category)
        suggested_desc = self._suggest_description(category, suggested_title)
        return {
            "title": suggested_title,
            "description": suggested_desc,
            "priority": "high" if "urgent" in task_data["title"].lower() or category.lower() == "work" else "low",
            "due_date": (datetime.now() + timedelta(days=1)).isoformat() if category.lower() == "work" else task_data["due_date"],
            "progress": 0,
            "effort_hours": 2.0 if category.lower() == "work" else 1.0
        }

    def edit_task(self):
        print(f"{GREEN}Selected: Edit Task{RESET}")
        self.display_tasks()
        task_id = input(f"{YELLOW}Enter task ID to edit: {RESET}")
        task = next((t for t in self.current_user.tasks if t.id == task_id), None)
        if task:
            try:
                task.title = input(f"{YELLOW}Enter new title ({task.title}): {RESET}") or task.title
                task.description = input(f"{YELLOW}Enter new description (Markdown OK, current: {task.description}): {RESET}") or task.description
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
            if task.completed:
                points_earned = self._calculate_points(task)
                self.current_user.points += points_earned
                self.current_user.milestone_history.append({
                    "task_id": task.id,
                    "title": task.title,
                    "points": points_earned,
                    "achieved_at": datetime.now().isoformat(),
                    "priority_bonus": 5 if task.priority == "high" else 0,
                    "timeliness_bonus": 5 if datetime.now() <= datetime.fromisoformat(task.due_date) else 0
                })
                if self.current_user.points >= 50 and not any(m["points"] == 50 for m in self.current_user.milestone_history if "milestone" in m):
                    self.current_user.milestone_history.append({"milestone": 50, "achieved_at": datetime.now().isoformat()})
                    self._show_milestone()
            self._save_tasks()
            print(f"{GREEN}Task completion toggled! Points earned: {points_earned if task.completed else 0}{RESET}")
        else:
            print(f"{RED}Task not found.{RESET}")
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        os.system('cls' if os.name == 'nt' else 'clear')

    def _calculate_points(self, task):
        base_points = 10
        priority_bonus = 5 if task.priority == "high" else 0
        timeliness_bonus = 5 if datetime.now() <= datetime.fromisoformat(task.due_date) else 0
        return base_points + priority_bonus + timeliness_bonus

    def _show_milestone(self):
        trophy = f"{GREEN}🏆 Congrats! You've reached 50 points! 🎉{RESET}\n" \
                 f"{GREEN}       .-""""""""-.\n" \
                 f"      .'          '.\n" \
                 f"     : ,          , :\n" \
                 f"     : ,  🏆    , :\n" \
                 f"      `._         _.'{RESET}"
        fireworks = f"{MAGENTA}🎆 Boom! Celebration time! 🎆{RESET}"
        print(trophy)
        print(fireworks)
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        os.system('cls' if os.name == 'nt' else 'clear')

    def check_milestones(self):
        print(f"{GREEN}Selected: Check Milestones{RESET}")
        print(f"{CYAN}Current Points: {self.current_user.points}{RESET}")
        if self.current_user.points >= 50:
            self._show_milestone()
        else:
            print(f"{YELLOW}Keep going! Need {50 - self.current_user.points} more points for the next milestone!{RESET}")

        while True:
            action = input(f"{YELLOW}Press 'h' for help on milestones, or Enter to exit: {RESET}").lower()
            if action == "h":
                self._show_milestone_help()
            elif not action:  # Enter key
                break
            else:
                print(f"{RED}Invalid input. Use 'h' or Enter.{RESET}")
        os.system('cls' if os.name == 'nt' else 'clear')

    def _show_milestone_help(self):
        print(f"{GREEN}=== Milestone Help ==={RESET}")
        print(f"{CYAN}Current Points: {self.current_user.points}{RESET}")
        if self.current_user.milestone_history:
            print(f"{CYAN}Milestone History & Reward Details:{RESET}")
            for entry in self.current_user.milestone_history:
                if "task_id" in entry:
                    print(f"- Task: {entry['title']} (ID: {entry['task_id']})")
                    print(f"  - Base Points: 10")
                    print(f"  - Priority Bonus: {entry['priority_bonus']} (High priority adds 5){RESET}")
                    print(f"  - Timeliness Bonus: {entry['timeliness_bonus']} (On-time adds 5){RESET}")
                    print(f"  - Total Points: {entry['points']} (Earned on {entry['achieved_at'][:19]}){RESET}")
                elif "milestone" in entry:
                    print(f"- Milestone Reached: {entry['milestone']} points on {entry['achieved_at'][:19]}{RESET}")
        else:
            print(f"{YELLOW}No milestones or task completions yet.{RESET}")
        print(f"{CYAN}Reward System:{RESET}")
        print(f"- Base Points: 10 per completed task{RESET}")
        print(f"- Priority Bonus: +5 for high-priority tasks{RESET}")
        print(f"- Timeliness Bonus: +5 if completed on or before due date{RESET}")
        print(f"{CYAN}Next Milestone: 50 points (triggers celebration!){RESET}")
        input(f"{YELLOW}Press Enter to continue...{RESET}")

    def filter_tasks(self):
        print(f"{GREEN}Selected: Filter Tasks{RESET}")
        category = input(f"{YELLOW}Enter category: {RESET}")
        filtered = [t for t in self.current_user.tasks if category.lower() in t.category.lower()]
        self.display_tasks(page=1, tasks=filtered)
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        os.system('cls' if os.name == 'nt' else 'clear')

    # Commented out Sort Tasks
    # def sort_tasks(self):
    #     print(f"{GREEN}Selected: Sort Tasks{RESET}")
    #     sort_by = input(f"{YELLOW}Sort by (priority/due_date/created_at): {RESET}").lower()
    #     if sort_by == "priority":
    #         self.current_user.tasks.sort(key=lambda t: {"high": 0, "medium": 1, "low": 2}.get(t.priority.lower(), 3))
    #     elif sort_by == "due_date":
    #         self.current_user.tasks.sort(key=lambda t: datetime.fromisoformat(t.due_date))
    #     else:
    #         self.current_user.tasks.sort(key=lambda t: t.created_at)
    #     self._save_tasks()
    #     self.display_tasks()
    #     input(f"{YELLOW}Press Enter to continue...{RESET}")
    #     os.system('cls' if os.name == 'nt' else 'clear')

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
        print(f"{CYAN}Total Tasks: {total} | Points: {self.current_user.points}{RESET}")
        print(f"{CYAN}Completed: {completed} ({completed/total*100:.1f}%) | Avatar: {self.current_user.avatar or 'None'}{RESET}")
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
            time.sleep(0.05)
        os.system('cls' if os.name == 'nt' else 'clear')

    def set_avatar(self):
        print(f"{GREEN}Selected: Set Avatar{RESET}")
        avatar = input(f"{YELLOW}Enter your ASCII avatar (e.g., ':-)' or '🐱'): {RESET}").strip()
        self.current_user.avatar = avatar
        self._save_users()
        print(f"{GREEN}Avatar set to: {avatar}{RESET}")
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        os.system('cls' if os.name == 'nt' else 'clear')

    def team_shoutout(self):
        print(f"{GREEN}Selected: Team Shoutout{RESET}")
        message = input(f"{YELLOW}Enter shoutout message: {RESET}")
        shoutout_art = f"{MAGENTA}🎉 {message} 🎉\n" \
                       f"{MAGENTA} .-""""""""-.\n" \
                       f": ,  👥  , :\n" \
                       f": ,______ , :\n" \
                       f" `._      _.'{RESET}"
        print(shoutout_art)
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        os.system('cls' if os.name == 'nt' else 'clear')

    def sync_cloud(self):
        print(f"{GREEN}Selected: Sync with Cloud{RESET}")
        action = input(f"{YELLOW}Sync to cloud (t) or from cloud (f)? (t/f): {RESET}").lower()
        if action == "t":
            self._save_cloud_tasks()
            print(f"{GREEN}Tasks synced to cloud!{RESET}")
            # Placeholder for API call (on-standby)
            # self._sync_with_api(action="upload")
        elif action == "f":
            self._sync_cloud_tasks()
            print(f"{GREEN}Tasks synced from cloud!{RESET}")
            # Placeholder for API call (on-standby)
            # self._sync_with_api(action="download")
        else:
            print(f"{RED}Invalid choice. Use 't' or 'f'.{RESET}")
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        os.system('cls' if os.name == 'nt' else 'clear')

    def check_milestones(self):
        print(f"{GREEN}Selected: Check Milestones{RESET}")
        print(f"{CYAN}Current Points: {self.current_user.points}{RESET}")
        if self.current_user.points >= 50:
            self._show_milestone()
        else:
            print(f"{YELLOW}Keep going! Need {50 - self.current_user.points} more points for the next milestone!{RESET}")

        while True:
            action = input(f"{YELLOW}Press 'h' for help on milestones, or Enter to exit: {RESET}").lower()
            if action == "h":
                self._show_milestone_help()
            elif not action:  # Enter key
                break
            else:
                print(f"{RED}Invalid input. Use 'h' or Enter.{RESET}")
        os.system('cls' if os.name == 'nt' else 'clear')

    def _show_milestone_help(self):
        print(f"{GREEN}=== Milestone Help ==={RESET}")
        print(f"{CYAN}Current Points: {self.current_user.points}{RESET}")
        if self.current_user.milestone_history:
            print(f"{CYAN}Milestone History & Reward Details:{RESET}")
            for entry in self.current_user.milestone_history:
                if "task_id" in entry:
                    print(f"- Task: {entry['title']} (ID: {entry['task_id']})")
                    print(f"  - Base Points: 10")
                    print(f"  - Priority Bonus: {entry['priority_bonus']} (High priority adds 5){RESET}")
                    print(f"  - Timeliness Bonus: {entry['timeliness_bonus']} (On-time adds 5){RESET}")
                    print(f"  - Total Points: {entry['points']} (Earned on {entry['achieved_at'][:19]}){RESET}")
                elif "milestone" in entry:
                    print(f"- Milestone Reached: {entry['milestone']} points on {entry['achieved_at'][:19]}{RESET}")
        else:
            print(f"{YELLOW}No milestones or task completions yet.{RESET}")
        print(f"{CYAN}Reward System:{RESET}")
        print(f"- Base Points: 10 per completed task{RESET}")
        print(f"- Priority Bonus: +5 for high-priority tasks{RESET}")
        print(f"- Timeliness Bonus: +5 if completed on or before due date{RESET}")
        print(f"{CYAN}Next Milestone: 50 points (triggers celebration!){RESET}")
        input(f"{YELLOW}Press Enter to continue...{RESET}")

    def run(self):
        tasks = self._load_tasks()
        last_input_time = time.time()
        queue = Queue()
        notify_thread = threading.Thread(target=self.notify_tasks, daemon=True)
        notify_thread.start()

        self.loading_screen()
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
            # Commented out Sort Tasks
            # print(f"{BLUE}7. Sort Tasks{RESET}")
            print(f"{BLUE}7. Search Tasks{RESET}")
            print(f"{BLUE}8. Export Tasks{RESET}")
            print(f"{BLUE}9. Import Tasks{RESET}")
            print(f"{BLUE}10. Show Dashboard{RESET}")
            print(f"{BLUE}11. Manage Categories{RESET}")
            print(f"{BLUE}12. Display All Tasks{RESET}")
            print(f"{BLUE}13. Set Avatar{RESET}")
            print(f"{BLUE}14. Team Shoutout{RESET}")
            print(f"{BLUE}15. Sync with Cloud{RESET}")
            print(f"{BLUE}16. Check Milestones{RESET}")
            print(f"{BLUE}17. Exit{RESET}")

            while not queue.empty():
                print(self.notification_queue.get())

            if time.time() - last_input_time > 15:
                self.idle_animation(last_input_time, queue)

            choice = input(f"{YELLOW}Enter your choice (1-17): {RESET}")
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
            # Commented out Sort Tasks logic
            # elif choice == "7":
            #     self.sort_tasks()
            elif choice == "7":
                self.search_tasks()
            elif choice == "8":
                self.export_tasks()
            elif choice == "9":
                self.import_tasks()
            elif choice == "10":
                self.show_dashboard()
            elif choice == "11":
                self.manage_categories()
            elif choice == "12":
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
                            print(f"{CYAN}Details for {task.title}: {self._render_markdown(task.description)}{RESET}")
                            input(f"{YELLOW}Press Enter to continue...{RESET}")
                    elif nav == "q":
                        break
                    else:
                        print(f"{RED}Invalid navigation.{RESET}")
                input(f"{YELLOW}Press Enter to continue...{RESET}")
                os.system('cls' if os.name == 'nt' else 'clear')
            elif choice == "13":
                self.set_avatar()
            elif choice == "14":
                self.team_shoutout()
            elif choice == "15":
                self.sync_cloud()
            elif choice == "16":
                self.check_milestones()
            elif choice == "17":
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
