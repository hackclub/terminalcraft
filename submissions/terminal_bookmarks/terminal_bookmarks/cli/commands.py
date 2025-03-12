import re
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm
from typing import Optional, List, Tuple
from uuid import UUID
import sys
from pathlib import Path
from rich.columns import Columns
from rich.padding import Padding
from rich.box import Box, ROUNDED, SIMPLE, DOUBLE, MINIMAL
from datetime import datetime

from ..core.manager import BookmarkManager
from ..core.models import (
    Bookmark,
    SearchOptions,
    SearchResult,
    DateFilter,
    SortOrder,
    ExecutionContext
)
from ..utils.config import get_default_storage_path
from ..utils.exceptions import (
    BookmarkError,
    BookmarkNotFoundError,
    ExecutionError,
    ValidationError,
    SecurityError,
    DependencyError,
    ContextError
)
from ..core.executor import CommandExecutor
from ..shell.integration import ShellIntegration
from ..utils.styling import (
    console,
    create_table,
    format_bookmark_table,
    format_bookmark_details,
    format_success,
    format_error,
    format_warning,
    format_tip,
    COLORS,
    OutputFormatter,
    formatter
)

try:
    from rich.progress import Progress, SpinnerColumn, TextColumn
except ImportError:
    Progress = None
    SpinnerColumn = None
    TextColumn = None

def print_help_message(ctx: click.Context):
    """Display beautifully formatted help message."""
    title = """
╭──────────────────────────────────────╮
│         Terminal Bookmarks           │
╰──────────────────────────────────────╯"""
    
    console.print(title, style=COLORS['primary'], justify="center")
    console.print("[bold]A powerful command-line bookmark manager[/bold]", 
                 style=COLORS['accent'], justify="center")
    quick_start = Table(show_header=False, box=None, padding=(0, 2))
    quick_start.add_column("Command", style=f"bold {COLORS['accent']}")
    quick_start.add_column("Description", style="white")
    
    quick_start.add_row(
        "tb add -t \"git status\" -c \"git status\"",
        "Add a bookmark"
    )
    quick_start.add_row(
        "tb list",
        "List all bookmarks"
    )
    quick_start.add_row(
        "tb run \"git status\"",
        "Run a bookmark"
    )

    console.print(Panel(
        quick_start,
        title="[bold]Quick Start Guide",
        border_style=COLORS['primary'],
        padding=(1, 2)
    ))
    commands_table = Table(
        show_header=True,
        header_style=f"bold {COLORS['highlight']}",
        box=None,
        padding=(0, 2),
        title="Available Commands",
        title_style=f"bold {COLORS['primary']}"
    )
    
    commands_table.add_column("Command", style=f"bold {COLORS['accent']}")
    commands_table.add_column("Description", style="white")
    commands_table.add_column("Example", style=f"dim {COLORS['muted']}")

    commands_table.add_row(
        "add",
        "Add a new bookmark",
        "tb add -t \"Git Status\" -c \"git status\" --tags git,status"
    )
    commands_table.add_row(
        "list",
        "List all bookmarks",
        "tb list --detailed"
    )
    commands_table.add_row(
        "edit",
        "Edit a bookmark",
        "tb edit <id> -t \"New Title\""
    )
    commands_table.add_row(
        "delete",
        "Remove a bookmark",
        "tb delete <id>"
    )
    commands_table.add_row(
        "run",
        "Execute a bookmarked command",
        "tb run <id>"
    )

    console.print(commands_table)
    options_table = Table(
        show_header=True,
        header_style=f"bold {COLORS['highlight']}",
        box=None,
        padding=(0, 2),
        title="Global Options",
        title_style=f"bold {COLORS['primary']}"
    )
    
    options_table.add_column("Option", style=f"bold {COLORS['accent']}")
    options_table.add_column("Description", style="white")
    options_table.add_column("Default", style=f"dim {COLORS['muted']}")

    options_table.add_row(
        "--help",
        "Show this help message",
        "-"
    )
    options_table.add_row(
        "--version",
        "Show version information",
        "-"
    )

    console.print(options_table)
    tips = [
        "[bold]💡 Tags:[/bold] Use tags to organize related commands",
        "[bold]🔍 IDs:[/bold] Use short IDs or full IDs to reference bookmarks",
        "[bold]📋 Details:[/bold] Use --detailed with list for more information"
    ]

    console.print(Panel(
        "\n".join(tips),
        title="[bold]Pro Tips",
        border_style=COLORS['primary'],
        padding=(1, 2)
    ))

