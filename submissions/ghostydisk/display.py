import curses
from colorama import Fore, Style, init
from rich import print
from rich.console import Console, Group
from rich.table import Table
from rich.align import Align
from rich.panel import Panel
from datetime import datetime
from rich.prompt import Prompt
from rich import box
import os
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich.padding import Padding
from rich.syntax import Syntax
from rich.progress import Progress
from rich.prompt import Confirm
from rich.markup import escape
import shutil
from typing import List, Tuple, Dict, Any
import time
import sys
import termios
import tty
import random
import math
import subprocess

# Todo: I should probably clean this up someday
# These are all the stupid imports we need
# Might move to a requirements.txt file later

# TODO(Doddy): Find a way to fix this dependency hell

console = Console()

try:
    # this works on my machine - doddy
    with open('logo', 'r') as f:
        logo = f.read()
except:
    # fallback if logo file not found
    logo = """
   .-.      _______
  {}      /       \\
   \\    /  ⌒ ⌒   |
    \\  |           |
     \\ \\     Y   /
      \\|      _ |
       |GhostyDisk|
    """

def clear():
    # My screen needs this - otherwise it flickers on my mac
    os.system('cls' if os.name == 'nt' else 'clear')  
    console.clear()  # double clear just to be safe

# some nice helpers for printing text
def center_print(text, border_style="", style="bold"):
    console.print(Panel(Align.center(text),
                  border_style=border_style, style=style))


def error_print(text):
    console.print(f"[!] {text}", style="bold red")


def success_print(text):
    console.print(f"[+] {text}", style="bold light_green")


def note_print(text):
    console.print(f"[*] {text}", style="cornsilk1")


# this is a bit messy, I know - will refactor later
def display_results(results):
    # using direct emoji cuz it's more fun than unicode chars
    console.print("\n[bold magenta]🔍 Ghost Files:[/bold magenta]")
    for path, size, age in results["ghosts"]:
        print(
            f"👻 {path} | {size/1024:.2f} KB | Last modified {int(age // 86400)} days ago")

    console.print("\n[bold yellow]💾 Large Files:[/bold yellow]")
    for path, size in results["large"]:
        print(f"💀 {path} | {size / (1024*1024):.2f} MB")

    console.print("\n[bold cyan]⏳ Old Files:[/bold cyan]")
    for path, age in results["old"]:
        print(f"🧟‍♂️ {path} | Last modified {int(age // 86400)} days ago")

    console.print("\n[bold red]📂 Duplicates:[/bold red]")
    for hash, paths in results["duplicates"].items():
        if len(paths) > 1:
            print(f"🪞 Hash: {hash[:8]}...")
            for path in paths:
                print(f"  🔁 {path}")


def display_options(options, title="Choose Scan Mode"):
    # I should really make this consistent with the cyberpunk style
    # but whatever - it works for now
    table = Table(title=title, show_header=False)

    for key, label in options:
        table.add_row(key, label)

    console.print(table)


# I like this one better - cooler style
def cyberbunk_display_options(options, title="Choose Scan Mode"):
    console.print(f"[bold magenta]┌─[ {title} ]─[/]")
    for key, label in options:
        console.print(
            f"[cyan]│[/] [bright_white]{key}[/] [magenta]➔[/] {label}")
    console.print("[cyan]└─>[/]", end="")


# This is a bit overkill, but I like it
# Note to self: curses is a pain, maybe replace with something simpler
def interactive_display_options(options, title="Choose Scan Mode", selected=0):
    def menu(stdscr):
        nonlocal selected
        curses.curs_set(0)
        stdscr.nodelay(False)
        stdscr.timeout(100)
        
        # hacky way to handle resizing
        CURSOR_MOVED = False

        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            title_str = f"{title}"
            stdscr.addstr(1, (width - len(title_str)) // 2,
                          title_str, curses.A_BOLD | curses.A_UNDERLINE)

            for i, (key, label) in enumerate(options):
                x = 4
                y = 3 + i
                style = curses.A_REVERSE if i == selected else curses.A_NORMAL
                
                # fix for weird terminal behavior on my system
                if y < height - 1 and x + len(f"{key}. {label}") < width - 1:
                    stdscr.addstr(y, x, f"{key}. {label}", style)

            stdscr.refresh()

            # lol this is probably not the best way to do this
            # but I kept getting weird input lag with getch() alone
            key = -1
            try:
                key = stdscr.getch()
            except:
                time.sleep(0.1)
                continue

            # this feels unnecessarily complicated but it works
            if key == curses.KEY_UP:
                selected = (selected - 1) % len(options)
                CURSOR_MOVED = True
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % len(options)
                CURSOR_MOVED = True
            elif key in [curses.KEY_ENTER, 10, 13]:
                break
            elif key == ord('q'):  # quick escape
                selected = -1
                break

    # I honestly hate curses but it works
    curses.wrapper(menu)
    # The +1 is because we're 0-indexed internally but present 1-indexed
    return options[selected][0] if selected >= 0 and selected < len(options) else "1"


