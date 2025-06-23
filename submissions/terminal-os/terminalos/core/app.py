"""Main TerminalOS application."""

import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Container, Vertical, Horizontal
from textual.binding import Binding
from textual.screen import ModalScreen
from rich.text import Text
from rich.panel import Panel
from rich.console import Console

try:
    import pyfiglet
    PYFIGLET_AVAILABLE = True
except ImportError:
    PYFIGLET_AVAILABLE = False


class BootScreen(ModalScreen):
    """Boot screen with TerminalOS logo."""
    
    def compose(self) -> ComposeResult:
        boot_text = Text()
        
        if PYFIGLET_AVAILABLE:
            try:
                logo = pyfiglet.figlet_format("TerminalOS", font="slant")
                boot_text.append(logo, style="bold cyan")
            except:
                boot_text.append("🖥️  TERMINALOS", style="bold cyan")
                boot_text.append("\n" + "="*50 + "\n", style="cyan")
        else:
            boot_text.append("🖥️  TERMINALOS", style="bold cyan")
            boot_text.append("\n" + "="*50 + "\n", style="cyan")
        
        boot_text.append("\n🚀 Initializing Terminal Operating System...", style="green")
        boot_text.append("\n⚡ Loading desktop environment...", style="yellow")
        boot_text.append("\n✅ System ready!", style="bright_green")
        boot_text.append("\n\n👋 Welcome! Press ENTER to continue", style="dim")
        
        yield Container(
            Static(boot_text, classes="boot-screen"),
            classes="boot-container"
        )
    
    def on_key(self, event) -> None:
        if event.key in ["enter", "escape", "space"]:
            self.dismiss()


class Desktop(Static):
    """Main desktop area with ASCII art wallpaper."""
    
    def __init__(self):
        super().__init__()
        self.update_timer = self.set_interval(5.0, self.update_wallpaper)
    
    def render(self) -> Text:
        """Render desktop wallpaper."""
        wallpaper = Text()
        
        # Header
        wallpaper.append("╔" + "═"*78 + "╗\n", style="blue")
        wallpaper.append("║" + " "*78 + "║\n", style="blue")
        wallpaper.append("║" + "🖥️  TerminalOS Desktop Environment".center(78) + "║\n", style="bold cyan")
        wallpaper.append("║" + " "*78 + "║\n", style="blue")
        wallpaper.append("║" + "Your complete terminal operating system".center(78) + "║\n", style="cyan")
        wallpaper.append("║" + " "*78 + "║\n", style="blue")
        
        # Current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        wallpaper.append("║" + f"🕐 {current_time}".center(78) + "║\n", style="green")
        wallpaper.append("║" + " "*78 + "║\n", style="blue")
        
        # Quick help
        wallpaper.append("║" + "Quick Actions:".center(78) + "║\n", style="bold yellow")
        wallpaper.append("║" + "F1: Help  •  F12: Apps  •  Ctrl+Q: Quit".center(78) + "║\n", style="white")
        wallpaper.append("║" + " "*78 + "║\n", style="blue")
        
        # Available apps
        wallpaper.append("║" + "📱 Available Applications:".center(78) + "║\n", style="bold magenta")
        wallpaper.append("║" + "📁 Files  📝 Editor  🔢 Calculator  📊 Monitor".center(78) + "║\n", style="green")
        wallpaper.append("║" + " "*78 + "║\n", style="blue")
        
        # Footer
        wallpaper.append("║" + "Press F12 to launch applications".center(78) + "║\n", style="dim")
        wallpaper.append("║" + " "*78 + "║\n", style="blue")
        wallpaper.append("╚" + "═"*78 + "╝", style="blue")
        
        return wallpaper
    
    def update_wallpaper(self) -> None:
        """Update wallpaper with current time."""
        self.refresh()


