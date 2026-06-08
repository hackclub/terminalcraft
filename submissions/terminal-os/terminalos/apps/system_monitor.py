"""System monitor application."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, ProgressBar
from textual.containers import Vertical, Horizontal
from textual.binding import Binding
import psutil


class SystemMonitorApp(Screen):
    """System monitoring application."""
    
    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("r", "refresh", "Refresh"),
    ]
    
    def __init__(self):
        super().__init__()
        self.set_interval(2.0, self.update_stats)
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Static("📊 System Monitor", classes="title"),
            Horizontal(
                Vertical(
                    Static("💻 CPU Usage", classes="label"),
                    ProgressBar(total=100, id="cpu_bar"),
                    Static("💾 Memory Usage", classes="label"),
                    ProgressBar(total=100, id="memory_bar"),
                    Static("💿 Disk Usage", classes="label"),
                    ProgressBar(total=100, id="disk_bar"),
                    classes="stats-panel"
                ),
                Vertical(
                    Static("📈 System Info", classes="label"),
                    Static("", id="system_info", classes="info-panel"),
                    classes="info-section"
                ),
                classes="monitor-content"
            ),
            classes="system-monitor"
        )
        yield Footer()
    
    def update_stats(self) -> None:
        """Update system statistics."""
        try:
            # CPU Usage
            cpu_percent = psutil.cpu_percent()
            cpu_bar = self.query_one("#cpu_bar")
            cpu_bar.progress = cpu_percent
            
            # Memory Usage
            memory = psutil.virtual_memory()
            memory_bar = self.query_one("#memory_bar")
            memory_bar.progress = memory.percent
            
            # Disk Usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_bar = self.query_one("#disk_bar")
            disk_bar.progress = disk_percent
            
            # System Info
            info = f"""🖥️  CPU: {psutil.cpu_count()} cores
💾 RAM: {self.format_bytes(memory.total)}
💿 Disk: {self.format_bytes(disk.total)}
⚡ Load: {cpu_percent:.1f}%
🔋 Available: {self.format_bytes(memory.available)}"""
            
            self.query_one("#system_info").update(info)
            
        except Exception as e:
            self.notify(f"Error updating stats: {e}")
    
    def format_bytes(self, bytes_val: int) -> str:
        """Format bytes in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} PB"
    
    def action_close(self) -> None:
        """Close system monitor."""
        self.dismiss()
    
    def action_refresh(self) -> None:
        """Force refresh stats."""
        self.update_stats()