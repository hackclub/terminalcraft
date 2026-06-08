# StandLog CLI - All-in-one
from ui.viewer import viewer_menu, reminder
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from datetime import datetime
import os
import json
import yagmail
import sounddevice as sd
from scipy.io.wavfile import write, read as wavread
import tempfile
import shutil
import re
from collections import defaultdict

DATA_DIR = os.path.expanduser("~/.standlog/entries")
GOALS_PATH = os.path.expanduser("~/.standlog/goals.json")
BADGES_PATH = os.path.expanduser("~/.standlog/badges.json")
EMAIL_CONFIG_PATH = os.path.expanduser("~/.standlog/email.json")
VOICE_DIR = os.path.expanduser("~/.standlog/voice_notes")
AUTOMATION_RULES_PATH = os.path.expanduser("~/.standlog/automation_rules.json")
os.makedirs(VOICE_DIR, exist_ok=True)
console = Console()


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def get_today_path():
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(DATA_DIR, f"{today}.json")


def multiline_input(prompt):
    panel = Panel(f"{prompt}\n(Press Enter twice to finish)", style="bold white on black", expand=False)
    console.print(panel)
    lines = []
    while True:
        line = input()
        if line == "":
            if lines:
                break
        lines.append(line)
    return "\n".join(lines)


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


def record_voice_note():
    fs = 44100  # Sample rate
    try:
        devices = sd.query_devices()
        input_devices = [d for d in devices if d.get('max_input_channels', 0) > 0]
        if not input_devices:
            console.print("[yellow]No input device (microphone) found. Cannot record voice note.[/yellow]")
            return None
    except Exception as e:
        console.print(f"[yellow]Could not query audio devices: {e}. Cannot record voice note.[/yellow]")
        return None
    seconds = Prompt.ask("Record for how many seconds?", default="10")
    try:
        seconds = int(seconds)
    except Exception:
        seconds = 10
    console.print(f"[cyan]Recording for {seconds} seconds... Speak now![/cyan]")
    try:
        recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
    except Exception as e:
        console.print(f"[yellow]Audio recording failed: {e}[/yellow]")
        return None
    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    write(tmpfile.name, fs, recording)
    tmpfile.close()
    return tmpfile.name

def save_voice_note_to_log(log_path, wav_path):
    if not os.path.exists(wav_path):
        return None
    dest = os.path.join(VOICE_DIR, os.path.basename(log_path).replace('.json', '.wav'))
    shutil.move(wav_path, dest)
    return dest

def play_voice_note(log_path):
    wav_path = os.path.join(VOICE_DIR, os.path.basename(log_path).replace('.json', '.wav'))
    if not os.path.exists(wav_path):
        console.print("[yellow]No voice note for this log.[/yellow]")
        return
    fs, data = wavread(wav_path)
    console.print("[cyan]Playing voice note...[/cyan]")
    sd.play(data, fs)
    sd.wait()


def log_entry():
    console.print(Panel("[bold cyan]StandLog CLI - Daily Standup[/bold cyan]", expand=False))
    did = multiline_input("What did you work on today?")
    will_do = multiline_input("What will you work on next?")
    blockers = multiline_input("Any blockers?")
    tags = Prompt.ask("[magenta]Tags (comma separated, optional)[/magenta]", default="")
    notes = multiline_input("Any additional notes? (optional)")
    # Time tracking
    time_spent = Prompt.ask("[yellow]Time spent today (in minutes, e.g. 90)[/yellow]", default="0")
    try:
        time_spent = int(time_spent)
    except Exception:
        time_spent = 0
    attach_voice = Prompt.ask("Record a voice note? (y/n)", choices=["y","n"], default="n")
    voice_path = None
    if attach_voice == "y":
        wav_path = record_voice_note()
        voice_path = wav_path
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "did": did,
        "will_do": will_do,
        "blockers": blockers,
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "notes": notes,
        "voice_note": None,
        "time_spent": time_spent
    }
    path = get_today_path()
    is_first_log = not os.path.exists(path)
    with open(path, "w") as f:
        json.dump(entry, f, indent=2)
    if voice_path:
        dest = save_voice_note_to_log(path, voice_path)
        entry["voice_note"] = dest
        with open(path, "w") as f:
            json.dump(entry, f, indent=2)
    console.print("[bold green]Entry saved![/bold green]")
    if is_first_log:
        award_badge("First Log")
    # Streak badge
    import re
    files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.json') and re.match(r'\d{4}-\d{2}-\d{2}\.json$', f)])
    streak = 0
    prev = None
    for fname in files:
        date = fname.replace('.json', '')
        try:
            d_obj = datetime.strptime(date, "%Y-%m-%d")
        except Exception:
            continue
        if prev and (d_obj - prev).days == 1:
            streak += 1
        else:
            streak = 1
        prev = d_obj
    if streak >= 3:
        award_badge(f"{streak}-Day Streak")