# Size formatting - stole this from stackoverflow, works great
def format_size(size_bytes: int) -> str:
    """Take bytes, return human-readable size"""
    # list of units is cleaner than a loop imo
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    unit_idx = 0
    
    while size_bytes >= 1024.0 and unit_idx < len(units) - 1:
        size_bytes /= 1024.0
        unit_idx += 1
        
    return f"{size_bytes:.1f} {units[unit_idx]}"


def format_path(path: str, max_length: int = 40) -> str:
    # keep paths readable by truncating from the left
    # this is better than ellipsis in the middle imo
    if len(path) > max_length:
        return "..." + path[-max_length+3:]
    return path


def show_scan_summary(results, scan_path):
    # Count up the total size of ghost files
    ghost_size = 0
    for _, size, _ in results["ghosts"]:
        ghost_size += size  # could use sum() but this is more explicit
    
    # Same for large files
    large_size = 0
    for _, size in results["large"]:
        large_size += size

    # Build a table to display the summary
    summary = Table.grid(padding=(0, 2))
    summary.add_column(style="bold")
    summary.add_column()

    summary.add_row("Path:", scan_path)
    summary.add_row("Date:", datetime.now().strftime("%Y-%m-%d"))
    summary.add_row("", "─" * 40)  # Separator
    summary.add_row("👻 Ghost Files:",
                    f"{len(results['ghosts'])} ({format_size(ghost_size)})")
    summary.add_row("💾 Large Files:",
                    f"{len(results['large'])} ({format_size(large_size)})")
    summary.add_row("⌛ Old Files:", str(len(results['old'])))
    summary.add_row("🌀 Duplicates:", f"{len(results['duplicates'])} groups")

    print("\n")
    print(Panel(summary, title="📊 Scan Summary",
          border_style="blue", box=box.ROUNDED))


# I hate this function but it works - some day I'll rewrite it
def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        if ch == '\x1b':  # Escape sequence
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            if ch2 == '[':
                if ch3 == 'A':
                    return 'UP'
                elif ch3 == 'B':
                    return 'DOWN'
                # there are more arrow keys but who cares
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


