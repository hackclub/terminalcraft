"""
AetherTap Terminal Interface Manager - Textual Version
Handles the multi-pane textual interface for the Signal Cartographer
"""

import asyncio
from typing import List, Optional, Dict, Any

from .ui.layout import AetherTapApp
from .ui.panes import SpectrumPane, SignalFocusPane, CartographyPane, DecoderPane, LogPane

try:
    from .signal_art import SignalArt
except ImportError:
    # Fallback if signal_art is not available
    class SignalArt:
        def get_signal_signature(self, sig_type): return ["[Signal Pattern]"]
        def get_analysis_display(self, signal): return [f"Analysis: {signal.id}"]
        def generate_spectrum_display(self, signals, freq_range): return ["Spectrum Display"]


class AetherTapTextual:
    """
    The AetherTap terminal interface using Textual - manages the multi-pane display
    """
    
    def __init__(self, game_controller=None):
        self.game_controller = game_controller
        self.app = AetherTapApp(game_controller)
        self.focused_signal = None
        self.current_sector = "Alpha-1"
        self.frequency_range = (100, 200)
        self.signals = []
          # Initialize signal art system
        self.signal_art = SignalArt()
        
    async def run(self):
        """Run the Textual application"""
        await self.app.run_async()
    def run_sync(self):
        """Run the application synchronously"""
        self.app.run()
    
    def show_startup_sequence(self):
        """Display startup sequence in the log pane"""
        # This will be handled by the screen's _initialize_panes method
        pass
    
    def show_error(self, error_msg: str):
        """Display an error message in the log pane"""
        screen = self.app.get_current_screen()
        if screen and screen.aethertap_layout and screen.aethertap_layout.log_pane:
            screen.aethertap_layout.log_pane.add_log_entry(f"[red]ERROR: {error_msg}[/red]")
    
    def get_panes(self) -> Dict[str, Any]:
        """Get references to all panes"""
        screen = self.app.get_current_screen()
        if screen and screen.aethertap_layout:
            return {
                'spectrum': screen.aethertap_layout.spectrum_pane,
                'signal_focus': screen.aethertap_layout.signal_focus_pane,
                'cartography': screen.aethertap_layout.cartography_pane,
                'decoder': screen.aethertap_layout.decoder_pane,
                'log': screen.aethertap_layout.log_pane,
                'command_input': screen.aethertap_layout.command_input
            }
        return {}
    
    def update_spectrum(self, signals: List[Any], freq_range: tuple = None, noise: float = 0.1):
        """Update the spectrum analyzer display"""
        self.signals = signals
        if freq_range:
            self.frequency_range = freq_range
            
        panes = self.get_panes()
        if 'spectrum' in panes and panes['spectrum']:
            panes['spectrum'].update_spectrum(signals, self.frequency_range, noise)
    
    def focus_signal(self, signal: Any):
        """Focus on a specific signal in the SFD pane"""
        self.focused_signal = signal
        panes = self.get_panes()
        if 'signal_focus' in panes and panes['signal_focus']:
            panes['signal_focus'].focus_signal(signal)
    
    def update_map(self, sector: str, locations: Dict[str, Any] = None, signals: List[Any] = None):
        """Update the cartography display"""
        self.current_sector = sector
        panes = self.get_panes()
        if 'cartography' in panes and panes['cartography']:
            panes['cartography'].update_map(sector, locations, signals)
    
    def start_analysis(self, tool_name: str, signal: Any = None):
        """Start analysis in the decoder pane"""
        if signal is None:
            signal = self.focused_signal
            
        panes = self.get_panes()
        if 'decoder' in panes and panes['decoder']:
            panes['decoder'].start_analysis(tool_name, signal)
    
    def add_log_entry(self, entry: str):
        """Add an entry to the log pane"""
        panes = self.get_panes()
        if 'log' in panes and panes['log']:
            panes['log'].add_log_entry(entry)
    
    def show_error(self, error_message: str):
        """Display an error message"""
        self.add_log_entry(f"ERROR: {error_message}")
    
    def show_startup_sequence(self):
        """Display the startup sequence"""
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
            self.add_log_entry(message)
    
    def shutdown(self):
        """Cleanly shutdown the interface"""
        if self.app:
            self.app.exit()
    
    # Compatibility methods for existing code
    def initialize(self):
        """Initialize the interface (compatibility method)"""
        # This is handled automatically in textual
        pass
    
    def update_display(self):
        """Update the display (compatibility method)"""
        # Textual handles this automatically through reactive updates
        pass
    
    def handle_input(self, key: int) -> Optional[str]:
        """Handle input (compatibility method)"""
        # Textual handles input through its own event system
        # This method is kept for compatibility but not used
        return None
