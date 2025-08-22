"""Platform-specific utilities and constants."""
import os
import sys
import platform
from enum import Enum
from pathlib import Path
from typing import Optional

class Platform(Enum):
    """Supported platforms."""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    UNKNOWN = "unknown"

def get_platform() -> Platform:
    """Detect current platform."""
    system = platform.system().lower()
    if system == "windows":
        return Platform.WINDOWS
    elif system == "linux":
        return Platform.LINUX
    elif system == "darwin":
        return Platform.MACOS
    return Platform.UNKNOWN

def get_config_dir() -> Path:
    """Get platform-specific config directory."""
    if get_platform() == Platform.WINDOWS:
        base = Path(os.environ.get('APPDATA', '~/.terminal-bookmarks'))
    elif get_platform() == Platform.MACOS:
        base = Path('~/Library/Application Support/terminal-bookmarks')
    else:
        base = Path(os.environ.get('XDG_CONFIG_HOME', '~/.config/terminal-bookmarks'))
    
    return base.expanduser()

def get_data_dir() -> Path:
    """Get platform-specific data directory."""
    if get_platform() == Platform.WINDOWS:
        base = Path(os.environ.get('LOCALAPPDATA', '~/.terminal-bookmarks/data'))
    elif get_platform() == Platform.MACOS:
        base = Path('~/Library/Application Support/terminal-bookmarks')
    else:
        base = Path(os.environ.get('XDG_DATA_HOME', '~/.local/share/terminal-bookmarks'))
    
    return base.expanduser()

def get_shell() -> str:
    """Detect current shell."""
    if get_platform() == Platform.WINDOWS:
        return os.environ.get('SHELL', 'powershell.exe')
    return os.environ.get('SHELL', '/bin/bash')

def supports_ansi() -> bool:
    """Check if terminal supports ANSI escape codes."""
    if get_platform() == Platform.WINDOWS:
        if os.environ.get('WT_SESSION'): 
            return True
        if os.environ.get('TERM_PROGRAM') == 'vscode': 
            return True
        if os.environ.get('ANSICON'):
            return True
        if os.environ.get('ConEmuANSI') == 'ON':
            return True
        return False
    if not sys.stdout.isatty():
        return False
    
    term = os.environ.get('TERM', '')
    return term in ('xterm', 'xterm-256color', 'linux', 'screen', 'ansi') 