class DetailViewer:
    """
    A class to view file details in a scrollable interface.
    
    God, I hate OOP sometimes, but this was the cleanest approach
    for this particular case. Just don't look at the MultiSelectList
    class if you value your sanity.
    
    - Doddy (May 2023)
    """
    def __init__(self, results: Dict[str, Any], category: str):
        self.results = results
        self.category = category
        self.current_page = 0
        # Magic number - looks good on my terminal
        self.items_per_page = 10  
        self.selected_index = 0
        self.deleted_items = set()
        
        # This is a bit messy but it works
        if category == "all":
            self.items = []
            # ghosts
            for path, size, age in results["ghosts"]:
                self.items.append(("ghost", path, size, age))
            # large files
            for path, size in results["large"]:
                self.items.append(("large", path, size, None))
            # old files
            for path, age in results["old"]:
                self.items.append(("old", path, None, age))
            # duplicates
            for hash_val, paths in results["duplicates"].items():
                for path in paths:
                    self.items.append(("duplicate", path, None, hash_val))
            
            self.columns = ["#", "Type", "Path", "Size", "Age/Hash"]
        else:
            if category == "ghosts":
                self.items = [(path, size, age) for path, size, age in results["ghosts"]]
                self.columns = ["#", "Path", "Size", "Age"]
            elif category == "large":
                self.items = [(path, size) for path, size in results["large"]]
                self.columns = ["#", "Path", "Size"]
            elif category == "old":
                self.items = [(path, age) for path, age in results["old"]]
                self.columns = ["#", "Path", "Age"]
            elif category == "duplicates":
                self.items = []
                for hash_val, paths in results["duplicates"].items():
                    for path in paths:
                        self.items.append((path, hash_val))
                self.columns = ["#", "Path", "Hash"]
        
        # Honestly we could just use math.ceil here but whatever
        self.total_pages = (len(self.items) + self.items_per_page - 1) // self.items_per_page

    def get_page_items(self) -> List[Tuple]:
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        return self.items[start:end]

    def render_table(self) -> Table:
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold blue")
        
        for col in self.columns:
            table.add_column(col)
        
        start_idx = self.current_page * self.items_per_page
        for i, item in enumerate(self.get_page_items(), start=start_idx + 1):
            if i - 1 in self.deleted_items:
                style = "dim"
            else:
                style = "bold green" if i - 1 == self.selected_index else None
            
            row = [str(i)]
            
            if self.category == "all":
                type_, path, size, age_or_hash = item
                # Oh look, more stupid emojis
                type_emoji = {
                    "ghost": "👻",
                    "large": "💾",
                    "old": "⌛",
                    "duplicate": "🌀"
                }
                row.extend([
                    f"{type_emoji[type_]} {type_.title()}",
                    format_path(path),
                    format_size(size) if size else "",
                    f"{age_or_hash // (24*3600)} days" if isinstance(age_or_hash, (int, float)) else str(age_or_hash)[:8] + "..." if age_or_hash else ""
                ])
            elif self.category == "ghosts":
                path, size, age = item
                row.extend([
                    format_path(path),
                    format_size(size),
                    f"{age // (24*3600)} days"
                ])
            elif self.category == "large":
                path, size = item
                row.extend([
                    format_path(path),
                    format_size(size)
                ])
            elif self.category == "old":
                path, age = item
                row.extend([
                    format_path(path),
                    f"{age // (24*3600)} days"
                ])
            elif self.category == "duplicates":
                path, hash_val = item
                row.extend([
                    format_path(path),
                    hash_val[:8] + "..."
                ])
            
            table.add_row(*row, style=style)
        
        return table

    def render_footer(self) -> str:
        # Shortcut keys should be more visible but this is fine for now
        return (
            f"Page {self.current_page + 1}/{self.total_pages} | "
            "Use ↑ ↓ to scroll, \[d] to delete, [Enter] to go back"
        )

    def delete_item(self, index: int) -> bool:
        if index >= len(self.items):
            return False
            
        if self.category == "all":
            path = self.items[index][1]
        else:
            path = self.items[index][0]
            
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            self.deleted_items.add(index)
            return True
        except Exception as e:
            console.print(f"[red]Error deleting {path}: {str(e)}[/red]")
            return False

    def show(self):
        # Screw you, PEP8 - this is a UI loop and a big function is fine
        while True:
            console.clear()
            table = self.render_table()
            footer = self.render_footer()
            
            title = "Files > All Categories" if self.category == "all" else f"Files > {self.category.title()}"
            panel = Panel(
                Align.center(
                    Padding(table, (1, 2)),
                    vertical="middle"
                ),
                title=title,
                subtitle=footer,
                border_style="blue"
            )
            
            console.print(panel)
            
            key = get_key()
            
            if key == 'q' or key == '\x1b':
                break
            elif key == 'UP':
                self.selected_index = max(0, self.selected_index - 1)
                if self.selected_index < self.current_page * self.items_per_page:
                    self.current_page = max(0, self.current_page - 1)
            elif key == 'DOWN':
                self.selected_index = min(len(self.items) - 1, self.selected_index + 1)
                if self.selected_index >= (self.current_page + 1) * self.items_per_page:
                    self.current_page = min(self.total_pages - 1, self.current_page + 1)
            elif key == 'd':
                if self.category == "all":
                    item_type = self.items[self.selected_index][0]
                    path = self.items[self.selected_index][1]
                else:
                    path = self.items[self.selected_index][0]
                if Confirm.ask(f"Delete {path}?"):
                    if self.delete_item(self.selected_index):
                        console.print("[green]File deleted successfully[/green]")
                        time.sleep(1)
                    else:
                        console.print("[red]Failed to delete file[/red]")
                        time.sleep(1)

def show_details(results: Dict[str, Any], category: str):
    viewer = DetailViewer(results, category)
    viewer.show()


