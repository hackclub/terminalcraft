#!/usr/bin/env python3
import os
import sys
import time
from typing import List, Any
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)  
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    class DummyColors:
        def __getattr__(self, name):
            return ""
    Fore = DummyColors()
    Back = DummyColors()
    Style = DummyColors()
TITLE_COLOR = Fore.YELLOW + Style.BRIGHT
LOCATION_COLOR = Fore.CYAN + Style.BRIGHT
HEALTH_COLOR = Fore.GREEN
LOW_HEALTH_COLOR = Fore.RED
INVENTORY_COLOR = Fore.BLUE
ALLY_COLOR = Fore.MAGENTA
ENEMY_COLOR = Fore.RED
PROMPT_COLOR = Fore.YELLOW
OPTION_COLOR = Fore.CYAN
DIVIDER_COLOR = Fore.BLUE
def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')
def slow_print(text: str, delay: float = 0.02, color: str = ""):
    """Print text slowly, character by character, for dramatic effect."""
    for char in text:
        sys.stdout.write(color + char if COLORS_AVAILABLE else char)
        sys.stdout.flush()
        time.sleep(delay)
    print()
def get_choice(prompt: str, options: List[str]) -> int:
    """Display a menu of options and get the user's choice."""
    print(f"\n{PROMPT_COLOR}{prompt}")
    for i, option in enumerate(options, 1):
        print(f"  {OPTION_COLOR}{i}. {option}")
    divider = create_vertical_divider(max(len(option) for option in options) + 5)
    print(divider)
    while True:
        try:
            choice = input(f"\n{PROMPT_COLOR}Enter your choice (number): ")
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(options):
                return choice_idx
            else:
                print(f"{Fore.RED}Please enter a number between 1 and {len(options)}.")
        except ValueError:
            print(f"{Fore.RED}Please enter a valid number.")
def wrap_text(text: str, width: int = 80) -> str:
    """Wrap text to the specified width."""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    for word in words:
        if current_length + len(word) + (1 if current_line else 0) <= width:
            current_line.append(word)
            current_length += len(word) + (1 if current_length > 0 else 0)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
    if current_line:
        lines.append(' '.join(current_line))
    return '\n'.join(lines)
def display_health_bar(health: int, max_health: int = 100, width: int = 20) -> str:
    """Create a visual health bar representation."""
    fill_width = int((health / max_health) * width)
    color = HEALTH_COLOR if health > 30 else LOW_HEALTH_COLOR
    bar = color + '█' * fill_width + Fore.WHITE + '░' * (width - fill_width)
    return f"[{bar}] {color}{health}/{max_health}"
def display_title(title: str, width: int = 80, char: str = '=') -> str:
    """Create a decorated title for display."""
    padding = (width - len(title) - 2) // 2
    return f"\n{TITLE_COLOR}{char * padding} {title} {char * padding}"
def create_vertical_divider(width: int = 80) -> str:
    """Create a vertical line divider for UI separation."""
    return f"{DIVIDER_COLOR}{'┃' + '─' * (width - 2) + '┃'}"
def create_box(text: str, width: int = 80, color: str = DIVIDER_COLOR) -> str:
    """Create a box around text for important messages."""
    lines = text.split('\n')
    max_line_length = max(len(line) for line in lines)
    box_width = min(width, max_line_length + 4)
    top = f"{color}┏{'━' * (box_width - 2)}┓"
    bottom = f"{color}┗{'━' * (box_width - 2)}┛"
    result = [top]
    for line in lines:
        padding = ' ' * (box_width - len(line) - 4)
        result.append(f"{color}┃ {line}{padding} ┃")
    result.append(bottom)
    return '\n'.join(result) 