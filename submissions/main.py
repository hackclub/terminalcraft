import json
import os
import calendar
from datetime import datetime, date, timedelta
from colorama import init, Fore, Style

init(autoreset=True)


TASKS_FILE = "tasks.json"
USERNAME_FILE = "username.txt"

def get_username():

    if os.path.exists(USERNAME_FILE):
        with open(USERNAME_FILE, "r") as f:
            username = f.read().strip()
        if username:
            return username
    username = input("Enter your name: ").strip()
    with open(USERNAME_FILE, "w") as f:
        f.write(username)
    return username

class TaskManager:
    def __init__(self, username):
        self.username = username
        self.tasks = []           
        self.last_deleted = None  
        self.load_tasks()        
        self.check_overdue_tasks()

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def display_urgent_tasks(self):
        today_dt = date.today()
        urgent = [t for t in self.tasks if (not t["completed"] and datetime.strptime(t["date"], "%Y-%m-%d").date() <= today_dt)]
        urgent.sort(key=lambda t: datetime.strptime(t["date"], "%Y-%m-%d").date())
        if urgent:
            print(Fore.RED + "!!! Urgent Tasks (due today or overdue):")
            for i, task in enumerate(urgent[:3]):
                print(Fore.RED + f"  {i+1}. {task['title']} - Due: {task['date']}")
            print(Style.RESET_ALL)
        else:
            print(Fore.GREEN + "No urgent tasks.")
        print("-" * 40)

    def display_statistics(self):
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t["completed"])
        pending = total - completed
        today_str = date.today().strftime("%Y-%m-%d")
        overdue = sum(1 for t in self.tasks if (not t["completed"] and t["date"] < today_str))
        stats = f"Total: {total} | Completed: {completed} | Pending: {pending} | Overdue: {overdue}"
        print(Fore.YELLOW + stats)
        print("-" * 40)

    def show_menu(self):
        print(Fore.CYAN + "======================================")
        print(Fore.CYAN + "              Task Board        ")
        print(Fore.CYAN + f"              User: {self.username}              ")
        print(Fore.CYAN + "======================================")
        self.display_urgent_tasks()  
        self.display_statistics()     
        print(Fore.CYAN + "1. Add Task")
        print(Fore.CYAN + "2. Edit Task")
        print(Fore.CYAN + "3. Delete Task")
        print(Fore.CYAN + "4. Mark Task as Completed")
        print(Fore.CYAN + "5. View Task Details")
        print(Fore.CYAN + "6. AI Assistant Recommendation")
        print(Fore.CYAN + "7. Sort Tasks")
        print(Fore.CYAN + "8. Filter Tasks")
        print(Fore.CYAN + "9. Dashboard / Statistics")
        print(Fore.CYAN + "10. Export Tasks to Report")
        print(Fore.CYAN + "11. Clear Completed Tasks")
        print(Fore.CYAN + "12. Undo Last Deletion")
        print(Fore.CYAN + "13. Quit")
        print(Fore.CYAN + "======================================")

    def list_tasks(self, tasks=None):
        if tasks is None:
            tasks = self.tasks
        if not tasks:
            print(Fore.MAGENTA + "No tasks available.")
        else:
            print(Fore.MAGENTA + "Tasks:")
            for i, task in enumerate(tasks):
                status = Fore.GREEN + "✔" if task["completed"] else Fore.RED + "✖"
                print(Fore.WHITE + f"{i+1}. {task['title']} - {task['date']} [Priority: {task['priority']}] - {status}")
        print(Fore.WHITE + "-" * 40)

    def add_task(self):
        print("----- Add Task -----")
        title = input("Task Title: ").strip()
        if not title:
            print("Task title cannot be empty.")
            input("Press Enter to continue...")
            return
        date_input = input("Due Date (YYYY-MM-DD or 'tomorrow'/'today') [default today]: ").strip()
        if not date_input:
            due_date = date.today()
        elif date_input.lower() in ["tomorrow", "tmrw"]:
            due_date = date.today() + timedelta(days=1)
        elif date_input.lower() in ["today"]:
            due_date = date.today()
        else:
            try:
                due_date = datetime.strptime(date_input, "%Y-%m-%d").date()
            except ValueError:
                print("Invalid date format. Task not added.")
                input("Press Enter to continue...")
                return
        due_date_str = due_date.strftime("%Y-%m-%d")
        details = input("Task Details (optional): ").strip()
        priority_input = input("Priority (1-low, 5-high) [default 3]: ").strip()
        if not priority_input:
            priority = 3
        else:
            try:
                priority = int(priority_input)
                if priority < 1 or priority > 5:
                    print("Priority must be between 1 and 5. Setting to default (3).")
                    priority = 3
            except ValueError:
                print("Invalid input. Setting priority to default (3).")
                priority = 3
        category = input("Category (optional, e.g., Household, School, Work, Personal, Other): ").strip()
        with_whom = input("With (optional): ").strip()
        task = {
            "title": title,
            "date": due_date_str,
            "details": details,
            "priority": priority,
            "category": category,
            "with": with_whom,
            "completed": False
        }
        confirm = input("Confirm adding task? (y/n): ").strip().lower()
        if confirm == "y":
            self.tasks.append(task)
            self.save_tasks()
            print("Task added.")
        else:
            print("Task not added.")
        input("Press Enter to continue...")

    def edit_task(self):
        print("----- Edit Task -----")
        self.list_tasks()
        idx = input("Enter task number to edit: ").strip()
        if not idx.isdigit() or int(idx) < 1 or int(idx) > len(self.tasks):
            print("Invalid task number.")
            input("Press Enter to continue...")
            return
        index = int(idx) - 1
        task = self.tasks[index]
        print(f"Editing Task: {task['title']}")
        new_title = input(f"New Title (leave blank to keep '{task['title']}'): ").strip()
        if new_title:
            task["title"] = new_title
        new_date = input(f"New Due Date (YYYY-MM-DD or 'tomorrow') (leave blank to keep '{task['date']}'): ").strip()
        if new_date:
            if new_date.lower() in ["tomorrow"]:
                new_due = date.today() + timedelta(days=1)
                task["date"] = new_due.strftime("%Y-%m-%d")
            else:
                try:
                    datetime.strptime(new_date, "%Y-%m-%d")
                    task["date"] = new_date
                except ValueError:
                    print("Invalid date format. Date not changed.")
        new_details = input("New Details (leave blank to keep current): ").strip()
        if new_details:
            task["details"] = new_details
        new_priority = input(f"New Priority (1-5) (leave blank to keep '{task['priority']}'): ").strip()
        if new_priority:
            try:
                prio = int(new_priority)
                if 1 <= prio <= 5:
                    task["priority"] = prio
                else:
                    print("Invalid priority. Not changed.")
            except ValueError:
                print("Invalid input. Not changed.")
        new_category = input(f"New Category (leave blank to keep '{task['category']}'): ").strip()
        if new_category:
            task["category"] = new_category
        new_with = input(f"New With (leave blank to keep '{task['with']}'): ").strip()
        if new_with:
            task["with"] = new_with
        self.save_tasks()
        print("Task updated.")
        input("Press Enter to continue...")

    def delete_task(self):
        print("----- Delete Task -----")
        self.list_tasks()
        idx = input("Enter task number to delete: ").strip()
        if not idx.isdigit() or int(idx) < 1 or int(idx) > len(self.tasks):
            print("Invalid task number.")
            input("Press Enter to continue...")
            return
        index = int(idx) - 1
        task = self.tasks[index]
        confirm = input(f"Are you sure you want to delete task '{task['title']}'? (y/n): ").strip().lower()
        if confirm == "y":
            self.last_deleted = (index, task)
            del self.tasks[index]
            self.save_tasks()
            print("Task deleted.")
        else:
            print("Deletion cancelled.")
        input("Press Enter to continue...")

    def mark_completed(self):
        print("----- Mark Task as Completed -----")
        self.list_tasks()
        idx = input("Enter task number to mark as completed: ").strip()
        if not idx.isdigit() or int(idx) < 1 or int(idx) > len(self.tasks):
            print("Invalid task number.")
            input("Press Enter to continue...")
            return
        index = int(idx) - 1
        self.tasks[index]["completed"] = True
        self.save_tasks()
        print("Task marked as completed.")
        input("Press Enter to continue...")

    def view_details(self):
        print("----- View Task Details -----")
        self.list_tasks()
        idx = input("Enter task number to view details: ").strip()
        if not idx.isdigit() or int(idx) < 1 or int(idx) > len(self.tasks):
            print("Invalid task number.")
            input("Press Enter to continue...")
            return
        index = int(idx) - 1
        task = self.tasks[index]
        print(Style.BRIGHT + "======================================")
        print(f"Title: {task['title']}")
        print(f"Due Date: {task['date']}")
        print(f"Priority: {task['priority']}")
        print(f"Category: {task['category']}")
        print(f"With: {task['with']}")
        print(f"Completed: {'Yes' if task['completed'] else 'No'}")
        print("Details:")
        print(task['details'] if task['details'] else "No details provided.")
        print("======================================")
        input("Press Enter to continue...")

    def ai_assistant(self):
        print("----- AI Assistant Recommendation -----")
        pending_tasks = [t for t in self.tasks if not t["completed"]]
        if not pending_tasks:
            print("No pending tasks.")
            input("Press Enter to continue...")
            return
        best_task = None
        best_score = -1
        today = date.today()
        for task in pending_tasks:
            try:
                due_date = datetime.strptime(task["date"], "%Y-%m-%d").date()
            except Exception:
                continue
            days_left = (due_date - today).days
            if days_left < 0:
                score = task["priority"] * 10
            else:
                score = task["priority"] / (days_left + 1)
            if score > best_score:
                best_score = score
                best_task = task
        if best_task:
            print(Fore.BLUE + f"Recommendation: Do '{best_task['title']}' (Due: {best_task['date']}, Priority: {best_task['priority']})")
        else:
            print("No valid task found.")
        input("Press Enter to continue...")

    def sort_tasks(self):
        print("----- Sort Tasks -----")
        print("1. Sort by Due Date")
        print("2. Sort by Priority")
        choice = input("Choose option: ").strip()
        if choice == "1":
            self.tasks.sort(key=lambda t: t["date"])
            print("Tasks sorted by due date.")
        elif choice == "2":
            self.tasks.sort(key=lambda t: t["priority"])
            print("Tasks sorted by priority.")
        else:
            print("Invalid option.")
        self.save_tasks()
        input("Press Enter to continue...")

    def filter_tasks(self):
        print("----- Filter Tasks -----")
        print("1. Filter by Category")
        print("2. Filter by Status (completed/pending)")
        choice = input("Choose option: ").strip()
        filtered = []
        if choice == "1":
            category = input("Enter category to filter by: ").strip()
            filtered = [t for t in self.tasks if t["category"].lower() == category.lower()]
        elif choice == "2":
            status = input("Enter status (completed/pending): ").strip().lower()
            if status == "completed":
                filtered = [t for t in self.tasks if t["completed"]]
            elif status == "pending":
                filtered = [t for t in self.tasks if not t["completed"]]
            else:
                print("Invalid status.")
                input("Press Enter to continue...")
                return
        else:
            print("Invalid option.")
            input("Press Enter to continue...")
            return
        if not filtered:
            print("No tasks match the filter criteria.")
        else:
            print("Filtered Tasks:")
            for i, task in enumerate(filtered):
                print(f"{i+1}. {task['title']} - {task['date']} {'(Completed)' if task['completed'] else ''}")
        input("Press Enter to continue...")

    def dashboard(self):
        print("----- Dashboard / Statistics -----")
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t["completed"])
        pending = total - completed
        today_str = date.today().strftime("%Y-%m-%d")
        overdue = sum(1 for t in self.tasks if not t["completed"] and t["date"] < today_str)
        print(Fore.YELLOW + f"Total tasks: {total}")
        print(Fore.YELLOW + f"Completed tasks: {completed}")
        print(Fore.YELLOW + f"Pending tasks: {pending}")
        print(Fore.YELLOW + f"Overdue tasks: {overdue}")
        input("Press Enter to continue...")

    def export_report(self):
        print("----- Export Tasks to Report -----")
        report_file = "task_report.txt"
        with open(report_file, "w") as f:
            f.write("Task Report\n")
            f.write("===========\n\n")
            for i, task in enumerate(self.tasks):
                f.write(f"{i+1}. {task['title']} - Due: {task['date']} - Priority: {task['priority']} - Category: {task['category']} - With: {task['with']}\n")
                f.write(f"    Completed: {'Yes' if task['completed'] else 'No'}\n")
                f.write(f"    Details: {task['details']}\n\n")
        print(f"Report exported to {report_file}.")
        input("Press Enter to continue...")

    def clear_completed(self):
        print("----- Clear Completed Tasks -----")
        original_count = len(self.tasks)
        self.tasks = [t for t in self.tasks if not t["completed"]]
        removed = original_count - len(self.tasks)
        print(f"Removed {removed} completed task(s).")
        self.save_tasks()
        input("Press Enter to continue...")

    def undo_deletion(self):
        print("----- Undo Last Deletion -----")
        if self.last_deleted is None:
            print("No deletion to undo.")
        else:
            index, task = self.last_deleted
            self.tasks.insert(index, task)
            self.save_tasks()
            print("Last deletion undone.")
            self.last_deleted = None
        input("Press Enter to continue...")

    def check_overdue_tasks(self):
        today_str = date.today().strftime("%Y-%m-%d")
        overdue_tasks = [t for t in self.tasks if not t["completed"] and t["date"] < today_str]
        if overdue_tasks:
            print(Fore.RED + "!!! You have overdue tasks:")
            for task in overdue_tasks:
                print(Fore.RED + f" - {task['title']} (Due: {task['date']})")
            input("Press Enter to continue...")

    def load_tasks(self):
        if os.path.exists(TASKS_FILE):
            try:
                with open(TASKS_FILE, "r") as f:
                    self.tasks = json.load(f)
            except Exception:
                self.tasks = []
        else:
            self.tasks = []

    def save_tasks(self):
        with open(TASKS_FILE, "w") as f:
            json.dump(self.tasks, f, indent=4)

    def run(self):
        while True:
            self.clear_screen()
            self.show_menu()
            choice = input("Select an option: ").strip()
            if choice == "1":
                self.add_task()
            elif choice == "2":
                self.edit_task()
            elif choice == "3":
                self.delete_task()
            elif choice == "4":
                self.mark_completed()
            elif choice == "5":
                self.view_details()
            elif choice == "6":
                self.ai_assistant()
            elif choice == "7":
                self.sort_tasks()
            elif choice == "8":
                self.filter_tasks()
            elif choice == "9":
                self.dashboard()
            elif choice == "10":
                self.export_report()
            elif choice == "11":
                self.clear_completed()
            elif choice == "12":
                self.undo_deletion()
            elif choice == "13":
                self.save_tasks()
                print("Goodbye!")
                break
            else:
                print("Invalid option.")
                input("Press Enter to continue...")

if __name__ == "__main__":
    username = get_username()
    tm = TaskManager(username)
    tm.run()
