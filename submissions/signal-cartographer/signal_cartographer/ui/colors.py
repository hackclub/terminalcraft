"""
Color schemes and themes for the AetherTap interface
"""

from textual.color import Color
from rich.style import Style

class AetherTapColors:
    """Color scheme for the AetherTap interface"""
    
    # Base colors
    BACKGROUND = Color.parse("#0d1117")
    FOREGROUND = Color.parse("#c9d1d9")
    
    # Interface elements
    BORDER_ACTIVE = Color.parse("#58a6ff")
    BORDER_INACTIVE = Color.parse("#30363d")
    TITLE = Color.parse("#7c3aed")
    
    # Signal colors
    SIGNAL_WEAK = Color.parse("#6e7681")
    SIGNAL_MEDIUM = Color.parse("#f78166")
    SIGNAL_STRONG = Color.parse("#56d364")
    SIGNAL_CRITICAL = Color.parse("#ffa657")
    
    # Status colors
    SUCCESS = Color.parse("#238636")
    WARNING = Color.parse("#d29922")
    ERROR = Color.parse("#da3633")
    INFO = Color.parse("#0969da")
    
    # Command line
    COMMAND_PROMPT = Color.parse("#7c3aed")
    COMMAND_TEXT = Color.parse("#c9d1d9")
    
    # Log colors
    LOG_NORMAL = Color.parse("#8b949e")
    LOG_HIGHLIGHT = Color.parse("#58a6ff")
    
    @classmethod
    def get_signal_color(cls, strength: float) -> Color:
        """Get color based on signal strength (0.0 to 1.0)"""
        if strength < 0.3:
            return cls.SIGNAL_WEAK
        elif strength < 0.6:
            return cls.SIGNAL_MEDIUM
        elif strength < 0.9:
            return cls.SIGNAL_STRONG
        else:
            return cls.SIGNAL_CRITICAL
    
    @classmethod
    def get_pane_style(cls, is_focused: bool = False) -> Style:
        """Get style for pane borders"""
        border_color = cls.BORDER_ACTIVE if is_focused else cls.BORDER_INACTIVE
        return Style(color=str(border_color))
