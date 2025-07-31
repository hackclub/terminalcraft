"""
Layout management for the AetherTap interface
"""

import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static
from textual.screen import Screen
from textual.binding import Binding

from .panes import SpectrumPane, SignalFocusPane, CartographyPane, DecoderPane, LogPane
from .input_handler import CommandInput, AetherTapInputHandler
from .colors import AetherTapColors

class AetherTapLayout(Container):
    """Main layout container for the AetherTap interface"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spectrum_pane = None
        self.signal_focus_pane = None
        self.cartography_pane = None
        self.decoder_pane = None
        self.log_pane = None
        self.command_input = None
    
    def compose(self) -> ComposeResult:
        """Compose the layout"""
        # Top row: Spectrum and Signal Focus
        with Horizontal(id="top_row"):
            self.spectrum_pane = SpectrumPane(id="spectrum_pane")
            yield self.spectrum_pane
            self.signal_focus_pane = SignalFocusPane(id="signal_focus_pane")
            yield self.signal_focus_pane
        
        # Middle row: Cartography and Decoder
        with Horizontal(id="middle_row"):
            self.cartography_pane = CartographyPane(id="cartography_pane")
            yield self.cartography_pane
            self.decoder_pane = DecoderPane(id="decoder_pane")
            yield self.decoder_pane
        
        # Bottom section: Log and Command Input
        with Vertical(id="bottom_section"):
            self.log_pane = LogPane(id="log_pane")
            yield self.log_pane
            self.command_input = CommandInput(id="command_input")
            yield self.command_input

class AetherTapScreen(Screen):
    """Main screen for the AetherTap interface"""
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+h", "help", "Help"),
        Binding("f1", "focus_spectrum", "Focus Spectrum"),
        Binding("f2", "focus_signal", "Focus Signal"),
        Binding("f3", "focus_map", "Focus Map"),
        Binding("f4", "focus_decoder", "Focus Decoder"),
        Binding("f5", "focus_log", "Focus Log"),
    ]
    
    def __init__(self, game_controller=None, **kwargs):
        super().__init__(**kwargs)
        self.game_controller = game_controller
        self.aethertap_layout = None
    
    def compose(self) -> ComposeResult:
        """Compose the screen"""
        yield Header(show_clock=True)
        self.aethertap_layout = AetherTapLayout()
        yield self.aethertap_layout
        yield Footer()
    
    async def on_mount(self) -> None:
        """Initialize the screen after mounting"""
        # Set window title
        self.title = "AetherTap - Signal Cartographer"
        
        # Initialize panes with default content
        await self._initialize_panes()
        
        # Set up command input after panes are initialized
        if self.aethertap_layout and self.aethertap_layout.command_input:
            self.aethertap_layout.command_input.command_handler = self._handle_command
    
    def _handle_command(self, command: str):
        """Handle command input"""
        parts = command.lower().split()
        if not parts:
            return
            
        command_name = parts[0]
        
        # Handle basic commands
        if command_name in ['quit', 'exit', 'q']:
            self.app.exit()
        elif command_name == 'help':
            self._show_help()
        elif command_name == 'clear':
            self._clear_logs()
        else:
            # Pass to game's command parser
            if self.game_controller:
                result = self.game_controller.process_command(command)
                if result and self.aethertap_layout and self.aethertap_layout.log_pane:
                    self.aethertap_layout.log_pane.add_log_entry(result)
            else:
                if self.aethertap_layout and self.aethertap_layout.log_pane:
                    self.aethertap_layout.log_pane.add_log_entry(f"Unknown command: {command_name}. Type 'help' for available commands.")
    
    def _show_help(self):
        """Display help information"""
        if self.aethertap_layout and self.aethertap_layout.log_pane:
            help_text = [
                "",
                "Available Commands:",
                "  SCAN [sector] [freq_range] - Scan for signals",
                "  FOCUS [signal_id] - Focus on a specific signal", 
                "  ANALYZE [signal_id] [tool] - Analyze signal with tool",
                "  MAP [sector] - Display sector map",
                "  HELP - Show this help",
                "  CLEAR - Clear log",
                "  QUIT - Exit the application",
                ""
            ]
            for line in help_text:
                self.aethertap_layout.log_pane.add_log_entry(line)
    
    def _clear_logs(self):
        """Clear the log pane"""
        if self.aethertap_layout and self.aethertap_layout.log_pane and self.aethertap_layout.log_pane.content_widget:
            self.aethertap_layout.log_pane.content_widget.clear()
            self.aethertap_layout.log_pane.log_entries.clear()
            self.aethertap_layout.log_pane.add_log_entry("Log cleared.")

    async def _initialize_panes(self):
        """Initialize all panes with default content"""
        if self.aethertap_layout:
            # Show startup sequence in log
            if self.aethertap_layout.log_pane:
                startup_messages = [
                    "=" * 60,
                    "  THE SIGNAL CARTOGRAPHER: ECHOES FROM THE VOID",
                    "  AetherTap Terminal Interface v1.1",
                    "=" * 60,
                    "",
                    "Initializing quantum resonance chambers...",
                    "Calibrating signal detection arrays...",
                    "Loading frequency databases...",
                    "AetherTap ready for operation.",
                    "",
                    "Type 'help' for available commands.",
                    "Press F1-F5 to focus different panes.",
                    "Use Ctrl+C to exit."
                ]
                
                for message in startup_messages:
                    self.aethertap_layout.log_pane.add_log_entry(message)
            
            # Initialize spectrum pane
            if self.aethertap_layout.spectrum_pane:
                self.aethertap_layout.spectrum_pane.update_spectrum([], (100, 200))
            
            # Initialize cartography pane
            if self.aethertap_layout.cartography_pane:
                self.aethertap_layout.cartography_pane.update_map("Alpha-1")
            
            # Initialize decoder pane
            if self.aethertap_layout.decoder_pane:
                self.aethertap_layout.decoder_pane.update_content(["No active analysis tool"])

class AetherTapApp(App):
    """Main Textual application for AetherTap"""
    
    CSS = """
    Screen {
        background: #0d1117;
    }
    
    Container {
        border: solid #30363d;
        margin: 1;
        padding: 1;
    }
    
    .pane-title {
        background: #21262d;
        height: 1;
        text-align: center;
        border-bottom: solid #30363d;
    }
    
    RichLog {
        background: #0d1117;
        color: #c9d1d9;
        border: none;
        scrollbar-background: #21262d;
        scrollbar-color: #58a6ff;
    }
    
    #top_row, #middle_row {
        height: 40%;
    }
    
    #bottom_section {
        height: 20%;
    }
    
    #spectrum_pane, #signal_focus_pane, #cartography_pane, #decoder_pane {
        width: 50%;
    }
    
    #log_pane {
        height: 80%;
    }
    
    #command_input {
        height: 20%;
        border: solid #58a6ff;
    }
    
    Input {
        background: #0d1117;
        color: #c9d1d9;
    }
    
    Header {
        background: #21262d;
        color: #7c3aed;
    }
    
    Footer {
        background: #21262d;
        color: #8b949e;
    }
    """
    
    def __init__(self, game_controller=None, **kwargs):
        super().__init__(**kwargs)
        self.game_controller = game_controller
    
    async def on_mount(self) -> None:
        """Set up the application"""
        # Push the main screen
        await self.push_screen(AetherTapScreen(self.game_controller))
    
    def get_current_screen(self) -> AetherTapScreen:
        """Get the current AetherTap screen"""
        return self.screen
