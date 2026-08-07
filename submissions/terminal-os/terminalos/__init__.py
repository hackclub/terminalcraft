"""TerminalOS - A complete operating system experience in your terminal."""

__version__ = "1.0.0"
__author__ = "Terminal Developer"
__email__ = "dev@terminalos.com"
__description__ = "A complete operating system experience in your terminal"

from .core.app import TerminalOSApp
from .config.settings import Settings

__all__ = ["TerminalOSApp", "Settings", "__version__"]