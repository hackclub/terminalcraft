import json
import typer
from pathlib import Path
from datetime import datetime, timedelta, timezone
import shutil
import os

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.text import Text
from rich.syntax import Syntax

from .config import add_repo, remove_repo, load_config, save_config, get_config_path, find_repo_by_alias, find_repo_by_path
from .git import get_repo_status, is_git_repo, fetch_repo, get_detailed_repo_info, open_repo, get_recent_commits, diff_repo, get_last_commit_date, run_git_command


app = typer.Typer()
console = Console()

def display_status_table(statuses: list[dict]):
    table = Table(title="[bold]Git Repositories Status[/bold]", show_lines=True, show_edge=True, row_styles=["", ""], expand=True)

    table.add_column("Alias", style="cyan", no_wrap=True)
    table.add_column("Path", style="dim")
    table.add_column("Branch", style="green")
    table.add_column("Uncommitted Changes", justify="right")
    table.add_column("Unpushed", justify="right")
    table.add_column("Needs Pull", justify="center")

    for s in statuses:
        uncommitted_style = "green" if s.get("uncommitted", 0) == 0 else "yellow"
        unpushed_style = "green" if s.get("unpushed", 0) == 0 else "red"
        needs_pull_style = "green" if not s.get("needs_pull", False) else "red"

        if "error" in s:
            alias = Text(s.get("alias", "<unknown>"), style="red")
            path = Text(s["path"], style="red")
            branch = Text("ERROR", style="red")
            uncommitted = unpushed = needs_pull = Text("ERROR", style="red")
        else:
            alias = s.get("alias", "<no-alias>")
            path = str(s["path"])
            branch = s["branch"]
            uncommitted = Text(str(s["uncommitted"]), style=uncommitted_style)
            unpushed = Text(str(s["unpushed"]), style=unpushed_style)
            needs_pull = Text("Yes" if s["needs_pull"] else "No", style=needs_pull_style)

        table.add_row(alias, path, branch, uncommitted, unpushed, needs_pull)

    console.print(table)

def format_detailed_info(alias: str, path: str, info: dict) -> Tree:
    tree = Tree(f"[bold cyan]Repo:[/bold cyan] {alias}")
    tree.add(f"[bold cyan]Path:[/bold cyan] {path}")
    tree.add(f"[bold cyan]Branch:[/bold cyan] {info['branch']}")

    status = tree.add("[bold cyan]Status:[/bold cyan]")
    if info["uncommitted"] == 0:
        status.add("[green]✔ No uncommitted changes[/green]")
    else:
        status.add(f"[yellow]✗ {info['uncommitted']} uncommitted[/yellow]")

    if info["unpushed"] == 0:
        status.add("[green]✔ 0 unpushed[/green]")
    else:
        status.add(f"[red]✗ {info['unpushed']} unpushed[/red]")

    if not info["needs_pull"]:
        status.add("[green]✔ Up-to-date[/green]")
    else:
        status.add("[red]✗ Needs pull[/red]")

    commit = tree.add("[bold magenta]Last Commit:[/bold magenta]")
    commit.add(f"[bold]Hash:[/bold] {info['last_commit_hash']}")
    commit.add(f"[bold]Message:[/bold] {info['last_commit_msg']}")
    commit.add(f"[bold]Author:[/bold] {info['last_commit_author']}")
    commit.add(f"[bold]Date:[/bold] {info['last_commit_date']}")

    remote = info.get("remote", "None")
    tree.add(f"[bold cyan]Remote:[/bold cyan] {remote}")
    tracked = info.get("is_tracked", True)
    tree.add(f"[bold cyan]Tracked:[/bold cyan] {'[green]✔ Yes[/green]' if tracked else '[red]✗ No[/red]'}")

    return tree

