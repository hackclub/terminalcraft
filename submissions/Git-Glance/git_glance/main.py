import typer
from pathlib import Path
import shutil

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.text import Text

from .config import add_repo, remove_repo, load_config
from .git import get_repo_status, is_git_repo, fetch_repo, get_detailed_repo_info


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
def list():
    """List all tracked repositories."""
    config = load_config()
    if not config["repos"]:
        print("[yellow]No repositories being tracked.[/yellow]")
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
        repo = next((r for r in config["repos"] if r["alias"] == only), None)
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