@click.group(invoke_without_command=True)
@click.version_option(
    version='1.0.0',
    prog_name='Terminal Bookmarks',
    message='%(prog)s version %(version)s',
)
@click.pass_context
def cli(ctx):
    """Terminal Bookmarks - Manage your command bookmarks efficiently."""
    ctx.ensure_object(dict)
    if 'manager' not in ctx.obj:
        storage_path = get_default_storage_path()
        ctx.obj['manager'] = BookmarkManager(storage_path)
    if ctx.invoked_subcommand is None:
        print_help_message(ctx)

@cli.command()
@click.option('--title', '-t', required=True, help='Title of the bookmark')
@click.option('--command', '-c', required=True, help='The command to bookmark')
@click.option('--description', '-d', help='Description of the command')
@click.option('--tags', help='Comma-separated list of tags')
@click.pass_context
def add(ctx, title: str, command: str, description: Optional[str], tags: Optional[str]):
    """Add a new bookmark.
    
    Examples:
        tb add -t "Git Status" -c "git status" --tags git,status
        tb add --title "Python Hello" --command "python -c 'print(\"Hello\")'" --tags python,demo
    """
    try:
        manager = ctx.obj.get('manager')
        tag_list = []
        if tags:
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
            
        bookmark = manager.add_bookmark(
            title=title,
            command=command,
            description=description,
            tags=tag_list
        )
        
        format_success(f"Added bookmark: {title}")
        format_tip(f"Run this command with: tb run \"{title}\"")
        _display_bookmark_details(bookmark)
    except Exception as e:
        format_error(f"Failed to add bookmark: {str(e)}")
        ctx.exit(1)

@cli.command()
@click.option('--tag', '-t', help='Filter by tag')
@click.option('--sort', '-s', 
              type=click.Choice(['title', 'date', 'usage']), 
              default='title',
              help='Sort bookmarks by field')
@click.option('--detailed', '-d', is_flag=True, help='Show detailed information')
@click.pass_context
def list(ctx, tag: Optional[str], sort: str, detailed: bool):
    """List all bookmarks."""
    try:
        manager = ctx.obj.get('manager')
        if not manager:
            raise BookmarkError("Bookmark manager not initialized")
        bookmarks = manager.get_all_bookmarks()
        if not bookmarks:  
            format_warning(
                "No bookmarks found",
                suggestion="Add your first bookmark with 'tb add'"
            )
            return
        if tag:
            bookmarks = [b for b in bookmarks if tag in (b.tags or [])]
            if not bookmarks:
                format_warning(f"No bookmarks found with tag: {tag}")
                return
        if sort == 'date':
            bookmarks.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
        elif sort == 'usage':
            bookmarks.sort(key=lambda x: x.use_count or 0, reverse=True)
        else:  
            bookmarks.sort(key=lambda x: (x.title or "").lower())
        
        if detailed:
            _display_detailed_list(bookmarks)
        else:
            _display_compact_list(bookmarks)
            
    except BookmarkError as e:
        format_error(f"Bookmark operation failed: {str(e)}")
    except Exception as e:
        format_error(f"Unexpected error: {str(e)}")
        if ctx.obj.get('debug'):
            raise