# Note: this whole class is way more complex than it needs to be, but I was learning
# Python when I wrote it and didn't know any better. Maybe refactor someday.
class ScrollableList:
    def __init__(self, items, title="List", window_size=6,
                 on_select=lambda item: None,
                 on_enter=lambda item: None,
                 on_input=lambda text: None,
                 input_prompt="> ",
                 input_handler=None):
        self.items = items
        self.title = title
        # Honestly I forget why 6 is the default but it looks good
        self.window_size = window_size 
        self.on_select = on_select
        self.on_enter = on_enter
        self.on_input = on_input
        self.input_prompt = input_prompt
        self.input_handler = input_handler
        self.selected_index = 0
        self.scroll_offset = 0
        self.input_text = ""
        self.input_mode = False
        self.deleted_items = set()

    def get_visible_items(self):
        start = self.scroll_offset
        end = start + self.window_size
        # I should use islice here but whatever
        return self.items[start:end]

    def render_list(self):
        table = Table(box=box.ROUNDED, show_header=False, padding=(0, 1))
        table.add_column("", style="bold blue")
        table.add_column("", style="bold")

        # FIXME: this is really inefficient for long lists
        # but it's fine for now
        for i, item in enumerate(self.get_visible_items(), start=self.scroll_offset):
            if i in self.deleted_items:
                style = "dim"
            else:
                style = "bold green" if i == self.selected_index else None
            
            table.add_row(
                "→" if i == self.selected_index else " ",
                str(item),
                style=style
            )

        return table

    def render_input(self):
        if self.input_mode:
            return f"{self.input_prompt}{self.input_text}_"
        return ""

    def render_footer(self):
        if self.input_mode:
            return "Type to input, [Enter] to submit, [Esc] to cancel"
        
        # This string formatting is getting ridiculous
        return (
            f"Items {self.scroll_offset + 1}-{min(self.scroll_offset + self.window_size, len(self.items))} "
            f"of {len(self.items)} | Use ↑ ↓ to scroll, [Enter] to select, \[i] for input"
        )

    def show(self):
        # This function is too long but I'm too lazy to refactor it
        while True:
            console.clear()
            
            list_panel = Panel(
                Align.center(
                    Padding(self.render_list(), (1, 2)),
                    vertical="middle"
                ),
                title=self.title,
                subtitle=self.render_footer(),
                border_style="blue"
            )
            
            if self.input_mode:
                input_panel = Panel(
                    self.render_input(),
                    border_style="yellow"
                )
                console.print(Group(list_panel, input_panel))
            else:
                console.print(list_panel)
            
            key = get_key()
            
            if self.input_mode:
                if key == '\x1b':  # ESC
                    self.input_mode = False
                    self.input_text = ""
                elif key == '\r':  # Enter
                    if self.input_text:
                        self.on_input(self.input_text)
                        if self.input_handler:
                            self.input_handler(self.input_text)
                    self.input_mode = False
                    self.input_text = ""
                elif key == '\x7f':  # Backspace
                    self.input_text = self.input_text[:-1]
                elif len(key) == 1 and key.isprintable():
                    self.input_text += key
            else:
                if key == 'q' or key == '\x1b':  # q or ESC
                    break
                elif key == 'UP':
                    self.selected_index = max(0, self.selected_index - 1)
                    if self.selected_index < self.scroll_offset:
                        self.scroll_offset = max(0, self.scroll_offset - 1)
                elif key == 'DOWN':
                    self.selected_index = min(len(self.items) - 1, self.selected_index + 1)
                    if self.selected_index >= self.scroll_offset + self.window_size:
                        self.scroll_offset = min(
                            len(self.items) - self.window_size,
                            self.scroll_offset + 1
                        )
                elif key == '\r':  # Enter
                    if 0 <= self.selected_index < len(self.items):
                        self.on_select(self.items[self.selected_index])
                        self.on_enter(self.items[self.selected_index])
                elif key == 'i':  # Input mode
                    self.input_mode = True

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, index):
        if 0 <= index < len(self.items):
            self.deleted_items.add(index)
            return True
        return False

    def clear_input(self):
        self.input_text = ""

    def set_input_mode(self, mode=True):
        self.input_mode = mode
        if not mode:
            self.input_text = ""


