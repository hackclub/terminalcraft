import click
import questionary
from pathlib import Path
from rich.console import Console
from rich.status import Status
import git # Import git for exception handling
from .analyzer import RepoAnalyzer
from .narrator import RepoNarrator
from .visualizer import create_html_story
import pyfiglet

console = Console(force_terminal=True)

@click.command()
def main():
    """Generate a human-readable story of a git repository's development."""
    
    # Display ASCII art welcome
    ascii_art = pyfiglet.figlet_format("Git-Narrate")
    console.print(f"[bold green]{ascii_art}[/bold green]")
    console.print("[bold green]Welcome to Git-Narrate! Let's create your project's story.[/bold green]")

    repo_path_str = console.input(
        "[bold cyan]Enter the path to your Git repository('/path/repo')[/bold cyan] [default: .]: "
    ) or "."
    repo_path = Path(repo_path_str)

    output_format = questionary.select(
        "Choose output format:",
        choices=["markdown", "html", "text"],
        default="html"
    ).ask()

    output_extension = "md" if output_format == "markdown" else "html" if output_format == "html" else "txt" if output_format == "text" else "txt"
    output_default = repo_path / "git_story"
    output_str = questionary.text(
        f"Enter output file path(/path/[filename])",
        default=str(output_default)
    ).ask()
    output_path = Path(f"{output_str}.{output_extension}")
    
    # Analyze repository
    console.print("[bold blue]Please be patient while the repository content is being examined.[/bold blue]")
    try:
        with click.progressbar(
            length=100,
            label=f"Analyzing repository at {repo_path}...",
            show_percent=False,
            show_eta=False,
            bar_template="%(label)s  %(bar)s | %(info)s",
            fill_char=click.style("█", fg="green"),
            empty_char=" ",
        ) as bar:
            analyzer = RepoAnalyzer(repo_path)
            repo_data = analyzer.analyze()
            bar.update(100) # Complete the progress bar once analysis is done
    except git.exc.NoSuchPathError:
        console.print(f"[bold red]Error: Repository not found at '{repo_path}'. Please ensure the path is correct and it's a valid Git repository.[/bold red]")
        return
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred during repository analysis: {e}[/bold red]")
        return
    
    # Generate narrative (always AI-powered)
    with Status(f"[bold green]Generating AI-powered narrative...", spinner="dots", console=console) as status:
        narrator = RepoNarrator(repo_data)
        story_md = narrator.generate_story()
        status.stop()

    # Save narrative
    try:
        if output_format == 'html':
            create_html_story(story_md, output_path, repo_data["repo_name"])
        else:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(story_md)
        console.print(f"[bold green]Narrative saved to {output_path}[/bold green]")
    except PermissionError:
        console.print(f"[bold red]Error: Permission denied to write to '{output_path}'. Please check file permissions or choose a different path.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")

if __name__ == "__main__":
    main()