class HelpScreen(ModalScreen):
    """Help screen with keyboard shortcuts and information."""
    
    def compose(self) -> ComposeResult:
        help_text = Text()
        help_text.append("🔧 TerminalOS Help & User Guide\n\n", style="bold cyan")
        
        help_text.append("📋 Keyboard Shortcuts:\n", style="bold yellow")
        help_text.append("  F1      - Show this help screen\n", style="green")
        help_text.append("  F12     - Open application launcher\n", style="green")
        help_text.append("  Ctrl+Q  - Quit TerminalOS\n", style="green")
        help_text.append("  ESC     - Close current dialog/app\n", style="green")
        help_text.append("  Tab     - Navigate between UI elements\n", style="green")
        help_text.append("  Enter   - Select/Activate item\n", style="green")
        
        help_text.append("\n📱 Available Applications:\n", style="bold yellow")
        help_text.append("  📁 File Manager    - Browse and manage files\n", style="green")
        help_text.append("  📝 Text Editor     - Edit text files with syntax highlighting\n", style="green")
        help_text.append("  🔢 Calculator      - Scientific calculator with history\n", style="green")
        help_text.append("  📊 System Monitor  - Real-time system statistics\n", style="green")
        help_text.append("  💻 Terminal        - Command-line interface (coming soon)\n", style="dim")
        help_text.append("  🎵 Music Player    - Audio player (coming soon)\n", style="dim")
        
        help_text.append("\n💡 Tips:\n", style="bold yellow")
        help_text.append("  • Use mouse or keyboard to navigate\n", style="cyan")
        help_text.append("  • Most apps support common shortcuts (Ctrl+S, Ctrl+O, etc.)\n", style="cyan")
        help_text.append("  • Press ESC to return to desktop from any app\n", style="cyan")
        help_text.append("  • Apps remember your settings between sessions\n", style="cyan")
        
        help_text.append("\n🌟 About TerminalOS:\n", style="bold yellow")
        help_text.append("  Version: 1.0.0\n", style="white")
        help_text.append("  Built with: Python + Textual\n", style="white")
        help_text.append("  GitHub: github.com/yourusername/terminalos\n", style="white")
        
        help_text.append("\n" + "─"*60 + "\n", style="dim")
        help_text.append("Press ESC to close this help screen", style="dim")
        
        yield Container(
            Static(help_text, classes="help-screen"),
            classes="help-container"
        )
    
    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss()


class AppLauncher(ModalScreen):
    """Application launcher with app grid."""
    
    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("1", "launch_files", "Files"),
        Binding("2", "launch_editor", "Editor"), 
        Binding("3", "launch_calculator", "Calculator"),
        Binding("4", "launch_monitor", "Monitor"),
        Binding("5", "launch_terminal", "Terminal"),
    ]
    
    def compose(self) -> ComposeResult:
        apps_text = Text()
        apps_text.append("📱 TerminalOS Application Launcher\n\n", style="bold cyan")
        
        # Available apps
        apps_text.append("🟢 Available Applications:\n", style="bold green")
        apps_text.append("  1️⃣  📁 File Manager     - Browse files and directories\n", style="green")
        apps_text.append("  2️⃣  📝 Text Editor      - Edit code and text files\n", style="green")
        apps_text.append("  3️⃣  🔢 Calculator       - Perform calculations\n", style="green")
        apps_text.append("  4️⃣  📊 System Monitor   - View system performance\n", style="green")
        
        # Coming soon
        apps_text.append("\n🟡 Coming Soon:\n", style="bold yellow")
        apps_text.append("  5️⃣  💻 Terminal         - Command-line interface\n", style="dim")
        apps_text.append("  6️⃣  🎵 Music Player     - Audio playback\n", style="dim")
        apps_text.append("  7️⃣  🌐 Web Browser      - Browse the web\n", style="dim")
        apps_text.append("  8️⃣  📧 Email Client     - Manage emails\n", style="dim")
        
        apps_text.append("\n" + "─"*50 + "\n", style="dim")
        apps_text.append("💡 Press number key to launch app or ESC to close", style="cyan")
        
        yield Container(
            Static(apps_text, classes="app-launcher"),
            classes="launcher-container"
        )
    
    def action_launch_files(self) -> None:
        """Launch file manager."""
        try:
            from ..apps.file_manager import FileManagerApp
            self.dismiss()
            self.app.push_screen(FileManagerApp())
        except Exception as e:
            self.app.notify(f"Error launching File Manager: {e}")
    
    def action_launch_editor(self) -> None:
        """Launch text editor."""
        try:
            from ..apps.text_editor import TextEditorApp
            self.dismiss()
            self.app.push_screen(TextEditorApp())
        except Exception as e:
            self.app.notify(f"Error launching Text Editor: {e}")
    
    def action_launch_calculator(self) -> None:
        """Launch calculator."""
        try:
            from ..apps.calculator import CalculatorApp
            self.dismiss()
            self.app.push_screen(CalculatorApp())
        except Exception as e:
            self.app.notify(f"Error launching Calculator: {e}")
    
    def action_launch_monitor(self) -> None:
        """Launch system monitor."""
        try:
            from ..apps.system_monitor import SystemMonitorApp
            self.dismiss() 
            self.app.push_screen(SystemMonitorApp())
        except Exception as e:
            self.app.notify(f"Error launching System Monitor: {e}")
    
    def action_launch_terminal(self) -> None:
        """Launch terminal (placeholder)."""
        self.dismiss()
        self.app.notify("💻 Terminal app coming soon! Stay tuned for updates.")