# I'm still not sure if inheritance was the right choice here...
# BUT it works and I'm not gonna rewrite it now
class MultiSelectList(ScrollableList):
    def __init__(self, items, title="Multi-Select List", window_size=6,
                 on_select=lambda item: None,
                 on_enter=lambda items: None,
                 on_input=lambda text: None,
                 input_prompt="> ",
                 input_handler=None,
                 selection_marker="✓"):
        super().__init__(items, title, window_size, on_select, on_enter, on_input, input_prompt, input_handler)
        self.selected_items = set()
        self.selection_marker = selection_marker
        self.selection_mode = False

    def render_list(self):
        table = Table(box=box.ROUNDED, show_header=False, padding=(0, 1))
        table.add_column("", style="bold blue")  # Selection marker
        table.add_column("", style="bold blue")  # Navigation arrow
        table.add_column("", style="bold")       # Item

        for i, item in enumerate(self.get_visible_items(), start=self.scroll_offset):
            if i in self.deleted_items:
                style = "dim"
            else:
                style = "bold green" if i == self.selected_index else None
            
            # Add selection marker, navigation arrow, and item
            table.add_row(
                self.selection_marker if i in self.selected_items else " ",
                "→" if i == self.selected_index else " ",
                str(item),
                style=style
            )

        return table

    def render_footer(self):
        if self.input_mode:
            return "Type to input, [Enter] to submit, [Esc] to cancel"
        
        selected_count = len(self.selected_items)
        total_count = len(self.items)
        
        if self.selection_mode:
            return (
                f"Selected: {selected_count}/{total_count} | "
                "Use ↑ ↓ to move, [Space] to select, [a] to select all, [n] to select none, "
                "[Enter] to confirm, [Esc] to cancel"
            )
        return (
            f"Items {self.scroll_offset + 1}-{min(self.scroll_offset + self.window_size, total_count)} "
            f"of {total_count} | Use ↑ ↓ to scroll, [Space] to select, [Enter] to confirm, [i] for input"
        )

    def toggle_selection(self, index):
        if index in self.selected_items:
            self.selected_items.remove(index)
        else:
            self.selected_items.add(index)

    def select_all(self):
        self.selected_items = set(range(len(self.items)))

    def select_none(self):
        self.selected_items.clear()

    def get_selected_items(self):
        return [self.items[i] for i in self.selected_items if i < len(self.items)]

    def show(self):
        while True:
            console.clear()
            
            list_panel = Panel(
                Align.center(
                    Padding(self.render_list(), (1, 2)),
                    vertical="middle"
                ),
                title=self.title,
                subtitle=self.render_footer(),
                border_style="blue"
            )
            
            if self.input_mode:
                input_panel = Panel(
                    self.render_input(),
                    border_style="yellow"
                )
                console.print(Group(list_panel, input_panel))
            else:
                console.print(list_panel)
            
            key = get_key()
            
            if self.input_mode:
                if key == '\x1b':  # ESC
                    self.input_mode = False
                    self.input_text = ""
                elif key == '\r':  # Enter
                    if self.input_text:
                        self.on_input(self.input_text)
                        if self.input_handler:
                            self.input_handler(self.input_text)
                    self.input_mode = False
                    self.input_text = ""
                elif key == '\x7f':  # Backspace
                    self.input_text = self.input_text[:-1]
                elif len(key) == 1 and key.isprintable():
                    self.input_text += key
            else:
                if self.selection_mode:
                    if key == '\x1b':  # ESC
                        self.end_selection_mode()
                    elif key == '\r':  # Enter
                        selected_items = self.get_selected_items()
                        self.on_enter(selected_items)
                        break
                    elif key == 'UP':
                        self.selected_index = max(0, self.selected_index - 1)
                        if self.selected_index < self.scroll_offset:
                            self.scroll_offset = max(0, self.scroll_offset - 1)
                    elif key == 'DOWN':
                        self.selected_index = min(len(self.items) - 1, self.selected_index + 1)
                        if self.selected_index >= self.scroll_offset + self.window_size:
                            self.scroll_offset = min(
                                len(self.items) - self.window_size,
                                self.scroll_offset + 1
                            )
                    elif key == ' ':  # Space
                        self.toggle_selection(self.selected_index)
                    elif key == 'a':  # Select all
                        self.select_all()
                    elif key == 'n':  # Select none
                        self.select_none()
                else:
                    if key == 'q' or key == '\x1b':  # q or ESC
                        break
                    elif key == '\r':  # Enter
                        self.start_selection_mode()
                    elif key == 'UP':
                        self.selected_index = max(0, self.selected_index - 1)
                        if self.selected_index < self.scroll_offset:
                            self.scroll_offset = max(0, self.scroll_offset - 1)
                    elif key == 'DOWN':
                        self.selected_index = min(len(self.items) - 1, self.selected_index + 1)
                        if self.selected_index >= self.scroll_offset + self.window_size:
                            self.scroll_offset = min(
                                len(self.items) - self.window_size,
                                self.scroll_offset + 1
                            )
                    elif key == ' ':  # Space
                        self.toggle_selection(self.selected_index)
                    elif key == 'i':  # Input mode
                        self.input_mode = True

    def start_selection_mode(self):
        self.selection_mode = True
        if self.selected_index < len(self.items) and self.selected_index not in self.selected_items:
            self.toggle_selection(self.selected_index)

    def end_selection_mode(self):
        self.selection_mode = False