def _display_compact_list(bookmarks: List[Bookmark]):
    """Display a compact table of bookmarks."""
    if not bookmarks:
        format_warning("No bookmarks found", suggestion="Add a bookmark with: tb add")
        return
    width = console.width or 80
    id_width = 6
    uses_width = 6
    padding = 4
    remaining_width = max(50, width - (id_width + uses_width + padding * 5))
    title_width = max(15, int(remaining_width * 0.3))
    command_width = max(20, int(remaining_width * 0.4))
    tags_width = max(10, int(remaining_width * 0.3))
    title_panel = Panel(
        "[bold]All Bookmarks[/]",
        style=COLORS['primary'],
        box=MINIMAL,
        padding=(0, 2)
    )
    console.print(title_panel)
    table = Table(
        box=DOUBLE,
        header_style=f"bold {COLORS['highlight']}",
        border_style=COLORS['muted'],
        padding=(0, 1),
        width=width,
        show_lines=True
    )
    table.add_column("ID", style=f"bold {COLORS['accent']}", width=id_width)
    table.add_column("Title", style="bold white", width=title_width)
    table.add_column("Command", style=COLORS['accent'], width=command_width)
    table.add_column("Tags", style=COLORS['highlight'], width=tags_width)
    table.add_column("Uses", justify="right", style=COLORS['muted'], width=uses_width)
    for bookmark in bookmarks:
        if not bookmark:  
            continue
        id_text = str(bookmark.id or "")[:4] + "…" if len(str(bookmark.id or "")) > 5 else str(bookmark.id or "")
        title = str(bookmark.title or "")
        title = (title[:title_width-2] + "…") if len(title) > title_width-1 else title
        
        command = str(bookmark.command or "")
        command = (command[:command_width-2] + "…") if len(command) > command_width-1 else command
        
        tags = ", ".join(bookmark.tags) if bookmark.tags else ""
        tags = (tags[:tags_width-2] + "…") if len(tags) > tags_width-1 else tags
        
        table.add_row(
            id_text,
            title,
            command,
            tags,
            str(bookmark.use_count or 0)
        )
    
    console.print(table)
    console.print()

def _display_detailed_list(bookmarks: List[Bookmark]):
    """Display detailed information for each bookmark."""
    title_panel = Panel(
        "[bold]All Bookmarks[/]",
        style=COLORS['primary'],
        box=MINIMAL,
        padding=(0, 2)
    )
    console.print("\n")
    console.print(title_panel)
    console.print()
    width = console.width or 80
    panel_width = width - 4
    
    for bookmark in bookmarks:
        content = [
            f"[bold white]{bookmark.title}[/]",
            f"[{COLORS['accent']}]Command:[/] {bookmark.command}",
            f"[{COLORS['highlight']}]Tags:[/] {', '.join(bookmark.tags) if bookmark.tags else 'None'}",
            "",  
            f"[{COLORS['muted']}]Created:[/] {bookmark.created_at.strftime('%Y-%m-%d %H:%M')}",
            f"[{COLORS['muted']}]Last Used:[/] {bookmark.last_used.strftime('%Y-%m-%d %H:%M') if bookmark.last_used else 'Never'}",
            f"[{COLORS['muted']}]Uses:[/] {bookmark.use_count}"
        ]
        
        if bookmark.description:
            content.insert(1, f"[dim]{bookmark.description}[/]")
            content.insert(2, "")  
        
        panel = Panel(
            "\n".join(content),
            title=f"[{COLORS['accent']}]{bookmark.id}[/]",
            title_align="left",
            width=panel_width,
            border_style=COLORS['primary'],
            box=DOUBLE,
            padding=(1, 2),
            expand=True
        )
        
        console.print(panel)
        console.print()  

@cli.command()
@click.option('--minimal', '-m', is_flag=True, help='Minimal output format')
@click.option('--no-color', is_flag=True, help='Disable colored output')
@click.pass_context
def configure(ctx, minimal: bool, no_color: bool):
    """Configure output formatting."""
    global formatter
    if no_color:
        formatter = OutputFormatter(color_scheme={k: '' for k in COLORS})
    if minimal:
        formatter = OutputFormatter(minimal=True)
    format_success("Display settings updated")

