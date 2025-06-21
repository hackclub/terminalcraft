import typer
from rich.console import Console
from rich.panel import Panel
import config

console = Console()

def closeWithError(error_description=f"Something's gone wrong.", error_code: int = 10, exception_object = None):
    if config.debugMode and exception_object:
        raise exception_object
    if error_code == 10:
        border_color = "red"
    else:
        border_color = "yellow"
    console.print(Panel(error_description, border_style=border_color, title="Ouch!", title_align="left"))
    console.print((f"[dim]Error code {error_code}.[/dim]"))
    raise typer.Exit(code=error_code)