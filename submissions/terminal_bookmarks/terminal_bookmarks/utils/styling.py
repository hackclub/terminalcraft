"""Styling constants and utilities for Terminal Bookmarks."""
from rich.theme import Theme
from rich.console import Console
from rich.style import Style
from rich.table import Table
from rich.panel import Panel
from typing import Optional, List, Any, Dict

COLORS = {
    'primary': '#7aa2f7',
    'success': '#9ece6a',
    'warning': '#e0af68', 
    'error': '#f7768e',
    'muted': '#565f89',
    'highlight': '#bb9af7',
    'accent': '#7dcfff'
}

class OutputFormatter:
    """Format output with consistent styling."""
    def __init__(self, minimal: bool = False, color_scheme: Optional[Dict[str, str]] = None):
        self.minimal = minimal
        self.color_scheme = color_scheme or COLORS

    def format_command(self, command: str) -> str:
        """Format a command with proper styling."""
        if self.minimal:
            return command
        return f"[{self.color_scheme['accent']}]{command}[/{self.color_scheme['accent']}]"

    def format_tags(self, tags: List[str]) -> str:
        """Format tags with proper styling."""
        if not tags:
            return ""
        if self.minimal:
            return ", ".join(tags)
        return ", ".join(f"[{self.color_scheme['highlight']}]{tag}[/{self.color_scheme['highlight']}]" 
                        for tag in tags)

formatter = OutputFormatter()

THEME = Theme({
    'header': Style(color=COLORS['primary'], bold=True),
    'success': Style(color=COLORS['success']),
    'warning': Style(color=COLORS['warning']),
    'error': Style(color=COLORS['error']),
    'muted': Style(color=COLORS['muted']),
    'tag': Style(color=COLORS['highlight'], italic=True),
    'command': Style(color=COLORS['accent'], italic=True),
    'title': Style(color='white', bold=True),
})

console = Console(theme=THEME)

def create_table(title: str, show_header: bool = True) -> Table:
    """Create a consistently styled table."""
    return Table(
        title=title,
        title_style=f"bold {COLORS['primary']}",
        header_style=f"bold {COLORS['highlight']}",
        border_style=COLORS['muted'],
        show_header=show_header,
        box=None,
        padding=(0, 1),
        show_lines=True
    )

def format_bookmark_table(bookmarks: List[Any], detailed: bool = False) -> Table:
    """Create a formatted table for bookmarks."""
    table = create_table("Terminal Bookmarks")
    table.add_column("ID", style=f"dim {COLORS['muted']}", width=8)
    table.add_column("Title", style="bold white")
    table.add_column("Command", style=COLORS['accent'])
    table.add_column("Tags", style=COLORS['highlight'])
    if detailed:
        table.add_column("Description", style=COLORS['muted'])
        table.add_column("Last Used", style=COLORS['muted'])
    table.add_column("Uses", justify="right", style=COLORS['muted'])

    for bookmark in bookmarks:
        row = [
            str(bookmark.id)[:8],
            bookmark.title,
            bookmark.command,
            ", ".join(bookmark.tags) if bookmark.tags else "",
        ]
        if detailed:
            row.extend([
                bookmark.description or "",
                bookmark.last_used.strftime("%Y-%m-%d %H:%M") if bookmark.last_used else "Never",
            ])
        row.append(str(bookmark.use_count))
        table.add_row(*row)

    return table

def format_bookmark_details(bookmark: Any) -> Panel:
    """Create a formatted panel for bookmark details."""
    content = [
        f"[bold white]{bookmark.title}[/bold white]",
        f"[dim]ID: {str(bookmark.id)[:8]}[/dim]",
        f"[{COLORS['accent']}]Command: {bookmark.command}[/{COLORS['accent']}]",
        f"Tags: [{COLORS['highlight']}]{', '.join(bookmark.tags) if bookmark.tags else 'None'}[/{COLORS['highlight']}]",
        f"Description: {bookmark.description or 'None'}",
        f"Created: {bookmark.created_at.strftime('%Y-%m-%d %H:%M')}",
        f"Last Used: {bookmark.last_used.strftime('%Y-%m-%d %H:%M') if bookmark.last_used else 'Never'}",
        f"Use Count: {bookmark.use_count}"
    ]
    
    return Panel(
        "\n".join(content),
        title="Bookmark Details",
        border_style=COLORS['primary'],
        padding=(1, 2)
    )

def format_success(message: str) -> None:
    """Print a success message."""
    console.print(f"✓ {message}", style=f"bold {COLORS['success']}")

def format_error(message: str, help_text: Optional[str] = None) -> None:
    """Print an error message with optional help text."""
    console.print(f"✗ Error: {message}", style=f"bold {COLORS['error']}")
    if help_text:
        console.print(f"💡 {help_text}", style=COLORS['muted'])

def format_warning(message: str, suggestion: Optional[str] = None) -> None:
    """Print a warning message with optional suggestion."""
    console.print(f"! {message}", style=f"bold {COLORS['warning']}")
    if suggestion:
        console.print(f"Tip: {suggestion}", style=COLORS['muted'])

def format_tip(message: str) -> None:
    """Print a tip message."""
    console.print(f"💡 {message}", style=COLORS['muted']) 