@cli.command()
@click.argument('query', required=False)
@click.option('--tags', '-t', help='Filter by tags (comma-separated)')
@click.option('--sort', '-s', 
              type=click.Choice(['relevance', 'title', 'date', 'usage']), 
              default='relevance',
              help='Sort results by')
@click.pass_context
def search(ctx, query: Optional[str], tags: Optional[str], sort: str):
    """Search bookmarks by title, command, or tags.
    
    Examples:
        tb search git                    Search in all fields
        tb search --tags git,status      Search by tags
        tb search "git status" --sort usage
    """
    try:
        manager = ctx.obj.get('manager')
        if not manager:
            raise click.ClickException("Failed to initialize bookmark manager")

        tag_list = []
        if tags:
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]

        bookmarks = manager.get_all_bookmarks()
        if not bookmarks:
            format_warning("No bookmarks found")
            return

        results = []
        search_query = query.strip().lower() if query else ""
        
        for bookmark in bookmarks:
            if not bookmark:  # Skip None bookmarks
                continue
                
            if tag_list and not any(tag in (bookmark.tags or []) for tag in tag_list):
                continue

            score = 0
            matches = []
            
            # Only search if we have a query
            if search_query:
                if bookmark.title and search_query in bookmark.title.lower():
                    score += 3
                    matches.append(bookmark.title)
                    
                if bookmark.command and search_query in bookmark.command.lower():
                    score += 2
                    matches.append(bookmark.command)
                    
                if bookmark.tags and any(search_query in tag.lower() for tag in bookmark.tags):
                    score += 1
                    matches.extend([tag for tag in bookmark.tags if search_query in tag.lower()])
                    
                if score == 0:  # No matches found
                    continue
            else:
                score = 1  # Include all bookmarks when no query
                
            results.append((bookmark, score))

        if not results:
            format_warning(
                "No matching bookmarks found",
                suggestion="Try different search terms or use 'tb list' to see all bookmarks"
            )
            return

        # Sort results
        if sort == 'relevance':
            results.sort(key=lambda x: x[1], reverse=True)
        elif sort == 'title':
            results.sort(key=lambda x: x[0].title.lower() if x[0].title else "")
        elif sort == 'date':
            results.sort(key=lambda x: x[0].created_at or datetime.min, reverse=True)
        else:  # usage
            results.sort(key=lambda x: x[0].use_count or 0, reverse=True)
            
        # Display results
        table = Table(
            title="Search Results",
            title_style=f"bold {COLORS['primary']}",
            box=DOUBLE,
            header_style=f"bold {COLORS['highlight']}",
            border_style=COLORS['muted'],
            padding=(0, 1),
            width=console.width
        )
        
        table.add_column("ID", style=f"bold {COLORS['accent']}", width=6)
        table.add_column("Title", style="bold white", width=25)
        table.add_column("Command", style=COLORS['accent'], width=35)
        table.add_column("Tags", style=COLORS['highlight'], width=20)
        table.add_column("Uses", justify="right", style=COLORS['muted'], width=6)
        
        for bookmark, score in results:
            id_text = str(bookmark.id)[:4] + "…" if len(str(bookmark.id)) > 5 else str(bookmark.id)
            title = bookmark.title or ""
            command = bookmark.command or ""
            
            if search_query:
                if search_query in title.lower():
                    title = title.replace(search_query, f"[yellow]{search_query}[/yellow]")
                if search_query in command.lower():
                    command = command.replace(search_query, f"[yellow]{search_query}[/yellow]")
            
            tags = ", ".join(bookmark.tags) if bookmark.tags else ""
            if search_query and tags:
                tags = tags.replace(search_query, f"[yellow]{search_query}[/yellow]")
            
            table.add_row(
                id_text,
                title,
                command[:32] + "..." if len(command) > 35 else command,
                tags[:17] + "..." if len(tags) > 20 else tags,
                str(bookmark.use_count or 0)
            )
        
        console.print(table)
        console.print()
        format_tip(f"Found {len(results)} matching bookmark{'s' if len(results) != 1 else ''}")
        
    except Exception as e:
        raise click.ClickException(f"Search failed: {str(e)}")

