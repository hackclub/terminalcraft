#!/usr/bin/env python3
import os
import json
import datetime
import typepip install typer richr
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="📈 Habitify: Simple CLI habit tracker")
console = Console()

# Where we store your data
DATA_PATH = os.path.expanduser("~/.habitify.json")

def load_data():
    if not os.path.exists(DATA_PATH):
        return {"habits": {}}
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def save_data(data):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

def today_str():
    return datetime.date.today().isoformat()

def compute_streak(dates):
    s = set(dates)
    # current streak
    streak = 0
    d = datetime.date.today()
    while d.isoformat() in s:
        streak += 1
        d -= datetime.timedelta(days=1)
    # longest streak
    longest = 0
    dates_sorted = sorted(s)
    curr = 1
    for i in range(1, len(dates_sorted)):
        prev = datetime.date.fromisoformat(dates_sorted[i-1])
        currd = datetime.date.fromisoformat(dates_sorted[i])
        if (currd - prev).days == 1:
            curr += 1
        else:
            longest = max(longest, curr)
            curr = 1
    longest = max(longest, curr)
    return streak, longest

@app.command()
def add(name: str = typer.Argument(..., help="Name of the new habit")):
    """Add a new habit to track."""
    data = load_data()
    if name in data["habits"]:
        console.print(f"[yellow]Habit '{name}' already exists.[/yellow]")
        raise typer.Exit()
    data["habits"][name] = {"dates": []}
    save_data(data)
    console.print(f"[green]Added habit:[/green] '{name}'")

@app.command()
def list():
    """List all your habits."""
    data = load_data()
    if not data["habits"]:
        console.print("[red]No habits yet. Use 'habitify add NAME' to create one.[/red]")
        raise typer.Exit()
    table = Table(title="Your Habits")
    table.add_column("Habit", style="cyan")
    table.add_column("Logged Days", justify="right")
    table.add_column("Current Streak", justify="right")
    table.add_column("Longest Streak", justify="right")
    for name, info in data["habits"].items():
        dates = info["dates"]
        streak, longest = compute_streak(dates)
        table.add_row(name, str(len(dates)), str(streak), str(longest))
    console.print(table)

@app.command()
def done(name: str = typer.Argument(..., help="Mark habit as done for today")):
    """Mark a habit as completed for today."""
    data = load_data()
    if name not in data["habits"]:
        console.print(f"[red]Habit '{name}' not found.[/red]")
        raise typer.Exit()
    t = today_str()
    if t in data["habits"][name]["dates"]:
        console.print(f"[yellow]Already marked '{name}' done today.[/yellow]")
        raise typer.Exit()
    data["habits"][name]["dates"].append(t)
    save_data(data)
    console.print(f"[green]Great job![/green] Marked '{name}' as done on {t}.")

@app.command()
def history(name: str = typer.Argument(..., help="Show completion dates for a habit")):
    """Show all dates you completed a habit."""
    data = load_data()
    if name not in data["habits"]:
        console.print(f"[red]Habit '{name}' not found.[/red]")
        raise typer.Exit()
    dates = sorted(data["habits"][name]["dates"])
    if not dates:
        console.print(f"[yellow]No entries yet for '{name}'.[/yellow]")
        raise typer.Exit()
    table = Table(title=f"History for '{name}'")
    table.add_column("Date", style="magenta")
    for d in dates:
        table.add_row(d)
    console.print(table)

if __name__ == "__main__":
    app()
