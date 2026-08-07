# Viewer UI for StandLog CLI
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box
from datetime import datetime
import os
import json
from cryptography.fernet import Fernet, InvalidToken
import base64
import getpass
import subprocess
import glob
from datetime import timedelta
try:
    import ics
except ImportError:
    ics = None
import platform
import shutil

BADGES_PATH = os.path.expanduser("~/.standlog/badges.json")
DATA_DIR = os.path.expanduser("~/.standlog/entries")
ENCRYPTION_KEY_PATH = os.path.expanduser("~/.standlog/.key")
console = Console()

# Helper to load/save badges

def load_badges():
    if not os.path.exists(BADGES_PATH):
        return {}
    with open(BADGES_PATH) as f:
        return json.load(f)

def save_badges(badges):
    with open(BADGES_PATH, "w") as f:
        json.dump(badges, f, indent=2)

def award_badge(badge):
    badges = load_badges()
    if badge not in badges:
        badges[badge] = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_badges(badges)
        console.print(f"[bold yellow]🏅 Achievement unlocked: {badge}![/bold yellow]")

def show_badges():
    badges = load_badges()
    if not badges:
        return
    badge_lines = [f"🏅 [green]{b}[/green] ([dim]{badges[b]}[/dim])" for b in badges]
    console.print(Panel("\n".join(badge_lines), title="Achievements & Badges", style="bold magenta", expand=False))

def list_entry_files():
    if not os.path.exists(DATA_DIR):
        return []
    return sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.json')])


def get_fernet():
    if not os.path.exists(ENCRYPTION_KEY_PATH):
        return None
    with open(ENCRYPTION_KEY_PATH, "rb") as f:
        key = f.read()
    return Fernet(key)


def set_encryption():
    passphrase = getpass.getpass("Set a passphrase for encryption: ")
    key = base64.urlsafe_b64encode(passphrase.encode().ljust(32, b'0'))
    with open(ENCRYPTION_KEY_PATH, "wb") as f:
        f.write(key)
    console.print("[green]Encryption enabled![/green]")


def unset_encryption():
    if os.path.exists(ENCRYPTION_KEY_PATH):
        os.remove(ENCRYPTION_KEY_PATH)
        console.print("[yellow]Encryption disabled.[/yellow]")
    else:
        console.print("[yellow]Encryption was not enabled.[/yellow]")


def encrypt_data(data):
    f = get_fernet()
    if not f:
        return data.encode()
    return f.encrypt(data.encode())


def decrypt_data(data):
    f = get_fernet()
    if not f:
        return data.decode()
    try:
        return f.decrypt(data).decode()
    except InvalidToken:
        console.print("[red]Invalid passphrase or corrupted data![/red]")
        return "[decryption failed]"


def load_entry(filename):
    try:
        path = os.path.join(DATA_DIR, filename)
        with open(path, "rb") as f:
            raw = f.read()
        try:
            # Try to decode as utf-8 (plain)
            return json.loads(raw.decode())
        except Exception:
            # Try to decrypt
            text = decrypt_data(raw)
            return json.loads(text)
    except Exception as e:
        console.print(f"[red]Error loading {filename}: {e}[/red]")
        return None


def save_entry(filename, entry):
    path = os.path.join(DATA_DIR, filename)
    data = json.dumps(entry, indent=2)
    enc = encrypt_data(data)
    with open(path, "wb") as f:
        f.write(enc)


def feedback_path(entry_file):
    return os.path.join(DATA_DIR, entry_file.replace('.json', '.feedbacks.json'))