def print_banner():
    text = r"""
    ██████╗ ██╗████████╗      ██████╗ ██╗      █████╗ ███╗   ██╗ ██████╗███████╗
    ██╔════╝ ██║╚══██╔══╝     ██╔════╝ ██║     ██╔══██╗████╗  ██║██╔════╝██╔════╝
    ██║  ███╗██║   ██║  █████╗██║  ███╗██║     ███████║██╔██╗ ██║██║     █████╗  
    ██║   ██║██║   ██║  ╚════╝██║   ██║██║     ██╔══██║██║╚██╗██║██║     ██╔══╝  
    ╚██████╔╝██║   ██║        ╚██████╔╝███████╗██║  ██║██║ ╚████║╚██████╗███████╗
    ╚═════╝ ╚═╝   ╚═╝         ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝
    """
    print(text)

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Git Glance: A simple CLI tool to track and manage multiple git repositories."""
    if ctx.invoked_subcommand is None:
        print_banner()

@app.command()
def scan(dir: str = typer.Argument(None, help="Directory to recursively scan for Git Repositories")):
    """Scan a directory recusrively for Git repositories and add them to the tracking list."""
    base_path = Path(dir).expanduser().resolve()
    if not base_path.exists():
        console.print(f"[bold red]Error: Directory: '{dir}' does not exist.[/bold red]")
        raise typer.Exit(1)
    
    found_repos = []
    for root, dirs, files in os.walk(base_path):
        if ".git" in dirs:
            repo_path = Path(root).resolve()
            found_repos.append(repo_path)
            dirs[:] = []
    
    if not found_repos:
        console.print(f"[bold yellow]No Git Repositories found in '{dir}'.[/bold yellow]")
        return
    
    console.print(f"[bold cyan]Found {len(found_repos)} Git Repositories:[/bold cyan]")

    config = load_config()

    for repo_path in found_repos:
        if find_repo_by_path(str(repo_path)):
            console.print(f"[yellow]• Skipping already tracked repo: {repo_path}[/yellow]")
            continue

        default_alias = repo_path.name
        console.print(f"\n[bold]Repository:[/bold] {repo_path}")
        alias = typer.prompt("Enter an alias for this repo", default=default_alias)

        try:
            add_repo(str(repo_path), alias)
            console.print(f"[green]✓ Added {alias}[/green]")
        except ValueError as e:
            console.print(f"[red]✗ Failed to add {alias}[/red]: {e}")

@app.command()
def clean():
    """Remove invalid or deleted Git Repos from the tracking list"""
    config = load_config()
    repos = config.get("repos", [])
    valid_repos = []

    removed = 0
    for repo in repos:
        if Path(repo["path"]).exists() and is_git_repo(repo["path"]):
            valid_repos.append(repo)
        else:
            console.print(f"[red]✗ Removed invalid repo:[/red] {repo['alias']} ({repo['path']})")
            removed += 1

    config["repos"] = valid_repos
    save_config(config)

    if removed == 0:
        console.print("[green]✔ All tracked repos are valid.[/green]")
    else:
        console.print(f"[bold yellow]Cleaned {removed} invalid entries from config.[/bold yellow]")

@app.command()
def config(
    reset: bool = typer.Option(False, "--reset", "-r", help="Reset config and removed all tracked repositories"),
    show: bool = typer.Option(False, "--show", help="Display raw config JSON")
):
    """Manage Git-Glance configuration: show or reset config file"""
    if reset and show:
        console.print("[bold red]Error:[/bold red] You can only use one of '--reset' or '--show' at a time")
        raise typer.Exit(1)
    
    config_path = get_config_path()
    
    if reset:
        confirm = typer.confirm("Are you sure you want to delete all tracked repos and reset config?")
        if confirm:
            config_path.unlink(missing_ok=True)
            console.print("[bold red]✔ Config reset. All tracked repositories removed.[/bold red]")
        else:
            console.print("[yellow]Reset cancelled.[/yellow]")
        return
    
    if show:
        config = load_config()
        pretty = json.dumps(config, indent=2)
        syntax = Syntax(pretty, "json", word_wrap=True, line_numbers=True)
        console.print(Panel(syntax, title="[bold]Current Configuration[bold]", expand=True))

@app.command()
def rename(
    old_alias: str = typer.Argument(..., help="Current alias of the repo you want to rename"),
    new_alias: str = typer.Argument(..., help="New alias to assign to the repo")
):
    """Rename the alias of a tracked repository"""
    config = load_config()
    repos = config.get("repos", [])

    if old_alias == new_alias:
        console.print("[yellow]⚠ New alias is the same as the old one. Nothing to do.[/yellow]")
        raise typer.Exit()

    if any(r["alias"] == new_alias for r in repos):
        console.print(f"[bold red]Error:[/bold red] An alias '{new_alias}' already exists.")
        raise typer.Exit(1)

    for repo in repos:
        if repo["alias"] == old_alias:
            repo["alias"] = new_alias
            save_config(config)
            console.print(f"[bold green]✔ Renamed repository from '{old_alias}' to '{new_alias}'[/bold green]")
            return

    console.print(f"[bold red]Error:[/bold red] No repository found with alias '{old_alias}'")

@app.command()
def open(alias: str = typer.Argument(..., help="Alias of the repository to open")):
    """Open a tracked repo in the system file manager"""
    repo = find_repo_by_alias(alias)
    if not repo:
        console.print(f"[bold red]Error:[/bold red] No repository found with alias '{alias}'")
        raise typer.Exit(1)
    
    try:
        open_repo(repo["path"])
        console.print(f"[green]✔ Opened repository '{alias}' in file manager[/green]")
    except Exception as e:
        console.print(f"[red]✗ Failed to open repository '{alias}': {e}[/red]")

@app.command()
def commit_summary(
    alias: str = typer.Option(None, help="Alias of specific repo (optional)"),
    count: int = typer.Option(5, help="Number of recent commits to show per repo")
):
    """Show latest N commits for tracked repositories"""
    config = load_config()
    repos = config.get("repos", [])

    if alias:
        repo = find_repo_by_alias(alias)
        if not repo:
            console.print(f"[bold red]Error:[/bold red] No repository found with alias '{alias}'")
            raise typer.Exit(1)
        repos = [repo]
    
    for repo in repos:
        path = repo["path"]
        repo_alias = repo["alias"]
        try:
            log = get_recent_commits(path, count)
            syntax = Syntax(log, "bash", theme="ansi_dark", line_numbers=False, word_wrap=True)
            console.print(Panel(syntax, title=f"[bold magenta]{repo_alias}[/bold magenta]", expand=True))
        except Exception as e:
            console.print(f"[red]✗ Failed to get commits for {repo_alias}[/red]: {e}")

@app.command()
def diff(alias: str = typer.Option(None, help="Alias of a single repo to view diff for")):
    """Show uncommitted changes (diff) for one or all tracked repositories"""
    config = load_config()
    repos = config.get("repos", [])

    if not repos:
        console.print("[yellow]No repositories are being tracked.[/yellow]")
        raise typer.Exit()
    
    if alias:
        repo = find_repo_by_alias(alias)
        if not repo:
            console.print(f"[bold red]Error:[/bold red] No repository found with alias '{alias}'")
            raise typer.Exit(1)
        
        try:
            diff_output = diff_repo(repo["path"])
            if not diff_output.strip():
                console.print(f"[green]✓ No changes in '{alias}'[/green]")
            else:
                syntax = Syntax(diff_output, "diff", theme="ansi_dark", line_numbers=False)
                console.print(Panel(syntax, title=f"[bold cyan]Diff: {alias}[/bold cyan]", expand=True))
        except Exception as e:
            console.print(f"[red]✗ Failed to get diff for {alias}: {e}[/red]")
        return
    

    for repo in repos:
        try:
            diff_output = diff_repo(repo["path"])
            if not diff_output.strip():
                continue
            syntax = Syntax(diff_output, "diff", theme="ansi_dark", line_numbers=False)
            console.print(Panel(syntax, title=f"[bold cyan]Diff: {repo['alias']}[/bold cyan]", expand=True))
        except Exception as e:
            console.print(f"[red]✗ Failed to get diff for {repo['alias']}: {e}[/red]")

@app.command()
def stale(days: int = typer.Option(10, help="Threshold in days in order to consider a repo stale")):
    """Show repositories with no commits in the last N days"""
    config = load_config()
    repos = config.get("repos", [])

    if not repos:
        console.print("[yellow]No repositories are being tracked.[/yellow]")
        raise typer.Exit()
    
    threshold = datetime.now(timezone.utc) - timedelta(days=days)
    stale_repos = []

    for repo in repos:
        try:
            last_commit = get_last_commit_date(repo["path"])
            if last_commit < threshold:
                stale_repos.append((repo, last_commit))
        except Exception as e:
            console.print(f"[red]✗ Failed to check last commit for {repo['alias']}: {e}[/red]")
    
    if not stale_repos:
        console.print("[green]✔ No stale repositories found.[/green]")
        return
    
    table = Table(title=f"Stale Repositories (> {days} days)", expand=True)
    table.add_column("Alias", style="cyan")
    table.add_column("Path", style="dim")
    table.add_column("Last Commit", style="red")

    for repo, date in stale_repos:
        table.add_row(repo["alias"], repo["path"], date.strftime("%Y-%m-%d"))

    console.print(table)
    
@app.command()
def pull(only: str = typer.Option(None, help="Alias of a specific repo to pull")):
    """Pull latest changes from remote for all or specific repo"""
    config = load_config()
    repos = config.get("repos", [])

    if only:
        repo = find_repo_by_alias(only)
        if not repo:
            console.print(f"[red]✗ No repo found with alias '{only}'[/red]")
            raise typer.Exit(1)
        try:
            run_git_command(repo["path"], ["pull"])
            console.print(f"[green]✔ Pulled latest changes for '{only}'[/green]")
        except Exception as e:
            console.print(f"[red]✗ Pull failed for '{only}': {e}[/red]")
        return

    console.print("[cyan]Pulling latest changes for all repos...[/cyan]")
    for repo in repos:
        try:
            run_git_command(repo["path"], ["pull"])
            console.print(f"[green]✔ Pulled '{repo['alias']}'[/green]")
        except Exception as e:
            console.print(f"[red]✗ Pull failed for '{repo['alias']}': {e}[/red]")

@app.command()
def push(only: str = typer.Option(None, help="Alias of a specific repo to push")):
    """Push local commits to remote for all or specific repo"""
    config = load_config()
    repos = config.get("repos", [])
    if only:
        repo = find_repo_by_alias(only)
        if not repo:
            console.print(f"[red]✗ No repo found with alias '{only}'[/red]")
            raise typer.Exit(1)
        try:
            run_git_command(repo["path"], ["push"])
            console.print(f"[green]✔ Pushed local commits for '{only}'[/green]")
        except Exception as e:
            console.print(f"[red]✗ Push failed for '{only}': {e}[/red]")
        return

    console.print("[cyan]Pushing local commits for all repos...[/cyan]")
    for repo in repos:
        try:
            run_git_command(repo["path"], ["push"])
            console.print(f"[green]✔ Pushed '{repo['alias']}'[/green]")
        except Exception as e:
            console.print(f"[red]✗ Push failed for '{repo['alias']}': {e}[/red]")

@app.command()
def list():
    """List all tracked repositories."""
    config = load_config()
    if not config["repos"]:
        console.print("[yellow]No repositories being tracked.[/yellow]")
        raise typer.Exit()

    table = Table(title="Tracked Git Repositories", expand=True, show_lines=True)
    table.add_column("Alias", style="cyan")
    table.add_column("Path", style="dim")

    for repo in config["repos"]:
        table.add_row(repo["alias"], repo["path"])

    console.print(table)


@app.command()
def fetch():
    """Fetch updates for all tracked git repositories."""
    config = load_config()
    repos = config.get("repos", [])
    if not repos:
        console.print("[yellow]No repositories are being tracked.[/yellow]")
        raise typer.Exit()

    console.print("[bold cyan]Fetching updates for all repos...[/bold cyan]")
    for repo in repos:
        try:
            fetch_repo(repo["path"])
            console.print(f"[green]✓ {repo['alias']}[/green] fetched successfully.")
        except ValueError as e:
            console.print(f"[red]✗ {repo['alias']}[/red] fetch failed: {e}")


@app.command()
def status(only: str = typer.Option(None, help="Alias of a single repo to show full detail for")):
    """Show status of all tracked git repositories"""
    config = load_config()
    if only:
        repo = find_repo_by_alias(only)
        if not repo:
            console.print(f"[bold red]Error: No repo with alias '{only}' found.[/bold red]")
            raise typer.Exit(1)
        info = get_detailed_repo_info(repo["path"])
        tree = format_detailed_info(repo["alias"], repo["path"], info)
        console.print(Panel(tree, title=f"Detailed Repo Info", expand=True))
        return

    statuses = []
    for repo in config["repos"]:
        stat = get_repo_status(repo["path"])
        stat["alias"] = repo.get("alias", "<no-alias>")
        statuses.append(stat)

    display_status_table(statuses)

@app.command()
def add(path: str = typer.Argument(help="Enter a path to your repo"), alias: str = typer.Argument(help="Enter a nickname for the repo.")):
    """Add a new git repo to the tracking list."""
    try:
        if not Path(path).expanduser().resolve().exists():
            console.print(f"[bold red]Error: The path '{path}' does not exist.[/bold red]")
            raise typer.Exit(1)
        
        if not is_git_repo(path):
            console.print(f"[bold red]Error: The path '{path}' is not a valid Git repository.[/bold red]")
            raise typer.Exit(1)
        add_repo(path, alias)
        console.print(f"[bold green]Added {path} to the tracking list.[/bold green]")
    except ValueError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

@app.command()
def remove(
    path: str = typer.Option(None, help="Path to the git repo to remove."),
    alias: str = typer.Option(None, help="Alias of the repo to remove (optional).")
):
    """Remove a git repo from the tracking list."""
    if not path and not alias:
        console.print("[bold red]Error: Either a path or an alias must be provided.[/bold red]")
        raise typer.Exit(1)
    try:
        remove_repo(path, alias)
        console.print(f"[bold green]Removed repo with path '{path}' or alias '{alias}' from the tracking list.[/bold green]")
    except ValueError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")\
        
if __name__ == "__main__":
    import shutil
    if not shutil.which("git"):
        typer.echo("❌ Git is not installed or not found in your PATH.")
        raise typer.Exit(1)
    app()