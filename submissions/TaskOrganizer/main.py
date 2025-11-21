from rich.console import Console
from datetime import datetime, timedelta
import re
import keyboard
import os
import json
import sys

IS_LINUX = os.name == 'posix'
if IS_LINUX:
    import tty
    import termios

def parse_duration(duration_str):
    duration_str = duration_str.strip().lower()
    hours = 0
    minutes = 0
    matches = re.findall(r"(\d+)\s*h", duration_str)
    if matches:
        hours = int(matches[0])
    matches = re.findall(r"(\d+)\s*m", duration_str)
    if matches:
        minutes = int(matches[0])
    return timedelta(hours=hours, minutes=minutes)

def get_task_heights(tasks, max_lines=24, min_height=1):
    durations = [max(1, int(parse_duration(t['duration']).total_seconds() // 600)) for t in tasks]
    total = sum(durations)
    if total <= max_lines:
        return durations
    # Scale down proportionally
    scaled = [max(min_height, int(d / total * max_lines)) for d in durations]
    # Ensure at least min_height for each, and adjust to fit exactly max_lines
    while sum(scaled) > max_lines:
        for i in range(len(scaled)):
            if scaled[i] > min_height:
                scaled[i] -= 1
                if sum(scaled) == max_lines:
                    break
    while sum(scaled) < max_lines:
        for i in range(len(scaled)):
            scaled[i] += 1
            if sum(scaled) == max_lines:
                break
    return scaled

def render_ascii_schedule(tasks):
    current_time = datetime.now()
    lines = []
    heights = get_task_heights(tasks)
    for idx, task in enumerate(tasks):
        start_str = current_time.strftime('%H:%M')
        duration_td = parse_duration(task['duration'])
        finish_time = current_time + duration_td
        finish_str = finish_time.strftime('%H:%M')
        height = heights[idx]
        block_lines = []
        for i in range(height):
            if i == 0:
                time_label = f"{start_str} - {finish_str}"
            else:
                time_label = " " * len(f"{start_str} - {finish_str}")
            if i == height // 2:
                content = f"{task['name']} ({task['duration']})"
            else:
                content = ""
            block_lines.append(f"{time_label:<15} | {content:<30}")
        lines.extend(block_lines)
        current_time = finish_time
    return lines

def display_tasks_with_cursor(tasks, cursor_idx, moving_idx=None):
    os.system('cls' if os.name == 'nt' else 'clear')
    console = Console()
    console.print("[bold yellow]Reorder Your Tasks[/bold yellow]\n")
    lines = []
    current_time = datetime.now()
    heights = get_task_heights(tasks)
    for idx, task in enumerate(tasks):
        start_str = current_time.strftime('%H:%M')
        duration_td = parse_duration(task['duration'])
        finish_time = current_time + duration_td
        finish_str = finish_time.strftime('%H:%M')
        height = heights[idx]
        block_lines = []
        for i in range(height):
            if i == 0:
                time_label = f"{start_str} - {finish_str}"
            else:
                time_label = " " * len(f"{start_str} - {finish_str}")
            if i == height // 2:
                content = f"{task['name']} ({task['duration']})"
            else:
                content = ""
            block_lines.append((time_label, content))
        style = "on blue" if idx == cursor_idx else ("on green" if moving_idx is not None and idx == moving_idx else "")
        for time_label, content in block_lines:
            if style:
                lines.append(f"[{style}]{time_label:<15} | {content:<30}[/{style}]")
            else:
                lines.append(f"{time_label:<15} | {content:<30}")
        current_time = finish_time
    for line in lines:
        console.print(line)
    if moving_idx is not None:
        console.print("\n[bold magenta]Use arrow keys to move the task. Press space to drop.[/bold magenta]")
    else:
        console.print("\n[bold magenta]Use arrow keys to move the cursor. Press space to pick up a task.[/bold magenta]")
    console.print("[bold magenta]Press 'a' to add a new task, 'e' to edit the selected task.[/bold magenta]")
    console.print("[bold magenta]Press Esc to end and save your schedule.[/bold magenta]")

def is_valid_duration(duration_str):
    duration_str = duration_str.strip().lower()
    # Accepts formats like '1h', '30m', '1h30m', '2h 15m', etc.
    return bool(re.fullmatch(r"(\d+\s*h)?\s*(\d+\s*m)?", duration_str)) and (re.search(r"\d", duration_str) is not None)

def get_key_linux():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':  # possible arrow key
            ch2 = sys.stdin.read(1)
            if ch2 == '[':
                ch3 = sys.stdin.read(1)
                if ch3 == 'A':
                    return 'up'
                elif ch3 == 'B':
                    return 'down'
            return 'esc'
        elif ch == ' ':  # space
            return 'space'
        elif ch == 'a':
            return 'a'
        elif ch == 'e':
            return 'e'
        elif ch == '\x1b':
            return 'esc'
        else:
            return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def reorder_tasks(tasks):
    cursor_idx = 0
    moving = False
    moving_idx = None
    console = Console()
    while True:
        display_tasks_with_cursor(tasks, cursor_idx, moving_idx)
        if IS_LINUX:
            key = get_key_linux()
            event_name = key
        else:
            event = keyboard.read_event(suppress=(os.name != 'posix'))
            if event.event_type != 'down':
                continue
            event_name = event.name
        if event_name == 'esc':
            break
        if event_name == 'a':
            console.print("\n[bold yellow]Add a new task[/bold yellow]")
            name = console.input("[green]Enter task name: [/green]")
            while True:
                duration = console.input("[yellow]Enter task duration (e.g., 30m, 1h): [/yellow]")
                if is_valid_duration(duration):
                    break
                console.print("[red]Invalid duration format. Please try again (e.g., 30m, 1h, 1h30m).[/red]")
            tasks.append({'name': name, 'duration': duration})
            cursor_idx = len(tasks) - 1
            continue
        if event_name == 'e' and tasks:
            console.print(f"\n[bold yellow]Edit task: {tasks[cursor_idx]['name']} ({tasks[cursor_idx]['duration']})[/bold yellow]")
            new_name = console.input(f"[green]Enter new name (leave blank to keep '{tasks[cursor_idx]['name']}'): [/green]")
            while True:
                new_duration = console.input(f"[yellow]Enter new duration (leave blank to keep '{tasks[cursor_idx]['duration']}'): [/yellow]")
                if not new_duration.strip() or is_valid_duration(new_duration):
                    break
                console.print("[red]Invalid duration format. Please try again (e.g., 30m, 1h, 1h30m).[/red]")
            if new_name.strip():
                tasks[cursor_idx]['name'] = new_name
            if new_duration.strip():
                tasks[cursor_idx]['duration'] = new_duration
            continue
        if not moving:
            if event_name == 'down':
                cursor_idx = min(len(tasks) - 1, cursor_idx + 1)
            elif event_name == 'up':
                cursor_idx = max(0, cursor_idx - 1)
            elif event_name == 'space':
                moving = True
                moving_idx = cursor_idx
        else:
            if event_name == 'down' and moving_idx < len(tasks) - 1:
                tasks[moving_idx], tasks[moving_idx + 1] = tasks[moving_idx + 1], tasks[moving_idx]
                moving_idx += 1
            elif event_name == 'up' and moving_idx > 0:
                tasks[moving_idx], tasks[moving_idx - 1] = tasks[moving_idx - 1], tasks[moving_idx]
                moving_idx -= 1
            elif event_name == 'space':
                cursor_idx = moving_idx
                moving = False
                moving_idx = None
    return tasks

def main():
    console = Console()
    tasks = []
    # Check for existing schedule.json
    if os.path.exists("schedule.json"):
        console.print("[bold yellow]A saved schedule was found.[/bold yellow]")
        choice = console.input("[cyan]Continue with existing schedule? (y/n): [/cyan]").strip().lower()
        if choice == 'y':
            with open("schedule.json", "r", encoding="utf-8") as f:
                tasks = json.load(f)
        else:
            console.print("[italic]Starting with a new schedule.[/italic]")
            os.remove("schedule.json")
    if not tasks:
        while True:
            name = console.input("[green]Enter task name (or type 'done' to finish): [/green]")
            if name.lower() == 'done':
                break
            while True:
                duration = console.input("[yellow]Enter task duration (e.g., 30m, 1h): [/yellow]")
                if is_valid_duration(duration):
                    break
                console.print("[red]Invalid duration format. Please try again (e.g., 30m, 1h, 1h30m).[/red]")
            tasks.append({'name': name, 'duration': duration})
            console.print(f"[bold green]Task '{name}' with duration '{duration}' added.[/bold green]\n")
    if tasks:
        reorder_tasks(tasks)
        # After reordering, print the final ascii schedule and write to file
        ascii_lines = render_ascii_schedule(tasks)
        console.print("\n[bold green]Final Schedule:[/bold green]")
        for line in ascii_lines:
            console.print(line)
        with open("schedule.txt", "w", encoding="utf-8") as f:
            for line in ascii_lines:
                f.write(line + "\n")
        console.print("\n[bold cyan]Schedule written to schedule.txt[/bold cyan]")
        # Ask to save as JSON
        save_json = console.input("\n[cyan]Save this schedule? (y/n): [/cyan]").strip().lower()
        if save_json == 'y':
            with open("schedule.json", "w", encoding="utf-8") as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)
            console.print("[bold green]Schedule saved[/bold green]")
    else:
        console.print("[italic]No tasks added.[/italic]")
    console.print("\n[bold cyan]Thank you for using Task Organizer![/bold cyan]")

if __name__ == "__main__":
    main()