def leave_feedback(entry_file):
    fb_path = feedback_path(entry_file)
    feedback = Prompt.ask("Enter your feedback (or encouragement)")
    user = Prompt.ask("Your name (optional)", default="Anonymous")
    fb_entry = {"user": user, "feedback": feedback, "time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    feedbacks = []
    if os.path.exists(fb_path):
        with open(fb_path, "rb") as f:
            raw = f.read()
        try:
            feedbacks = json.loads(raw.decode())
        except Exception:
            text = decrypt_data(raw)
            feedbacks = json.loads(text)
    feedbacks.append(fb_entry)
    enc = encrypt_data(json.dumps(feedbacks, indent=2))
    with open(fb_path, "wb") as f:
        f.write(enc)
    console.print("[green]Feedback added![/green]")
    award_badge("Feedback Given")


def view_feedback(entry_file):
    fb_path = feedback_path(entry_file)
    if not os.path.exists(fb_path):
        console.print("[yellow]No feedback yet for this entry.[/yellow]")
        return
    with open(fb_path, "rb") as f:
        raw = f.read()
    try:
        feedbacks = json.loads(raw.decode())
    except Exception:
        text = decrypt_data(raw)
        feedbacks = json.loads(text)
    table = Table(title=f"Feedback for {entry_file.replace('.json','')}", box=box.SIMPLE)
    table.add_column("User", style="cyan")
    table.add_column("Feedback", style="magenta")
    table.add_column("Time", style="dim")
    for fb in feedbacks:
        table.add_row(fb.get("user","?"), fb.get("feedback",""), fb.get("time",""))
    console.print(table)
    if feedbacks:
        award_badge("Feedback Received")


def show_weekly_stats():
    files = list_entry_files()
    last_7 = files[-7:]
    if not last_7:
        console.print("[red]No logs found for the past week.[/red]")
        return
    table = Table(title="Weekly StandLog Stats", box=box.ROUNDED)
    table.add_column("Date", style="cyan")
    table.add_column("Did", style="green")
    table.add_column("Blockers", style="red")
    blockers_count = {}
    streak = 0
    prev_date = None
    for fname in last_7:
        entry = load_entry(fname)
        if not entry:
            continue
        date = fname.replace('.json', '')
        table.add_row(date, entry['did'][:20], entry['blockers'][:20])
        if entry['blockers']:
            for word in entry['blockers'].split():
                blockers_count[word] = blockers_count.get(word, 0) + 1
        # Streak calculation
        d = datetime.strptime(date, "%Y-%m-%d")
        if prev_date is None or (d - prev_date).days == 1:
            streak += 1
        else:
            streak = 1
        prev_date = d
    console.print(table)
    if blockers_count:
        common = max(blockers_count, key=blockers_count.get)
        console.print(f"[bold yellow]Most common blocker:[/bold yellow] {common}")
    console.print(f"[bold green]Logging streak:[/bold green] {streak} days")


def export_logs(fmt="md"):
    files = list_entry_files()
    if not files:
        console.print("[red]No logs to export.[/red]")
        return
    if fmt == "md":
        out = "# StandLog Journal\n\n"
        for fname in files:
            entry = load_entry(fname)
            if not entry:
                continue
            out += f"## {fname.replace('.json', '')}\n- **Did:** {entry['did']}\n- **Will do:** {entry['will_do']}\n- **Blockers:** {entry['blockers']}\n- **Tags:** {', '.join(entry['tags']) if entry['tags'] else '-'}\n\n"
        md_path = os.path.expanduser("~/.standlog/journal.md")
        os.makedirs(os.path.dirname(md_path), exist_ok=True)
        with open(md_path, "w") as f:
            f.write(out)
        console.print(f"[green]Exported to {md_path}[/green]")
    elif fmt == "json":
        all_entries = [load_entry(f) for f in files if load_entry(f)]
        json_path = os.path.expanduser("~/.standlog/journal.json")
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, "w") as f:
            json.dump(all_entries, f, indent=2)
        console.print(f"[green]Exported to {json_path}[/green]")