class TerminalOSApp(App):
    """Main TerminalOS application class."""
    
    CSS = """
    /* Boot Screen Styles */
    .boot-container {
        align: center middle;
    }
    
    .boot-screen {
        width: 90;
        height: 25;
        text-align: center;
        border: solid $primary;
        background: $surface;
        padding: 2;
    }
    
    /* Help Screen Styles */
    .help-container {
        align: center middle;
    }
    
    .help-screen {
        width: 85;
        height: 35;
        border: solid $accent;
        background: $surface;
        padding: 2;
        overflow-y: scroll;
    }
    
    /* App Launcher Styles */
    .launcher-container {
        align: center middle;
    }
    
    .app-launcher {
        width: 75;
        height: 30;
        text-align: center;
        border: solid $success;
        background: $surface;
        padding: 2;
    }
    
    /* Desktop Styles */
    .desktop {
        height: 1fr;
        background: $surface;
        text-align: center;
        padding: 1;
    }
    
    /* Common Styles */
    Static {
        text-align: center;
    }
    """
    
    TITLE = "TerminalOS"
    SUB_TITLE = "v1.0.0 - Your Terminal Operating System"
    
    BINDINGS = [
        Binding("f1", "show_help", "Help", show=True),
        Binding("f12", "launch_apps", "Apps", show=True),
        Binding("ctrl+q", "quit_app", "Quit", show=True),
        Binding("ctrl+r", "refresh_desktop", "Refresh"),
    ]
    
    def __init__(self):
        super().__init__()
        self.options: Dict[str, Any] = {}
        self.startup_time = datetime.now()
    
    def configure(self, options: Dict[str, Any]):
        """Configure app with startup options."""
        self.options = options
        
        # Apply debug mode
        if options.get('debug'):
            self.debug = True
    
    def compose(self) -> ComposeResult:
        """Compose the main application UI."""
        yield Header(
            show_clock=True, 
            name="🖥️ TerminalOS",
            icon="🖥️"
        )
        yield Container(
            Desktop(),
            classes="desktop"
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize app when mounted."""
        # Show welcome message
        self.notify("🚀 Welcome to TerminalOS! Press F12 for apps, F1 for help.")
        
        # Show boot screen unless disabled
        if not self.options.get('no_boot', False):
            self.call_after_refresh(self.show_boot_screen)
    
    def show_boot_screen(self) -> None:
        """Show the boot screen."""
        self.push_screen(BootScreen())
    
    def action_show_help(self) -> None:
        """Show help screen."""
        self.push_screen(HelpScreen())
    
    def action_launch_apps(self) -> None:
        """Show application launcher."""
        self.push_screen(AppLauncher())
    
    def action_quit_app(self) -> None:
        """Quit TerminalOS with confirmation."""
        self.exit(message="👋 Thanks for using TerminalOS!")
    
    def action_refresh_desktop(self) -> None:
        """Refresh the desktop."""
        self.refresh()
        self.notify("🔄 Desktop refreshed!")
    
    def on_key(self, event) -> None:
        """Handle global key events."""
        # You can add global shortcuts here
        pass