@cli.command()
@click.argument('bookmark_id')
@click.option('--force', '-f', is_flag=True, help='Skip confirmation')
@click.pass_context
def delete(ctx, bookmark_id: str, force: bool):
    """Delete a bookmark by ID.
    
    Examples:
        tb delete <id>
        tb delete <id> --force
    """
    try:
        manager = ctx.obj.get('manager')
        if not manager:
            raise click.ClickException("Failed to initialize bookmark manager")
        
        try:
            bookmark_id_obj = UUID(bookmark_id)
            bookmark = manager.get_bookmark(bookmark_id_obj)
        except ValueError:
            bookmark = manager.find_bookmark_by_partial_id(bookmark_id)
            if not bookmark:
                raise BookmarkNotFoundError(f"No bookmark found with ID starting with '{bookmark_id}'")
        
        if not force:
            if not click.confirm(f"Are you sure you want to delete bookmark '{bookmark.title}'?"):
                click.echo("Deletion cancelled.")
                return

        manager.delete_bookmark(bookmark.id)
        click.echo(f"✓ Deleted bookmark: {bookmark.title}")
        
    except BookmarkNotFoundError as e:
        raise click.ClickException(str(e))
    except BookmarkError as e:
        raise click.ClickException(f"Failed to delete bookmark: {str(e)}")
    except Exception as e:
        raise click.ClickException(f"An unexpected error occurred: {str(e)}")

@cli.command()
@click.argument('bookmark_id')
@click.argument('args', nargs=-1)
@click.option('--force', '-f', is_flag=True, help='Skip safety checks')
@click.option('--sandbox', '-s', is_flag=True, help='Run in sandbox mode')
@click.option('--preview', '-p', is_flag=True, help='Preview command before running')
@click.pass_context
def run(ctx, bookmark_id: str, args: tuple[str, ...], force: bool, 
        sandbox: bool, preview: bool):
    """Execute a bookmarked command."""
    try:
        manager = ctx.obj.get('manager')
        bookmark = _resolve_bookmark_reference(manager, bookmark_id)
        executor = CommandExecutor(sandbox_mode=sandbox)
        context = ExecutionContext(
            force=force,
            check_dependencies=True,
            command_args=list(args) if args else None
        )
        console.print(f"\n[bold {COLORS['primary']}]Running bookmark:[/]")
        console.print(f"  Title: [bold white]{bookmark.title}[/]")
        console.print(f"  Command: [{COLORS['accent']}]{bookmark.command}[/]")
        if args:
            console.print(f"  Args: [{COLORS['highlight']}]{' '.join(args)}[/]")
        with console.status(f"[{COLORS['primary']}]Running command...", spinner="dots"):
            result = executor.execute_bookmark(bookmark, context=context)
        
        if result.success:
            format_success("Command executed successfully")
            if result.output:
                console.print(Panel(
                    result.output,
                    title="Output",
                    border_style=COLORS['primary'],
                    padding=(1, 2)
                ))
        else:
            format_error(
                "Command failed", 
                help_text="Check if all required dependencies are installed"
            )
            if result.error:
                console.print(Panel(
                    result.error,
                    title="Error",
                    border_style=COLORS['error'],
                    padding=(1, 2)
                ))
        manager.record_usage(bookmark.id)
        
    except BookmarkNotFoundError as e:
        format_error(
            f"Bookmark not found: {str(e)}", 
            help_text="Use 'tb list' to see all available bookmarks"
        )
    except ValidationError as e:
        format_error(str(e))
        if ctx.obj.get('debug'):
            raise
    except (SecurityError, DependencyError, ContextError, ExecutionError) as e:
        format_error(str(e))
    except Exception as e:
        format_error(f"Unexpected error: {str(e)}")
        if ctx.obj.get('debug'):
            raise