def reminder():
    today = datetime.now().strftime("%Y-%m-%d")
    today_path = os.path.join(DATA_DIR, f"{today}.json")
    already_logged = os.path.exists(today_path)
    context_msgs = []
    # Calendar event check (local .ics file)
    ics_files = glob.glob(os.path.expanduser("~/*.ics"))
    if ics is None:
        context_msgs.append("[red]Install the 'ics' package for calendar-based reminders: pip install ics[/red]")
    elif ics_files:
        for ics_file in ics_files:
            try:
                with open(ics_file) as f:
                    cal = ics.Calendar(f.read())
                for event in cal.timeline.today():
                    context_msgs.append(f"You had a calendar event today: {event.name}")
            except Exception:
                pass
    # Git activity check (commits today) - only if git is available
    if shutil.which("git"):
        try:
            git_dir = os.path.expanduser("~")
            result = subprocess.run([
                "git", "--no-pager", "log", "--since=midnight", "--pretty=oneline"
            ], cwd=git_dir, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                context_msgs.append("You made git commits today!")
        except Exception:
            pass
    # System usage check (uptime > 2h today) - only if uptime is available and not on Windows
    if shutil.which("uptime") and platform.system() != "Windows":
        try:
            uptime = subprocess.check_output(["uptime", "-p"]).decode()
            if "hour" in uptime or "hours" in uptime:
                context_msgs.append(f"You've been active for: {uptime.strip()}")
        except Exception:
            pass
    if not already_logged:
        if context_msgs:
            console.print("[bold blink yellow]Context-Aware Reminder:[/bold blink yellow]")
            for msg in context_msgs:
                console.print(f"[cyan]- {msg}[/cyan]")
            console.print("[bold blink red]Don't forget to log your day![/bold blink red]")
        else:
            console.print("[bold blink red]Reminder: Don't forget to log your day![/bold blink red]")
    else:
        console.print("[green]You have already logged today![green]")


def show_heatmap():
    files = list_entry_files()
    if not files:
        console.print("[red]No logs to visualize.[/red]")
        return
    from collections import defaultdict
    from rich.text import Text
    from rich.columns import Columns
    from datetime import date as dtdate
    import calendar
    year = datetime.now().year
    log_days = defaultdict(int)
    for fname in files:
        date = fname.replace('.json', '')
        log_days[date] += 1
    # Calculate streaks
    all_dates = sorted(log_days.keys())
    streak = 0
    max_streak = 0
    prev = None
    for d in all_dates:
        d_obj = datetime.strptime(d, "%Y-%m-%d")
        if prev and (d_obj - prev).days == 1:
            streak += 1
        else:
            streak = 1
        if streak > max_streak:
            max_streak = streak
        prev = d_obj
    # Color gradient: 1 log = green, 2 = yellow, 3+ = red, no log = grey
    months = []
    for month in range(1, 13):
        cal = calendar.monthcalendar(year, month)
        month_name = calendar.month_abbr[month]
        lines = [f"[bold]{month_name}[/bold]"]
        for week in cal:
            week_str = ""
            for day in week:
                if day == 0:
                    week_str += "   "
                else:
                    dstr = f"{year}-{month:02d}-{day:02d}"
                    count = log_days.get(dstr, 0)
                    if count == 0:
                        week_str += "[grey]·[/grey] "
                    elif count == 1:
                        week_str += "[color(46)]■[/color(46)] "  # green
                    elif count == 2:
                        week_str += "[color(226)]■[/color(226)] "  # yellow
                    else:
                        week_str += "[color(196)]■[/color(196)] "  # red
            lines.append(week_str)
        months.append(Text("\n".join(lines)))
    legend = Text("[color(46)]■[/color(46)] 1 log  [color(226)]■[/color(226)] 2 logs  [color(196)]■[/color(196)] 3+ logs  [grey]·[/grey] no log", justify="center")
    stats = f"[cyan]Total logs:[/cyan] {len(files)}   [cyan]Longest streak:[/cyan] {max_streak} days"
    console.print(Panel(Columns(months, equal=True, expand=True), title="Journal Activity Heatmap", expand=True))
    console.print(legend)
    console.print(stats)


def viewer_menu():
    while True:
        console.print("\n[bold cyan]StandLog Viewer[/bold cyan]")
        console.print("[1] Show weekly stats\n[2] Export as Markdown\n[3] Export as JSON\n[4] Reminder\n[5] Leave feedback\n[6] View feedback\n[7] Enable encryption\n[8] Disable encryption\n[9] Visualize journal (heatmap)\n[10] Back")
        choice = Prompt.ask("Choose an option", choices=[str(i) for i in range(1,11)], default="1")
        if choice == "1":
            show_weekly_stats()
        elif choice == "2":
            export_logs("md")
        elif choice == "3":
            export_logs("json")
        elif choice == "4":
            reminder()
        elif choice == "5":
            files = list_entry_files()
            if not files:
                console.print("[red]No entries to leave feedback on.[/red]")
                continue
            for idx, fname in enumerate(files):
                console.print(f"[{idx+1}] {fname}")
            idx = Prompt.ask("Select entry number", choices=[str(i+1) for i in range(len(files))])
            leave_feedback(files[int(idx)-1])
        elif choice == "6":
            files = list_entry_files()
            if not files:
                console.print("[red]No entries to view feedback for.[/red]")
                continue
            for idx, fname in enumerate(files):
                console.print(f"[{idx+1}] {fname}")
            idx = Prompt.ask("Select entry number", choices=[str(i+1) for i in range(len(files))])
            view_feedback(files[int(idx)-1])
        elif choice == "7":
            set_encryption()
        elif choice == "8":
            unset_encryption()
        elif choice == "9":
            show_heatmap()
        elif choice == "10":
            break
