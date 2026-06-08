"""Text editor application."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, TextArea, Static
from textual.containers import Horizontal, Vertical
from textual.binding import Binding


class TextEditorApp(Screen):
    """Text editor application."""
    
    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+o", "open", "Open"),
    ]
    
    def __init__(self):
        super().__init__()
        self.current_file = None
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            TextArea("# Welcome to TerminalOS Text Editor\n\nStart typing...", id="editor"),
            Vertical(
                Static("📝 Editor Info", classes="panel-title"),
                Static("New Document", id="file_info"),
                Static("Lines: 3\nWords: 7\nChars: 45", id="stats"),
                classes="editor-sidebar"
            ),
            classes="text-editor"
        )
        yield Footer()
    
    def on_text_area_changed(self, event) -> None:
        """Update statistics when text changes."""
        content = event.text_area.text
        lines = len(content.split('\n'))
        words = len(content.split())
        chars = len(content)
        
        stats = f"Lines: {lines}\nWords: {words}\nChars: {chars}"
        self.query_one("#stats").update(stats)
    
    def action_close(self) -> None:
        """Close text editor."""
        self.dismiss()
    
    def action_save(self) -> None:
        """Save current document."""
        self.notify("Save functionality coming soon!")
    
    def action_open(self) -> None:
        """Open document."""
        self.notify("Open functionality coming soon!")