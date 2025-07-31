class Colors:
    """ANSI color codes for terminal output"""
    
    # Basic formatting
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Standard colors
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Atom-specific color scheme
    NUCLEUS = BRIGHT_RED
    PROTON = '\033[38;5;208m'  # Orange
    NEUTRON = '\033[38;5;250m'  # Light gray
    ELECTRON = BRIGHT_CYAN
    
    # Electron shells (different colors for each shell)
    SHELL_1 = BRIGHT_YELLOW      # K shell
    SHELL_2 = BRIGHT_GREEN       # L shell  
    SHELL_3 = BRIGHT_BLUE        # M shell
    SHELL_4 = BRIGHT_MAGENTA     # N shell
    SHELL_5 = '\033[38;5;135m'   # O shell (purple)
    SHELL_6 = '\033[38;5;201m'   # P shell (pink)
    SHELL_7 = '\033[38;5;87m'    # Q shell (light cyan)
    
    # UI colors
    HEADER = BRIGHT_CYAN
    INFO = CYAN
    HIGHLIGHT = BRIGHT_YELLOW
    ERROR = BRIGHT_RED
    SUCCESS = BRIGHT_GREEN

def clear_screen():
    """Clear the terminal screen"""
    print('\033[2J\033[H', end='')

def hide_cursor():
    """Hide the terminal cursor"""
    print('\033[?25l', end='')

def show_cursor():
    """Show the terminal cursor"""
    print('\033[?25h', end='')