def view_entry():
    path = get_today_path()
    if not os.path.exists(path):
        console.print("[red]No entry for today yet.[/red]")
        return
    with open(path) as f:
        entry = json.load(f)
    panel = Panel(f"[b]What I did:[/b] {entry['did']}\n[b]What I'll do:[/b] {entry['will_do']}\n[b]Blockers:[/b] {entry['blockers']}\n[b]Tags:[/b] {', '.join(entry['tags']) if entry['tags'] else '-'}\n[b]Notes:[/b] {entry.get('notes','-')}\n[b]Date:[/b] {entry['date']}", title="Today's Log", expand=False)
    console.print(panel)
    if entry.get("voice_note") or os.path.exists(os.path.join(VOICE_DIR, os.path.basename(path).replace('.json', '.wav'))):
        play = Prompt.ask("Play attached voice note? (y/n)", choices=["y","n"], default="n")
        if play == "y":
            play_voice_note(path)


def set_weekly_goals():
    console.print(Panel("[bold yellow]Set your goals for this week! (Enter one per line, Enter twice to finish)[/bold yellow]", expand=False))
    goals = []
    while True:
        line = input()
        if line == "":
            if goals:
                break
        goals.append({"goal": line, "done": False})
    with open(GOALS_PATH, "w") as f:
        json.dump(goals, f, indent=2)
    console.print("[green]Goals saved![/green]")


def mark_goal_progress():
    if not os.path.exists(GOALS_PATH):
        console.print("[yellow]No goals set for this week.[/yellow]")
        return
    with open(GOALS_PATH) as f:
        goals = json.load(f)
    if not goals:
        console.print("[yellow]No goals set for this week.[/yellow]")
        return
    console.print("[bold cyan]Your Weekly Goals:[/bold cyan]")
    for idx, g in enumerate(goals):
        status = "[green]✔[/green]" if g["done"] else "[red]✗[/red]"
        console.print(f"[{idx+1}] {g['goal']} {status}")
    idxs = Prompt.ask("Enter goal numbers to mark as done (comma separated)", default="")
    if idxs.strip():
        for i in idxs.split(","):
            try:
                goals[int(i)-1]["done"] = True
            except Exception:
                pass
        with open(GOALS_PATH, "w") as f:
            json.dump(goals, f, indent=2)
        console.print("[green]Progress updated![/green]")


def show_goal_progress():
    if not os.path.exists(GOALS_PATH):
        return
    with open(GOALS_PATH) as f:
        goals = json.load(f)
    if not goals:
        return
    done = sum(1 for g in goals if g["done"])
    total = len(goals)
    percent = int((done/total)*100) if total else 0
    bar = "[green]" + "█"*done + "[/green][white]" + "█"*(total-done) + "[/white]"
    console.print(Panel(f"[bold]Weekly Goals Progress:[/bold]\n{bar} {done}/{total} ({percent}%)", style="bold blue", expand=False))


