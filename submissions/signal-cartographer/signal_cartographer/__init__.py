"""
The Signal Cartographer: Echoes from the Void
A sci-fi terminal-based signal analysis game with beautiful TUI interface

A thrilling adventure where you scan space signals, decode mysterious transmissions,
and uncover secrets hidden in the void. Features a modern 6-panel interface,
progressive difficulty across 5 sectors, 9 signal types, equipment upgrades,
and an achievement system.
"""

__version__ = "1.0.1"
__author__ = "Maverick"
__description__ = "A sci-fi terminal-based signal analysis game with beautiful TUI interface"

# Import main components for easy access
try:
    from .game_core import SignalCartographer
    from .main import main
    
    __all__ = [
        "SignalCartographer",
        "main",
        "__version__",
        "__author__",
        "__description__",
    ]
except ImportError:
    # Handle import errors gracefully during package setup
    __all__ = [
        "__version__",
        "__author__", 
        "__description__",
    ]
