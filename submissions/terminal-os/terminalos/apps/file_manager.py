"""File manager application."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, DirectoryTree, Static
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from pathlib import Path


class FileManagerApp(Screen):
    """File manager application."""
    
    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("f5", "refresh", "Refresh"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            DirectoryTree(str(Path.home()), id="file_tree"),
            Vertical(
                Static("📁 File Details", classes="panel-title"),
                Static("Select a file to see details", id="file_details"),
                classes="details-panel"
            ),
            classes="file-manager"
        )
        yield Footer()
    
    def on_directory_tree_file_selected(self, event) -> None:
        """Handle file selection."""
        file_path = Path(event.path)
        details = f"📄 {file_path.name}\n📍 {file_path.parent}\n📊 {self.get_file_size(file_path)}"
        self.query_one("#file_details").update(details)
    
    def get_file_size(self, path: Path) -> str:
        """Get formatted file size."""
        try:
            size = path.stat().st_size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} TB"
        except:
            return "Unknown"
    
    def action_close(self) -> None:
        """Close file manager."""
        self.dismiss()
    
    def action_refresh(self) -> None:
        """Refresh file tree."""
        tree = self.query_one("#file_tree")
        tree.reload()