"""
AetherTap Terminal Interface Manager
Handles the multi-pane curses interface for the Signal Cartographer
"""

try:
    import curses
    CURSES_AVAILABLE = True
except ImportError:
    CURSES_AVAILABLE = False

import time
from typing import List, Optional, Dict, Any

try:
    from .signal_art import SignalArt
except ImportError:
    # Fallback if signal_art is not available
    class SignalArt:
        def get_signal_signature(self, sig_type): return ["[Signal Pattern]"]
        def get_analysis_display(self, signal): return [f"Analysis: {signal.id}"]
        def generate_spectrum_display(self, signals, freq_range): return ["Spectrum Display"]


class AetherTap:
    """
    The AetherTap terminal interface - manages the multi-pane display
    """
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height = 0
        self.width = 0
        self.panes: Dict[str, Any] = {}
        self.command_buffer = ""
        self.log_entries: List[str] = []
        self.max_log_entries = 100
        self.focused_signal = None
        self.error_message = ""
        self.error_time = 0
        
        # Initialize signal art system
        self.signal_art = SignalArt()
        
    def initialize(self):
        """Initialize the curses interface and create panes"""
        try:
            curses.curs_set(0)
        except curses.error:
            pass
            
        self.stdscr.nodelay(1)
        self.stdscr.timeout(50)
        
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_GREEN, -1)
            curses.init_pair(2, curses.COLOR_BLUE, -1)
            curses.init_pair(3, curses.COLOR_YELLOW, -1)
            curses.init_pair(4, curses.COLOR_RED, -1)
        
        self.height, self.width = self.stdscr.getmaxyx()
        
        if self.height < 24 or self.width < 80:
            raise Exception(f"Terminal too small ({self.width}x{self.height}). Need at least 80x24.")
        
        self._create_panes()
        
    def _create_panes(self):
        """Create the individual panes for the AetherTap interface"""
        self.panes.clear()
        
        # Simple layout that won't cause crashes
        pane_height = max(8, (self.height - 6) // 2)
        pane_width = max(30, (self.width - 4) // 2)
        
        try:
            self.panes['msa'] = {
                'window': curses.newwin(pane_height, pane_width, 1, 1),
                'title': 'Main Spectrum Analyzer [MSA]',
                'content': []
            }
            
            self.panes['sfd'] = {
                'window': curses.newwin(pane_height, pane_width, 1, pane_width + 2),
                'title': 'Signal Focus & Data [SFD]',
                'content': []
            }
            
            self.panes['cnp'] = {
                'window': curses.newwin(pane_height, pane_width, pane_height + 2, 1),
                'title': 'Cartography & Navigation [CNP]',
                'content': []
            }
            
            self.panes['cld'] = {
                'window': curses.newwin(pane_height, pane_width, pane_height + 2, pane_width + 2),
                'title': "Captain's Log & Database [CLD]",
                'content': []
            }
            
            cli_y = pane_height * 2 + 3
            self.panes['cli'] = {
                'window': curses.newwin(3, self.width - 2, cli_y, 1),
                'title': 'Command Line Interface [CLI]',
                'content': []
            }
            
        except curses.error:
            # Fallback: just create CLI
            self.panes['cli'] = {
                'window': curses.newwin(3, self.width - 2, self.height - 4, 1),
                'title': 'Command Line Interface [CLI]',
                'content': []
            }
        
        self._init_pane_content()
    
    def _init_pane_content(self):
        """Initialize default content for each pane"""
        if 'msa' in self.panes:
            self.panes['msa']['content'] = [
                "Frequency band: 100.0 - 200.0 MHz",
                "Status: Standby",
                "No signals detected. Use SCAN to begin."
            ]
        
        if 'sfd' in self.panes:
            self.panes['sfd']['content'] = [
                "No signal currently focused.",
                "Use FOCUS <signal_id> to analyze a signal."
            ]
          if 'cnp' in self.panes:
            self.panes['cnp']['content'] = [
                "Current Location: ALPHA-1",
                "",
                "╔════════ SECTOR MAP ════════╗",
                "║                            ║",
                "║    [ALPHA-1] ◄── YOU       ║",
                "║       │                    ║",
                "║    [BETA-2]                ║",
                "║                            ║",
                "║  Known Sectors: 1 of ???   ║",
                "╚════════════════════════════╝"
            ]
        
        self.log_entries = [
            "AetherTap v1.0 initialized.",
            "Signal Cartographer ready.",
            "Type HELP for commands."
        ]
        self._update_log_pane()
    
    def show_startup_sequence(self):
        """Display the startup sequence"""
        self.stdscr.clear()
        
        title_lines = [
            "THE SIGNAL CARTOGRAPHER: ECHOES FROM THE VOID",
            "AetherTap v1.0 Terminal Interface",
            "",
            "Initializing quantum resonance chambers...",
            "Ready to scan for echoes from the deep.",
            "",
            "Press any key to continue..."
        ]
        
        start_y = max(0, (self.height - len(title_lines)) // 2)
        
        for i, line in enumerate(title_lines):
            if start_y + i < self.height:
                x = max(0, (self.width - len(line)) // 2)
                try:
                    self.stdscr.addstr(start_y + i, x, line[:self.width-1])
                except curses.error:
                    pass
        
        self.stdscr.refresh()
        self.stdscr.nodelay(0)
        self.stdscr.getch()
        self.stdscr.nodelay(1)
        self.stdscr.clear()
    
    def update_display(self):
        """Update all panes and refresh the display"""
        try:
            # Check for terminal resize
            new_height, new_width = self.stdscr.getmaxyx()
            if new_height != self.height or new_width != self.width:
                self.height, self.width = new_height, new_width
                if self.height >= 20 and self.width >= 60:
                    self._create_panes()
                else:
                    return
            
            self.stdscr.clear()
            
            # Draw all panes
            for pane in self.panes.values():
                self._draw_pane(pane)
            
            # Draw error message if present
            if self.error_message and time.time() - self.error_time < 3:
                self._draw_error_message()
            elif self.error_message:
                self.error_message = ""
            
            self.stdscr.refresh()
            
        except curses.error:
            pass
    
    def _draw_pane(self, pane):
        """Draw a single pane with border and content"""
        try:
            window = pane['window']
            title = pane['title']
            content = pane['content']
            
            window.clear()
            height, width = window.getmaxyx()
            
            if height < 3 or width < 3:
                return
            
            # Draw border
            window.box()
            
            # Draw title
            if len(title) < width - 2:
                title_x = (width - len(title)) // 2
                window.addstr(0, title_x, title[:width-2])
            
            # Draw content
            max_lines = height - 2
            max_width = width - 2
            
            for i, line in enumerate(content[:max_lines]):
                if i + 1 < height - 1:
                    display_line = line[:max_width]
                    window.addstr(i + 1, 1, display_line)
            
            # Special handling for CLI
            if title.startswith('Command Line') and height >= 3:
                prompt = f"AetherTap> {self.command_buffer}"
                window.addstr(height - 2, 1, prompt[:max_width])
            
            window.refresh()
            
        except curses.error:
            pass

    def handle_input(self, key: int) -> Optional[str]:
        """Handle keyboard input"""
        if 32 <= key <= 126:  # Printable ASCII
            self.command_buffer += chr(key)
            return None
            
        elif key == 10 or key == 13:  # Enter
            if self.command_buffer.strip():
                command = self.command_buffer.strip()
                self.command_buffer = ""
                self.add_log_entry(f"> {command}")
                
                if command.lower() in ['quit', 'exit', 'q']:
                    return "quit"
                
                return f"command:{command}"
            return None
            
        elif key == 127 or key == 8:  # Backspace
            if self.command_buffer:
                self.command_buffer = self.command_buffer[:-1]
            return None
              elif key == 27:  # Escape
            self.command_buffer = ""
            return None
        
        return None
    
    def add_log_entry(self, entry: str):
        """Add an entry to the Captain's Log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_entries.append(f"[{timestamp}] {entry}")
        
        if len(self.log_entries) > self.max_log_entries:
            self.log_entries = self.log_entries[-self.max_log_entries:]
        
        self._update_log_pane()
    
    def _update_log_pane(self):
        """Update the Captain's Log pane content"""        if 'cld' in self.panes:
            recent_entries = self.log_entries[-10:]
            self.panes['cld']['content'] = recent_entries
    
    def update_spectrum(self, signals: List[Any]):
        """Update the spectrum display with new signal data"""
        if 'msa' not in self.panes:
            return
            
        content = [
            f"Frequency band: {self.get_frequency_range_str()}",
            f"Signals detected: {len(signals)}",
            ""
        ]
        
        if signals:
            # Add spectrum visualization using SignalArt
            spectrum_display = self.signal_art.generate_spectrum_display(signals, (100.0, 200.0))
            content.extend(spectrum_display[:3])  # First 3 lines of spectrum
            content.append("")
            
            content.append("Active Signals:")
            for i, signal in enumerate(signals[:4]):  # Reduced to fit screen
                freq = getattr(signal, 'frequency', 'Unknown')
                strength = getattr(signal, 'strength', 0.0)
                sig_type = getattr(signal, 'signal_type', 'unknown')
                content.append(f"  {i+1}: {freq} MHz [{strength:.2f}] ({sig_type})")
        else:
            content.extend([
                "╔══════════════════════════════════════╗",
                "║ [   No Signals Detected   ]         ║",
                "║                                      ║",
                "║ ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁ ║",
                "╚══════════════════════════════════════╝",
                "",
                "Use SCAN to begin signal detection."
            ])
        
        self.panes['msa']['content'] = content
      def update_focused_signal(self, signal: Any):
        """Update the Signal Focus & Data pane with signal details"""
        if 'sfd' not in self.panes:
            return
            
        if signal:
            # Get signal type for art display
            sig_type = getattr(signal, 'signal_type', 'unknown')
            
            content = [
                f"Signal ID: {getattr(signal, 'id', 'Unknown')}",
                f"Frequency: {getattr(signal, 'frequency', 'N/A')} MHz",
                f"Strength: {getattr(signal, 'strength', 0.0):.2f}",
                f"Type: {sig_type}",
                ""
            ]
            
            # Add ASCII art visualization
            signal_signature = self.signal_art.get_signal_signature(sig_type)
            content.extend(signal_signature[:4])  # First 4 lines to fit pane
            
            content.extend([
                "",
                "Use ANALYZE to decode this signal."
            ])
            
            self.focused_signal = signal
        else:
            content = [
                "No signal currently focused.",
                "",
                "╔════════════════════════════════════╗",
                "║          SIGNAL FOCUS ARRAY        ║",
                "║                                    ║",
                "║     [  No Target Selected  ]      ║",
                "║                                    ║",
                "║  Use FOCUS <signal_id> to begin   ║",
                "╚════════════════════════════════════╝"
            ]
            self.focused_signal = None
        
        self.panes['sfd']['content'] = content
    
    def show_signal_analysis(self, signal: Any):
        """Display detailed signal analysis using SignalArt system"""
        if 'sfd' not in self.panes:
            return
            
        if signal:
            # Get comprehensive analysis display
            analysis_display = self.signal_art.get_analysis_display(signal)
            
            content = [
                f"=== ANALYZING: {getattr(signal, 'id', 'Unknown')} ===",
                ""
            ]
            
            # Add the analysis visualization
            content.extend(analysis_display)
            
            self.panes['sfd']['content'] = content
            self.add_log_entry(f"Analysis complete for signal {getattr(signal, 'id', 'Unknown')}")
        else:
            self.show_error("No signal to analyze")
    
    def get_frequency_range_str(self) -> str:
        """Get current frequency range as string"""
        return "100.0 - 200.0 MHz"
    
    def show_error(self, message: str):
        """Show an error message"""
        self.error_message = message
        self.error_time = time.time()
        self.add_log_entry(f"ERROR: {message}")
    
    def _draw_error_message(self):
        """Draw error message overlay"""
        if not self.error_message:
            return
        
        msg = self.error_message[:40]
        try:
            y = self.height // 2
            x = max(0, (self.width - len(msg) - 10) // 2)
            self.stdscr.addstr(y, x, f"ERROR: {msg}")
        except curses.error:
            pass