# This function is fun but completely unnecessary
# I just like the animation
def animate_ghost_logo():
    """Shows an animated ghost logo because why not"""
    # We all need some fun in our terminal apps
    
    # This is totally unnecessary but it's cool and I'm keeping it
    
    ghost_text = """
   .-.
  (o o)
   \|/
    |
   / \\
  /   \\
    """
    
    ghost_colors = [
        "bright_blue",
        "bright_magenta",
        "bright_cyan",
        "bright_green",
        "bright_yellow",
        "bright_red",
    ]
    
    # Look ma, no sleep()! Using time-based animation instead
    start_time = time.time()
    duration = 5  # seconds
    fps = 15
    frame_time = 1.0 / fps
    
    # Hack: sometimes curses leaves the terminal in a weird state
    # so let's make sure it's clean
    clear()
    
    try:
        while time.time() - start_time < duration:
            console.clear()
            
            # Calculate animation progress
            progress = (time.time() - start_time) / duration
            
            # Oscillate movement
            offset = int(10 * abs(math.sin(progress * 2 * math.pi)))
            
            # Cycle through colors
            color_idx = int(progress * len(ghost_colors) * 4) % len(ghost_colors)
            
            # Render ghost
            ghost = get_ghost_with_offset(offset)
            colored_ghost = get_ghost_with_color(ghost, ghost_colors[color_idx])
            
            console.print(colored_ghost)
            console.print("\n\n[bold cyan]Press Ctrl+C to return to menu[/]")
            
            # Timing loop
            frame_end = time.time() + frame_time
            while time.time() < frame_end:
                pass
    except KeyboardInterrupt:
        pass
    
    clear()


def get_ghost_with_offset(offset):
    # i know this seems like overkill but it's easier than
    # trying to pad each line individually
    return f"""
{' ' * offset}   .-.
{' ' * offset}  (o o)
{' ' * offset}   \\|/
{' ' * offset}    |
{' ' * offset}   / \\
{' ' * offset}  /   \\
    """

def get_ghost_with_color(ghost_text, color):
    # simple trick to colorize the ghost
    return f"[{color}]{ghost_text}[/{color}]"


# Debugging stuff - I use this when testing terminal issues
def _get_term_size():
    """Get terminal size (used for debugging)"""
    # This is a bit hackish but works across platforms
    try:
        columns, lines = shutil.get_terminal_size()
    except:
        try:
            # Fallback for weird terminals
            result = subprocess.run(['stty', 'size'], stdout=subprocess.PIPE)
            lines, columns = map(int, result.stdout.decode().split())
        except:
            # Default if all else fails
            columns, lines = 80, 24
    
    return columns, lines


def show_ghost_logo():
    """Shows a static ghost logo with a randomly chosen color"""
    color = random.choice([
        "bright_blue", "bright_magenta", "bright_cyan", 
        "bright_green", "bright_yellow", "bright_red"
    ])
    console.print(f"[{color}]{logo}[/{color}]")


def show_thank_you_message():
    """Shows a thank you message with heart animation"""
    # Let me go super overboard with this...
    hearts = ["❤️", "💙", "💚", "💛", "💜", "🧡"]
    
    for _ in range(5):  # Number of animation frames
        clear()
        heart = random.choice(hearts)
        
        message = f"""
        
        {heart} Thank you for using GhostyDisk! {heart}
        
        Created with lots of coffee and little sleep
        by someone who really needed to clean up their disk.
        
        {heart} Have a ghostly day! {heart}
        
        """
        
        console.print(Panel(
            Align.center(message),
            border_style=random.choice(["red", "magenta", "cyan", "green", "yellow"]),
            box=box.ROUNDED
        ))
        
        time.sleep(0.3)
    
    time.sleep(2)
    clear()