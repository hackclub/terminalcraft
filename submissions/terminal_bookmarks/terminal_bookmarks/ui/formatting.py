from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.style import Style
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.syntax import Syntax
from rich import box

from ..core.models import Bookmark
console = Console()
DEFAULT_COLORS = {
    'title': 'bold blue',
    'header': 'bold magenta',
    'success': 'bold green',
    'error': 'bold red',
    'warning': 'bold yellow',
    'highlight': 'bold cyan',
    'dim': 'dim',
    'tag': 'green',
    'id': 'dim blue',
    'command': 'cyan',
}

class OutputFormatter:
    """Handles consistent formatting of terminal output."""
    
    def __init__(self, color_scheme: dict = None, minimal: bool = False):
        self.colors = color_scheme or DEFAULT_COLORS
        self.minimal = minimal
        
    def create_table(self, 
                    title: str,
                    columns: List[str],
                    styles: Optional[List[str]] = None,
                    box_style: Optional[box.Box] = None) -> Table:
        """Create a consistently styled table."""
        if self.minimal:
            box_style = None
        else:
            box_style = box_style or box.ROUNDED
            
        table = Table(
            show_header=True,
            header_style=self.colors['header'],
            title=title,
            title_style=self.colors['title'],
            box=box_style,
            expand=True
        )
        for i, column in enumerate(columns):
            style = styles[i] if styles and i < len(styles) else None
            table.add_column(column, style=style)
            
        return table
    
    def format_command(self, command: str, highlight: Optional[str] = None) -> Text:
        """Format a command with optional highlighting."""
        text = Text(command, style=self.colors['command'])
        if highlight and highlight in command:
            text.highlight_words([highlight], style=self.colors['highlight'])
        return text
    
    def format_tags(self, tags: List[str], highlight: Optional[List[str]] = None) -> Text:
        """Format tags with optional highlighting."""
        if not tags:
            return Text("")
            
        text = Text()
        for i, tag in enumerate(tags):
            if i > 0:
                text.append(", ")
            if highlight and tag in highlight:
                text.append(tag, style=self.colors['highlight'])
            else:
                text.append(tag, style=self.colors['tag'])
        return text
    
    def show_success(self, message: str):
        """Display a success message."""
        if self.minimal:
            console.print(message)
        else:
            console.print(f"✓ {message}", style=self.colors['success'])
    
    def show_error(self, message: str):
        """Display an error message."""
        if self.minimal:
            console.print(f"Error: {message}")
        else:
            console.print(f"[{self.colors['error']}]Error:[/] {message}")
    
    def show_warning(self, message: str):
        """Display a warning message."""
        if self.minimal:
            console.print(f"Warning: {message}")
        else:
            console.print(f"[{self.colors['warning']}]Warning:[/] {message}")
            
    def create_help_panel(self, title: str, content: str) -> Panel:
        """Create a help panel with formatted content."""
        if self.minimal:
            return Text(f"{title}\n\n{content}")
            
        return Panel(
            content,
            title=title,
            border_style=self.colors['title'],
            padding=(1, 2)
        )

    def show_command_preview(self, command: str, bookmark: Bookmark):
        """Show a formatted command preview."""
        if self.minimal:
            console.print(f"{bookmark.title}: {command}")
            return
            
        panel = Panel(
            f"[bold]{bookmark.title}[/bold]\n\n"
            f"[cyan]{command}[/cyan]",
            title="Command Preview",
            border_style=self.colors['warning']
        )
        console.print(panel)

class InteractivePrompts:
    """Handles interactive user input and menus."""
    
    @staticmethod
    def confirm(message: str, default: bool = False) -> bool:
        """Ask for user confirmation."""
        return Confirm.ask(message, default=default)
    
    @staticmethod
    def select_from_list(options: List[str], 
                        prompt: str = "Select an option",
                        default: Optional[int] = None) -> int:
        """Show an interactive selection menu."""
        for i, option in enumerate(options, 1):
            console.print(f"{i}. {option}")
        
        while True:
            try:
                choice = Prompt.ask(
                    prompt,
                    default=str(default) if default else None
                )
                index = int(choice) - 1
                if 0 <= index < len(options):
                    return index
                console.print("Invalid selection. Please try again.", style="red")
            except ValueError:
                console.print("Please enter a number.", style="red")
    
    @staticmethod
    def paginate(items: List[Any], 
                page_size: int = 10,
                renderer: callable = str,
                title: str = "Results") -> None:
        """Display items with interactive pagination."""
        total_pages = (len(items) + page_size - 1) // page_size
        current_page = 1
        
        while True:
            start_idx = (current_page - 1) * page_size
            end_idx = min(start_idx + page_size, len(items))
            page_items = items[start_idx:end_idx]
            
            console.clear()
            console.print(f"{title} (Page {current_page}/{total_pages})", style="bold blue")
            
            for item in page_items:
                console.print(renderer(item))
            
            if total_pages > 1:
                console.print("\nNavigation: [n]ext, [p]revious, [q]uit", style="dim")
                key = Prompt.ask("").lower()
                
                if key == 'n' and current_page < total_pages:
                    current_page += 1
                elif key == 'p' and current_page > 1:
                    current_page -= 1
                elif key == 'q':
                    break
            else:
                Prompt.ask("\nPress Enter to continue")
                break 