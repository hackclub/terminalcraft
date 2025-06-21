"""
UI framework for Peeky.

This module provides a consistent UI framework with styled components.
"""

from typing import Dict, List, Optional, Union, Callable
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.text import Text
from rich.box import ROUNDED, DOUBLE, HEAVY, DOUBLE_EDGE
from rich.style import Style
from rich.padding import Padding

THEME = {
    "app_title": "bold bright_magenta",
    "panel_border": "bright_blue",
    "title": "bold bright_magenta",
    "section_title": "bold cyan",
    "label": "bright_white",
    "value_highlight": "bright_green",
    "input": "bright_cyan",
    "success": "bright_green",
    "warning": "bright_yellow",
    "error": "bright_red",
    "info": "bright_blue",
    "dim": "dim",
    "port": "cyan",
    "process": "bright_blue",
    "pid": "magenta",
    "header": "bold bright_white on blue",
    "command": "bright_white",
}

console = Console()


def app_header(title: str = "Peeky", subtitle: str = "A Minimal Port & Process Inspector") -> Panel:
    """
    Create a styled header for the application.
    
    Args:
        title: The main title
        subtitle: The subtitle
        
    Returns:
        Rich Panel object
    """
    content = Text()
    content.append("✨ ", style=THEME["panel_border"])
    content.append(title, style=THEME["app_title"])
    content.append(" ✨", style=THEME["panel_border"])
    
    if subtitle:
        content.append("\n")
        content.append(subtitle, style=THEME["info"])
    
    panel = Panel(
        content,
        box=DOUBLE_EDGE,
        border_style=THEME["panel_border"],
        expand=False,
        padding=(1, 2)
    )
    
    return panel


def styled_panel(
    content: Union[str, Text, Table],
    title: Optional[str] = None,
    style: str = "panel_border",
    box_style = ROUNDED,
    padding: tuple = (1, 2)
) -> Panel:
    """
    Create a styled panel.
    
    Args:
        content: The panel content
        title: Optional panel title
        style: Style name from THEME
        box_style: Box style from rich.box
        padding: Padding as (vertical, horizontal)
        
    Returns:
        Rich Panel object
    """
    return Panel(
        content,
        title=title,
        title_align="center",
        border_style=THEME[style],
        box=box_style,
        padding=padding
    )


def styled_prompt(
    prompt: str,
    default: str = "",
    password: bool = False,
    choices: Optional[List[str]] = None
) -> str:
    """
    Create a styled prompt for user input.
    
    Args:
        prompt: The prompt text
        default: Default value
        password: Whether this is a password input
        choices: Optional list of valid choices
        
    Returns:
        User input string
    """
    return Prompt.ask(
        f"[{THEME['label']}]{prompt}[/{THEME['label']}]",
        default=default,
        password=password,
        choices=choices
    )


def styled_confirm(prompt: str, default: bool = False) -> bool:
    """
    Create a styled confirmation prompt.
    
    Args:
        prompt: The prompt text
        default: Default value
        
    Returns:
        Boolean response
    """
    return Confirm.ask(
        f"[{THEME['label']}]{prompt}[/{THEME['label']}]",
        default=default
    )


def styled_input_panel(
    title: str,
    prompt_text: str,
    description: Optional[str] = None,
    default: str = "",
) -> Panel:
    """
    Create a styled input panel similar to the DreamShell interface.
    
    Args:
        title: The panel title
        prompt_text: The prompt text placeholder
        description: Optional description
        default: Default value
        
    Returns:
        Rich Panel object
    """
    content = Text()
    
    if description:
        content.append(f"{description}\n\n", style=THEME["info"])
    
    content.append(prompt_text, style=THEME["input"])
    
    panel = Panel(
        content,
        title=title,
        title_align="right",
        border_style=THEME["panel_border"],
        box=ROUNDED,
        padding=(1, 2)
    )
    
    return panel


def create_app_layout(title: str = "Peeky") -> Layout:
    """
    Create a full-screen application layout.
    
    Args:
        title: The application title
        
    Returns:
        Rich Layout object
    """
    layout = Layout()
    
    layout.split(
        Layout(name="header", size=3),
        Layout(name="body", ratio=1),
        Layout(name="footer", size=1)
    )
    
    layout["header"].update(app_header())
    
    footer_text = Text("Press Ctrl+C to exit", style=THEME["dim"])
    layout["footer"].update(Padding(footer_text, (0, 1)))
    
    return layout


def print_styled_error(message: str, title: str = "Error") -> None:
    """
    Print a styled error message.
    
    Args:
        message: The error message
        title: The error title
    """
    console.print(styled_panel(
        message,
        title=title,
        style="error"
    ))


def print_styled_success(message: str, title: str = "Success") -> None:
    """
    Print a styled success message.
    
    Args:
        message: The success message
        title: The success title
    """
    console.print(styled_panel(
        message,
        title=title,
        style="success"
    ))


def print_styled_info(message: str, title: str = "Information") -> None:
    """
    Print a styled info message.
    
    Args:
        message: The info message
        title: The title
    """
    console.print(styled_panel(
        message,
        title=title,
        style="info"
    ))


def format_label_value(label: str, value: str, label_style: str = "label", value_style: str = "value_highlight") -> Text:
    """
    Format a label-value pair with consistent styling.
    
    Args:
        label: The label text
        value: The value text
        label_style: Style for the label
        value_style: Style for the value
        
    Returns:
        Formatted Text object
    """
    text = Text()
    text.append(f"{label}: ", style=THEME[label_style])
    text.append(f"{value}", style=THEME[value_style])
    return text 