def _resolve_bookmark_reference(manager: BookmarkManager, reference: str) -> Bookmark:
    """Resolve a bookmark reference to a Bookmark object."""
    try:
        return manager.get_bookmark(UUID(reference))
    except ValueError:
        pass
    if len(reference) >= 4:
        matching_bookmarks = []
        for bookmark in manager.bookmarks.values():
            if str(bookmark.id).startswith(reference):
                matching_bookmarks.append(bookmark)
        
        if len(matching_bookmarks) == 1:
            return matching_bookmarks[0]
        elif len(matching_bookmarks) > 1:
            console.print("\n[yellow]Multiple bookmarks found:[/yellow]")
            _display_compact_list([SearchResult(b) for b in matching_bookmarks])
            raise ValidationError(
                "Please use a longer ID prefix to be more specific"
            )
    matching_bookmarks = []
    for bookmark in manager.bookmarks.values():
        if bookmark.title.lower() == reference.lower():
            matching_bookmarks.append(bookmark)
    
    if len(matching_bookmarks) == 1:
        return matching_bookmarks[0]
    elif len(matching_bookmarks) > 1:
        console.print("\n[yellow]Multiple bookmarks found with the same title:[/yellow]")
        _display_compact_list([SearchResult(b) for b in matching_bookmarks])
        raise ValidationError(
            "Please use the ID to select a specific bookmark"
        )
    console.print("\n[yellow]Available bookmarks:[/yellow]")
    all_bookmarks = [SearchResult(b) for b in manager.bookmarks.values()]
    _display_compact_list(all_bookmarks)
    
    raise BookmarkNotFoundError(
        f"No bookmark found matching '{reference}'. Please use an ID or title from the list above."
    )

@cli.command()
@click.argument('shell', type=click.Choice(['bash', 'zsh', 'powershell']))
@click.option('--print-only', is_flag=True, help='Print integration script without installing')
@click.pass_context
def shell_setup(ctx, shell: str, print_only: bool):
    """Generate or install shell integration scripts."""
    try:
        integration = ShellIntegration()
        
        if print_only:
            script = integration.generate_shell_script(shell, sys.executable)
            console.print(script)
            return
            
        integration.install_shell_integration(shell)
        format_success(f"Shell integration installed for {shell}")
        console.print("\nPlease restart your shell or source the config file to apply changes.")
        
    except Exception as e:
        format_error(str(e))

def _display_bookmark_details(bookmark: Bookmark):
    """Helper function to display bookmark details."""
    table = Table(
        show_header=True,
        header_style=f"bold {COLORS['highlight']}",
        title=f"Bookmark: {bookmark.title}",
        title_style=f"bold {COLORS['primary']}",
        border_style=COLORS['muted'],
        padding=(0, 1)
    )
    table.add_column("ID", style=f"bold {COLORS['accent']}", width=4)
    table.add_column("Title", style="bold white", width=30)
    table.add_column("Command", style=COLORS['accent'], width=40)
    table.add_column("Description", style=COLORS['muted'], width=20)
    table.add_column("Tags", style=COLORS['highlight'], width=15)
    table.add_column("Uses", justify="right", style=COLORS['muted'], width=5)
    table.add_row(
        bookmark.id,
        bookmark.title,
        bookmark.command,
        bookmark.description or "",
        ", ".join(bookmark.tags) if bookmark.tags else "",
        str(bookmark.use_count)
    )
    
    console.print(table)

def _display_search_results(results: List[SearchResult]):
    """Display search results."""
    table = create_table("Search Results")
    table.add_column("ID", style=f"dim {COLORS['muted']}", width=8)
    table.add_column("Title", style="bold white")
    table.add_column("Command", style=COLORS['accent'])
    table.add_column("Tags", style=COLORS['highlight'])
    table.add_column("Uses", justify="right", style=COLORS['muted'])
    
    for result in results:
        bookmark = result.bookmark
        table.add_row(
            str(bookmark.id)[:8],
            bookmark.title,
            formatter.format_command(bookmark.command),
            formatter.format_tags(bookmark.tags),
            str(bookmark.use_count)
        )
    
    console.print(table)

