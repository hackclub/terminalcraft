
import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import shutil
import os
import json
from pathlib import Path
from datetime import datetime

app = typer.Typer()
console = Console()
DATA_DIR = Path("data")
BACKUP_DIR = Path("backups")
LOG_FILE = DATA_DIR / "logs.json"

# Ensure dirs exist
DATA_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

def load_logs():
    if LOG_FILE.exists():
        return json.loads(LOG_FILE.read_text())
    return []

def save_logs(logs):
    LOG_FILE.write_text(json.dumps(logs, indent=2))

@app.command()
def backup():
    folder = Prompt.ask("Full path of folder to back up")
    src = Path(folder)
    if not src.exists() or not src.is_dir():
        console.print(f"[red]Error: Folder '{folder}' does not exist.[/red]")
        raise typer.Exit()
    
    fmt = Prompt.ask("Compression format (zip/tar)", default="zip")
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    base_name = f"{src.name}_{ts}"
    dest = BACKUP_DIR / base_name

    console.print(f"[cyan]Backing up '{src}'...[/cyan]")
    try:
        if fmt == "zip":
            shutil.make_archive(str(dest), "zip", root_dir=src)
            backup_file = dest.with_suffix(".zip")
        elif fmt == "tar":
            shutil.make_archive(str(dest), "gztar", root_dir=src)
            backup_file = dest.with_suffix(".tar.gz")
        else:
            console.print("[red]Unsupported format.[/red]")
            raise typer.Exit()
        
        logs = load_logs()
        logs.append({
            "source": str(src.resolve()),
            "backup": str(backup_file.resolve()),
            "format": fmt,
            "time": ts
        })
        save_logs(logs)
        console.print(f"[green]Backup complete: {backup_file}[/green]")
    except Exception as e:
        console.print(f"[red]Backup failed: {e}[/red]")

@app.command()
def list():
    logs = load_logs()
    if not logs:
        console.print("[yellow]No backups found.[/yellow]")
        return
    table = Table(title="NyxBackup History")
    table.add_column("Source")
    table.add_column("Backup File")
    table.add_column("Format")
    table.add_column("Time")

    for entry in logs:
        table.add_row(entry["source"], Path(entry["backup"]).name, entry["format"], entry["time"])
    
    console.print(table)

@app.command()
def clean(days: int = typer.Option(30, help="Delete backups older than X days")):
    now = datetime.now()
    logs = load_logs()
    new_logs = []
    removed = 0

    for entry in logs:
        bfile = Path(entry["backup"])
        age = (now - datetime.strptime(entry["time"], "%Y-%m-%d_%H-%M")).days
        if age > days:
            if bfile.exists():
                bfile.unlink()
                console.print(f"[red]Deleted:[/red] {bfile} (age: {age} days)")
                removed += 1
            else:
                console.print(f"[yellow]Not found (already deleted?):[/yellow] {bfile}")
        else:
            new_logs.append(entry)
    save_logs(new_logs)
    console.print(f"[green]{removed} old backups removed.[/green]")

if __name__ == "__main__":
    app()
