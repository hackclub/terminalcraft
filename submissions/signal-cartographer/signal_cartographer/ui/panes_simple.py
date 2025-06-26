"""
Individual pane managers for the AetherTap interface
"""

from typing import List, Optional, Any, Dict
from textual.widgets import Static
from rich.text import Text

from .colors import AetherTapColors

class BasePane(Static):
    """Base class for all AetherTap panes"""
    
    def __init__(self, title: str, *args, **kwargs):
        self.title = title
        self.content_lines = []
        initial_content = f"[bold cyan]{self.title}[/bold cyan]\n[dim]Initializing...[/dim]"
        super().__init__(initial_content, *args, **kwargs)
    
    def add_content_line(self, line: str):
        """Add a line to the pane content"""
        self.content_lines.append(line)
        self._update_display()
    
    def clear_content(self):
        """Clear the pane content"""
        self.content_lines = []
        self._update_display()
    
    def set_content(self, lines: list):
        """Set the entire content"""
        self.content_lines = lines[:]
        self._update_display()
    
    def _update_display(self):
        """Update the displayed content"""
        content = f"[bold cyan]{self.title}[/bold cyan]\n"
        if self.content_lines:
            content += "\n".join(self.content_lines)
        else:
            content += "[dim]No data[/dim]"
        self.update(content)
    
    def update_content(self, lines: List[str]):
        """Update the content of this pane"""
        self.set_content(lines)

class SpectrumPane(BasePane):
    """Main Spectrum Analyzer pane [MSA]"""
    
    def __init__(self, **kwargs):
        super().__init__("Main Spectrum Analyzer [MSA]", **kwargs)
        self.signals = []
        self.frequency_range = (100, 200)
        self.noise_level = 0.1
        
    def update_spectrum(self, signals: List[Any], freq_range: tuple, noise: float = 0.1):
        """Update the spectrum display with current signals"""
        self.signals = signals
        self.frequency_range = freq_range
        self.noise_level = noise
        
        # Generate ASCII spectrum display
        lines = self._generate_spectrum_display()
        self.set_content(lines)
        
    def _generate_spectrum_display(self):
        """Generate ASCII art spectrum display"""
        lines = []
        width = 50
        height = 10
        
        # Header
        lines.append("=" * width)
        lines.append(f"Frequency Range: {self.frequency_range[0]}-{self.frequency_range[1]} MHz")
        lines.append("=" * width)
        
        # Generate spectrum bars
        for i in range(height):
            line = ""
            for j in range(width):
                # Calculate frequency for this position
                freq = self.frequency_range[0] + (j / width) * (self.frequency_range[1] - self.frequency_range[0])
                
                # Find signal strength at this frequency
                signal_strength = self.noise_level
                for signal in self.signals:
                    if hasattr(signal, 'frequency') and hasattr(signal, 'strength'):
                        if abs(signal.frequency - freq) < 5:  # Within range
                            signal_strength = max(signal_strength, signal.strength)
                
                # Draw spectrum bar based on height position
                bar_height = (height - i) / height
                if signal_strength > bar_height:
                    if signal_strength > 0.8:
                        char = "█"
                    elif signal_strength > 0.6:
                        char = "▓"
                    elif signal_strength > 0.4:
                        char = "▒"
                    elif signal_strength > 0.2:
                        char = "░"
                    else:
                        char = "·"
                else:
                    char = " "
                
                line += char
            lines.append(line)
        
        # Footer with signal count
        lines.append("=" * width)
        lines.append(f"Detected Signals: {len(self.signals)}")
        
        return lines

class SignalFocusPane(BasePane):
    """Signal Focus & Data pane [SFD]"""
    
    def __init__(self, **kwargs):
        super().__init__("Signal Focus & Data [SFD]", **kwargs)
        self.focused_signal = None
        
    def focus_signal(self, signal):
        """Focus on a specific signal"""
        self.focused_signal = signal
        if signal:
            lines = [
                f"Signal ID: {signal.id}",
                f"Frequency: {signal.frequency} MHz",
                f"Strength: {signal.strength:.2f}",
                f"Type: {signal.signal_type}",
                f"Source: {signal.source_sector}",
                "",
                "Signal Pattern:",
                "▓▒░▓▒▓░▒▓░▒▓▒░",
                "░▒▓░▒░▓▒░▓▒░▓",
                "",
                f"Analysis: {signal.description}"
            ]
        else:
            lines = ["No signal focused", "", "Use FOCUS [signal_id] to select a signal"]
        
        self.set_content(lines)

class CartographyPane(BasePane):
    """Cartography & Navigation pane [CNP]"""
    
    def __init__(self, **kwargs):
        super().__init__("Cartography & Navigation [CNP]", **kwargs)
        self.current_sector = "Alpha-1"
        
    def update_map(self, sector: str):
        """Update the map display"""
        self.current_sector = sector
        lines = [
            f"Current Sector: {sector}",
            "",
            "     N",
            "  ┌─────┐",
            "W │  ●  │ E",
            "  │ ╱ ╲ │",
            "  └─────┘",
            "     S",
            "",
            f"Coordinates: {sector}",
            "Signal Sources: 3",
            "Anomalies: 1"
        ]
        self.set_content(lines)

class DecoderPane(BasePane):
    """Decoder & Analysis Toolkit pane [DAT]"""
    
    def __init__(self, **kwargs):
        super().__init__("Decoder & Analysis Toolkit [DAT]", **kwargs)
        self.active_tool = None
        
    def set_analysis_tool(self, tool_name: str):
        """Set the active analysis tool"""
        self.active_tool = tool_name
        lines = [
            f"Active Tool: {tool_name}",
            "",
            "Analysis Results:",
            "- Pattern recognition: 75%",
            "- Signal coherence: 89%",
            "- Interference level: Low",
            "",
            "Decoded fragments:",
            "[...static...]",
            "\"The void whispers...\""
        ]
        self.set_content(lines)

class LogPane(BasePane):
    """Captain's Log & Database pane [CLD]"""
    
    def __init__(self, **kwargs):
        super().__init__("Captain's Log & Database [CLD]", **kwargs)
        self.log_entries: List[str] = []
    
    def add_log_entry(self, entry: str):
        """Add a new log entry"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_entry = f"[dim]{timestamp}[/dim] {entry}"
        self.log_entries.append(formatted_entry)
        
        # Keep only the last 20 entries for display
        display_entries = self.log_entries[-20:]
        self.set_content(display_entries)
    
    def search_logs(self, keyword: str) -> List[str]:
        """Search log entries for a keyword"""
        matching_entries = [entry for entry in self.log_entries if keyword.lower() in entry.lower()]
        return matching_entries