def print_ascii_art():
    from rich.text import Text
    from rich.align import Align
    from rich.style import Style
    from rich.panel import Panel
    from rich.console import Group
    import time
    art_lines = [
        ("   _____ _             _      _                _     _     _ ", "magenta"),
        ("  / ____| |           | |    | |              | |   | |   | |", "blue"),
        (" | (___ | |_ __ _ _ __| | __ | |     ___   ___| | __| | __| |", "cyan"),
        ("  \\___ \\| __/ _` | '__| |/ / | |    / _ \\ / __| |/ _` |/ _` |", "green"),
        ("  ____) | || (_| | |  |   <  | |___| (_) | (__| | (_| | (_| |", "yellow"),
        (" |_____/ \\__\\__,_|_|  |_|\\_\\ |______\\___/ \\___|_|\\__,_|\\__,_|", "red")
    ]
    art = "\n".join([f"[bold {color}]{line}[/bold {color}]" for line, color in art_lines])
    # Colorful square ASCII clock
    from datetime import datetime
    now = datetime.now()
    date_str = now.strftime("%A, %d %B %Y")
    time_str = now.strftime("%H:%M:%S")
    clock_art = f"""
[bold white]┌───────────────┐
│   [cyan]{time_str}[/cyan]   │
│ [yellow]{date_str}[/yellow] │
└───────────────┘[/bold white]
"""
    # Footer
    footer = Align.center("[dim]made with :heart: by dev for dev[/dim]", style="bold magenta")
    # Group all together
    group = Group(
        Align.center(Text.from_markup(art)),
        Align.center(Text.from_markup(clock_art)),
        Align.center("[bold cyan]Welcome to StandLog CLI![/bold cyan] :notebook_with_decorative_cover: :sparkles:"),
        Align.center("[dim]Your beautiful terminal developer journal[/dim]"),
        footer,
        Text("\n")
    )
    console.print(group)


def search_logs():
    files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.json')])
    if not files:
        console.print("[red]No logs to search.[/red]")
        return
    console.print(Panel("[bold cyan]Search Logs[/bold cyan]", expand=False))
    mode = Prompt.ask("Search by", choices=["keyword", "tag", "date"], default="keyword")
    results = []
    if mode == "keyword":
        kw = Prompt.ask("Enter keyword").lower()
        for fname in files:
            with open(os.path.join(DATA_DIR, fname)) as f:
                entry = json.load(f)
            if not isinstance(entry, dict):
                continue
            if (kw in entry.get("did", "").lower() or
                kw in entry.get("will_do", "").lower() or
                kw in entry.get("blockers", "").lower() or
                kw in entry.get("notes", "").lower()):
                results.append((fname, entry))
    elif mode == "tag":
        tag = Prompt.ask("Enter tag").lower()
        for fname in files:
            with open(os.path.join(DATA_DIR, fname)) as f:
                entry = json.load(f)
            if not isinstance(entry, dict):
                continue
            tags = [t.lower() for t in entry.get("tags", [])]
            if tag in tags:
                results.append((fname, entry))
    elif mode == "date":
        start = Prompt.ask("Start date (YYYY-MM-DD)", default=files[0].replace('.json',''))
        end = Prompt.ask("End date (YYYY-MM-DD)", default=files[-1].replace('.json',''))
        for fname in files:
            date = fname.replace('.json','')
            with open(os.path.join(DATA_DIR, fname)) as f:
                entry = json.load(f)
            if not isinstance(entry, dict):
                continue
            if start <= date <= end:
                results.append((fname, entry))
    if not results:
        console.print("[yellow]No matching logs found.[/yellow]")
        return
    for fname, entry in results:
        panel = Panel(f"[b]Date:[/b] {entry['date']}\n[b]What I did:[/b] {entry['did']}\n[b]What I'll do:[/b] {entry['will_do']}\n[b]Blockers:[/b] {entry['blockers']}\n[b]Tags:[/b] {', '.join(entry['tags']) if entry['tags'] else '-'}\n[b]Notes:[/b] {entry.get('notes','-')}", title=f"Log: {fname.replace('.json','')}", expand=False)
        console.print(panel)