def _highlight_matches(text: str, matches: List[str]) -> str:
    """Highlight matched portions of text."""
    if not text or not matches:  
        return text or ""
        
    highlighted = text
    for match in matches:
        if match:  
            pattern = re.compile(re.escape(match), re.IGNORECASE)
            highlighted = pattern.sub(f"[yellow]{match}[/yellow]", highlighted)
        
    return highlighted 

def _create_table(title: str, show_score: bool = False) -> Table:
    """Create a consistently styled table."""
    table = Table(
        show_header=True,
        header_style="bold magenta",
        title=title,
        title_style="bold blue",
        show_lines=True,  
        padding=(0, 1)    
    )
    table.add_column("ID", style="dim", width=8)
    table.add_column("Title", style="bold", width=30)
    table.add_column("Command", style="cyan", width=40)
    table.add_column("Tags", style="green", width=20)
    table.add_column("Uses", justify="right", width=6)
    if show_score:
        table.add_column("Score", justify="right", width=6)
    
    return table 

def _resolve_bookmark_id(manager: BookmarkManager, bookmark_id: str) -> UUID:
    """Helper function to resolve partial or full bookmark IDs."""
    try:
        return UUID(bookmark_id)
    except ValueError:
        try:
            bookmark = manager.find_bookmark_by_partial_id(bookmark_id)
            if bookmark:
                return bookmark.id
            raise BookmarkNotFoundError(f"No bookmark found with ID starting with '{bookmark_id}'")
        except BookmarkError as e:
            raise BookmarkError(str(e))

@cli.command()
@click.argument('bookmark_id')
@click.option('--title', '-t', help='New title for the bookmark')
@click.option('--command', '-c', help='New command for the bookmark')
@click.option('--description', '-d', help='New description for the bookmark')
@click.option('--tags', help='New comma-separated list of tags')
@click.pass_context
def edit(ctx, bookmark_id: str, title: Optional[str], command: Optional[str], 
         description: Optional[str], tags: Optional[str]):
    """Edit an existing bookmark.
    
    Examples:
        tb edit <id> --title "New Title"
        tb edit <id> --command "new command"
        tb edit <id> --tags "tag1,tag2"
    """
    try:
        manager = ctx.obj.get('manager')
        if not manager:
            raise click.ClickException("Failed to initialize bookmark manager")

        # Validate that at least one field is being edited
        if not any([title, command, description, tags]):
            raise click.ClickException("Please specify at least one field to edit (--title, --command, --description, or --tags)")
        
        try:
            bookmark_id_obj = UUID(bookmark_id)
            bookmark = manager.get_bookmark(bookmark_id_obj)
        except ValueError:
            bookmark = manager.find_bookmark_by_partial_id(bookmark_id)
            if not bookmark:
                raise BookmarkNotFoundError(f"No bookmark found with ID starting with '{bookmark_id}'")

        # Process tags if provided
        tag_list = None
        if tags is not None:
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
            
        # Create update dictionary with only provided fields
        updates = {}
        if title is not None:
            updates['title'] = title.strip()
        if command is not None:
            updates['command'] = command.strip()
        if description is not None:
            updates['description'] = description.strip() if description else None
        if tag_list is not None:
            updates['tags'] = tag_list

        # Update the bookmark
        updated_bookmark = manager.update_bookmark(bookmark.id, **updates)
        click.echo(f"✓ Updated bookmark: {updated_bookmark.title}")
        
    except BookmarkNotFoundError as e:
        raise click.ClickException(str(e))
    except BookmarkError as e:
        raise click.ClickException(f"Failed to update bookmark: {str(e)}")
    except Exception as e:
        raise click.ClickException(f"An unexpected error occurred: {str(e)}") 