def setup_email():
    console.print(Panel("[bold yellow]Setup Email Export[/bold yellow]", expand=False))
    user = Prompt.ask("Enter your Gmail address")
    password = Prompt.ask("Enter your Gmail app password (see README)", password=True)
    to = Prompt.ask("Enter recipient email (yourself or team)", default=user)
    config = {"user": user, "password": password, "to": to}
    with open(EMAIL_CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    console.print("[green]Email config saved![/green]")


def email_weekly_logs():
    if not os.path.exists(EMAIL_CONFIG_PATH):
        console.print("[yellow]No email config found. Please run setup first.[/yellow]")
        setup_email()
    with open(EMAIL_CONFIG_PATH) as f:
        config = json.load(f)
    files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.json')])
    if not files:
        console.print("[red]No logs to email.[/red]")
        return
    # Get last 7 days
    from datetime import timedelta
    today = datetime.now().date()
    week_files = []
    for fname in files:
        try:
            d = datetime.strptime(fname.replace('.json',''), "%Y-%m-%d").date()
            if (today - d).days < 7:
                week_files.append(fname)
        except Exception:
            continue
    if not week_files:
        console.print("[yellow]No logs from the past week.[/yellow]")
        return
    week_files.sort()
    body = "# StandLog Weekly Report\n\n"
    for fname in week_files:
        with open(os.path.join(DATA_DIR, fname)) as f:
            entry = json.load(f)
        body += f"## {fname.replace('.json', '')}\n- **Did:** {entry['did']}\n- **Will do:** {entry['will_do']}\n- **Blockers:** {entry['blockers']}\n- **Tags:** {', '.join(entry['tags']) if entry['tags'] else '-'}\n- **Notes:** {entry.get('notes','-')}\n\n"
    yag = yagmail.SMTP(config['user'], config['password'])
    yag.send(config['to'], "StandLog Weekly Report", body)
    console.print(f"[green]Weekly logs emailed to {config['to']}![/green]")


# --- Automation Rules Engine ---
def load_automation_rules():
    if not os.path.exists(AUTOMATION_RULES_PATH):
        return []
    with open(AUTOMATION_RULES_PATH) as f:
        try:
            return json.load(f)
        except Exception:
            return []

def save_automation_rules(rules):
    with open(AUTOMATION_RULES_PATH, "w") as f:
        json.dump(rules, f, indent=2)

def automation_rules_menu():
    while True:
        console.print("\n[bold cyan]Automation Rules[/bold cyan]")
        console.print("[1] List rules\n[2] Add rule\n[3] Remove rule\n[4] Back")
        choice = Prompt.ask("Choose an option", choices=["1","2","3","4"], default="1")
        rules = load_automation_rules()
        if choice == "1":
            if not rules:
                console.print("[yellow]No automation rules defined.[/yellow]")
            for idx, rule in enumerate(rules):
                console.print(f"[{idx+1}] IF {rule['if']} THEN {rule['then']}")
        elif choice == "2":
            trigger = Prompt.ask("Enter trigger (calendar_event, git_commit, uptime, time_of_day)")
            action = Prompt.ask("Enter action (remind, auto_log, email)")
            value = Prompt.ask("Optional: value for trigger (e.g. 18:00 for time_of_day)", default="")
            rules.append({"if": trigger, "then": action, "value": value})
            save_automation_rules(rules)
            console.print("[green]Rule added![/green]")
        elif choice == "3":
            if not rules:
                console.print("[yellow]No rules to remove.[/yellow]")
                continue
            for idx, rule in enumerate(rules):
                console.print(f"[{idx+1}] IF {rule['if']} THEN {rule['then']}")
            idx = Prompt.ask("Enter rule number to remove", choices=[str(i+1) for i in range(len(rules))])
            del rules[int(idx)-1]
            save_automation_rules(rules)
            console.print("[green]Rule removed![/green]")
        elif choice == "4":
            break

def evaluate_automation_rules(context):
    rules = load_automation_rules()
    actions = []
    now = datetime.now()
    for rule in rules:
        trig = rule.get('if')
        val = rule.get('value','')
        if trig == 'calendar_event' and context.get('calendar_event'):
            actions.append(rule['then'])
        elif trig == 'git_commit' and context.get('git_commit'):
            actions.append(rule['then'])
        elif trig == 'uptime' and context.get('uptime'):
            actions.append(rule['then'])
        elif trig == 'time_of_day' and val:
            try:
                h, m = map(int, val.split(":"))
                if now.hour == h and abs(now.minute - m) < 10:
                    actions.append(rule['then'])
            except Exception:
                pass
    return actions


def build_contextual_links():
    """
    Scan all logs and goals, auto-link related logs (by tags/keywords/date),
    link logs to goals if goal keywords appear in log, and feedback to logs.
    Store links in each log file as a 'links' field.
    """
    # Load all logs
    logs = {}
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json') and re.match(r'\d{4}-\d{2}-\d{2}\.json$', f)]
    for fname in files:
        with open(os.path.join(DATA_DIR, fname)) as f:
            try:
                logs[fname] = json.load(f)
            except Exception:
                continue
    # Load goals
    goals = []
    if os.path.exists(GOALS_PATH):
        with open(GOALS_PATH) as f:
            try:
                goals = json.load(f)
            except Exception:
                goals = []
    # Build links
    tag_map = defaultdict(list)
    for fname, entry in logs.items():
        for tag in entry.get('tags', []):
            tag_map[tag.lower()].append(fname)
    # Link logs by shared tags
    for fname, entry in logs.items():
        links = set()
        for tag in entry.get('tags', []):
            for other in tag_map[tag.lower()]:
                if other != fname:
                    links.add(other)
        # Link to goals if goal keywords appear in log fields
        goal_links = []
        for idx, goal in enumerate(goals):
            goal_kw = goal['goal'].lower()
            if (goal_kw in entry.get('did', '').lower() or
                goal_kw in entry.get('will_do', '').lower() or
                goal_kw in entry.get('notes', '').lower()):
                goal_links.append(idx)
        # Feedback links (if feedback is stored in log)
        feedback_links = []
        if 'feedback' in entry:
            feedback_links.append(fname + ':feedback')
        # Save links
        entry['links'] = {
            'related_logs': sorted(list(links)),
            'goals': goal_links,
            'feedback': feedback_links
        }
        with open(os.path.join(DATA_DIR, fname), 'w') as f:
            json.dump(entry, f, indent=2)

def render_knowledge_graph():
    """
    Render a simple ASCII/text knowledge graph of logs, goals, and feedback links.
    """
    # Load logs and goals
    logs = {}
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json') and re.match(r'\d{4}-\d{2}-\d{2}\.json$', f)]
    for fname in files:
        with open(os.path.join(DATA_DIR, fname)) as f:
            try:
                logs[fname] = json.load(f)
            except Exception:
                continue
    goals = []
    if os.path.exists(GOALS_PATH):
        with open(GOALS_PATH) as f:
            try:
                goals = json.load(f)
            except Exception:
                goals = []
    # Build nodes and edges
    nodes = []
    edges = []
    for fname, entry in logs.items():
        nodes.append(f"[log] {fname.replace('.json','')}")
        for rel in entry.get('links', {}).get('related_logs', []):
            edges.append((f"[log] {fname.replace('.json','')}", f"[log] {rel.replace('.json','')}", 'tag'))
        for goal_idx in entry.get('links', {}).get('goals', []):
            if goal_idx < len(goals):
                edges.append((f"[log] {fname.replace('.json','')}", f"[goal] {goals[goal_idx]['goal']}", 'goal'))
        for fb in entry.get('links', {}).get('feedback', []):
            edges.append((f"[log] {fname.replace('.json','')}", f"[feedback] {fname.replace('.json','')}", 'feedback'))
    for idx, goal in enumerate(goals):
        nodes.append(f"[goal] {goal['goal']}")
    # Render as ASCII graph (simple indented tree)
    console.print(Panel("[bold magenta]StandLog Knowledge Graph[/bold magenta]", expand=False))
    for node in nodes:
        console.print(f"[bold]{node}[/bold]")
        for edge in edges:
            if edge[0] == node:
                if edge[2] == 'tag':
                    console.print(f"   └─[cyan]related log[/cyan]→ {edge[1]}")
                elif edge[2] == 'goal':
                    console.print(f"   └─[green]linked goal[/green]→ {edge[1]}")
                elif edge[2] == 'feedback':
                    console.print(f"   └─[yellow]feedback[/yellow]→ {edge[1]}")


def print_ascii_art():
    from rich.text import Text
    from rich.align import Align
    from rich.style import Style
    from rich.panel import Panel
    from rich.console import Group
    import time
    art_lines = [
        ("   _____ _             _      _                _     _     _ ", "magenta"),
        ("  / ____| |           | |    | |              | |   | |   | |", "blue"),
        (" | (___ | |_ __ _ _ __| | __ | |     ___   ___| | __| | __| |", "cyan"),
        ("  \\___ \\| __/ _` | '__| |/ / | |    / _ \\ / __| |/ _` |/ _` |", "green"),
        ("  ____) | || (_| | |  |   <  | |___| (_) | (__| | (_| | (_| |", "yellow"),
        (" |_____/ \\__\\__,_|_|  |_|\\_\\ |______\\___/ \\___|_|\\__,_|\\__,_|", "red")
    ]
    art = "\n".join([f"[bold {color}]{line}[/bold {color}]" for line, color in art_lines])
    # Colorful square ASCII clock
    from datetime import datetime
    now = datetime.now()
    date_str = now.strftime("%A, %d %B %Y")
    time_str = now.strftime("%H:%M:%S")
    clock_art = f"""
[bold white]┌───────────────┐
│   [cyan]{time_str}[/cyan]   │
│ [yellow]{date_str}[/yellow] │
└───────────────┘[/bold white]
"""
    # Footer
    footer = Align.center("[dim]made with :heart: by dev for dev[/dim]", style="bold magenta")
    # Group all together
    group = Group(
        Align.center(Text.from_markup(art)),
        Align.center(Text.from_markup(clock_art)),
        Align.center("[bold cyan]Welcome to StandLog CLI![/bold cyan] :notebook_with_decorative_cover: :sparkles:"),
        Align.center("[dim]Your beautiful terminal developer journal[/dim]"),
        footer,
        Text("\n")
    )
    console.print(group)


def main_menu():
    print_ascii_art()
    show_goal_progress()
    show_badges()
    while True:
        reminder()
        console.print("\n[bold cyan]StandLog CLI[/bold cyan]", style="bold")
        console.print("[1] Log today's standup\n[2] View today's log\n[3] Stats/Export/Reminder\n[4] Set weekly goals\n[5] Mark goal progress\n[6] Search logs\n[7] Email weekly logs\n[8] Knowledge Graph\n[9] Time Tracking Stats\n[10] Automation Rules\n[11] Quit")
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"], default="1")
        if choice == "1":
            log_entry()
        elif choice == "2":
            view_entry()
        elif choice == "3":
            viewer_menu()
        elif choice == "4":
            set_weekly_goals()
        elif choice == "5":
            mark_goal_progress()
        elif choice == "6":
            search_logs()
        elif choice == "7":
            email_weekly_logs()
        elif choice == "8":
            knowledge_graph_menu()
        elif choice == "9":
            time_tracking_stats()
        elif choice == "10":
            automation_rules_menu()
        elif choice == "11":
            console.print("[bold yellow]Goodbye![/bold yellow]")
            break


def knowledge_graph_menu():
    build_contextual_links()
    render_knowledge_graph()
    Prompt.ask("Press Enter to return to main menu")

def time_tracking_stats():
    """
    Show time spent per day/week and a simple bar chart in the terminal.
    """
    files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.json') and re.match(r'\d{4}-\d{2}-\d{2}\.json$', f)])
    if not files:
        console.print("[yellow]No logs to show time tracking stats.[/yellow]")
        return
    # Collect time per day
    day_times = []
    for fname in files:
        with open(os.path.join(DATA_DIR, fname)) as f:
            try:
                entry = json.load(f)
            except Exception:
                continue
        t = entry.get('time_spent', 0)
        try:
            t = int(t)
        except Exception:
            t = 0
        day_times.append((fname.replace('.json',''), t))
    # Show table and bar chart
    console.print(Panel("[bold blue]Time Tracking Stats[/bold blue]", expand=False))
    total = sum(t for _, t in day_times)
    console.print(f"[bold]Total time logged:[/bold] {total} min ({total//60}h {total%60}m)")
    for day, t in day_times[-7:]:
        bar = "[green]" + "█"*(t//10) + "[/green]" if t else ""
        console.print(f"[bold]{day}[/bold]: {t} min {bar}")
    Prompt.ask("Press Enter to return to main menu")


def main():
    ensure_data_dir()
    main_menu()

if __name__ == "__main__":
    main()
