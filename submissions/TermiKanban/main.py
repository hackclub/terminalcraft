import copy
import curses
import os

from kanban_board import KanbanBoard

# Constants for color pairs
LOW_PRIORITY = 1
MEDIUM_PRIORITY = 2
HIGH_PRIORITY = 3

def draw_board(stdscr, board, selected_col=0, selected_card=0):
    """
    Draw the Kanban board on the screen with columns and cards.
    
    Args:
        stdscr: The curses window object
        board: KanbanBoard instance containing columns and cards
        selected_col: Currently selected column index
        selected_card: Currently selected card index
    """
    curses.curs_set(0)  # Hide the cursor
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    col_width = width // len(board.columns) if board.columns else width

    # Draw each column and its cards
    for i, column in enumerate(board.columns):
        x_start = i * col_width
        stdscr.addstr(0, x_start, column.name, curses.A_BOLD)
        y_offset = 2
        # Sort cards by priority (high to low)
        sorted_cards = sorted(column.cards, key=lambda c: c.priority, reverse=True)
        for j, card in enumerate(sorted_cards):
            color = curses.color_pair(card.priority)
            # Highlight selected card
            attr = color | (curses.A_REVERSE if i == selected_col and j == selected_card else 0)
            if y_offset < height - 1:
                stdscr.addstr(y_offset, x_start, f"- {card.title}", attr)
                y_offset += 1
                if y_offset < height:
                    stdscr.addstr(y_offset, x_start + 2, f"{card.description}", attr)
                    y_offset += 1
    stdscr.refresh()

def file_picker(stdscr, path="."):
    """
    Display a file selection menu for .kanban files.
    
    Args:
        stdscr: The curses window object
        path: Directory path to search for .kanban files
        
    Returns:
        str: Selected file path or None if cancelled
    """
    files = [f for f in os.listdir(path) if f.endswith(".kanban")]
    if not files:
        stdscr.addstr(15, 0, "No .kanban files found.")
        stdscr.getch()
        return None
    
    idx = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Select a file to open:")
        # Display file list with selection highlight
        for i, fname in enumerate(files):
            if i == idx:
                stdscr.addstr(i + 2, 2, fname, curses.A_REVERSE)
            else:
                stdscr.addstr(i + 2, 2, fname)
        
        key = stdscr.getch()
        # Handle navigation
        if key in (curses.KEY_UP, ord('k')) and idx > 0:
            idx -= 1
        elif key in (curses.KEY_DOWN, ord('j')) and idx < len(files) - 1:
            idx += 1
        elif key in (curses.KEY_ENTER, 10, 13):
            return os.path.join(path, files[idx])
        elif key == 27:  # ESC to cancel
            return None

def get_input(stdscr, y, x, prompt, max_length):
    """
    Get user input with a prompt and maximum length limit.
    
    Args:
        stdscr: The curses window object
        y, x: Screen coordinates for the prompt
        prompt: Text to display before input
        max_length: Maximum allowed input length
        
    Returns:
        str: User input string
    """
    curses.curs_set(1)  # Show cursor
    stdscr.addstr(y, x, prompt)
    stdscr.refresh()
    inp = ""
    
    while True:
        key = stdscr.getch(y, x + len(prompt) + len(inp))
        if key in (curses.KEY_ENTER, 10, 13):  # Enter key
            break
        elif key in (curses.KEY_BACKSPACE, 127, 8):  # Backspace
            if len(inp) > 0:
                inp = inp[:-1]
                stdscr.addstr(y, x + len(prompt), inp + " " * (max_length - len(inp)))
                stdscr.move(y, x + len(prompt) + len(inp))
        elif 32 <= key <= 126 and len(inp) < max_length:  # Printable characters
            inp += chr(key)
            stdscr.addstr(y, x + len(prompt), inp)
        stdscr.refresh()
    curses.curs_set(0)  # Hide cursor
    return inp

def show_help(stdscr):
    """Display help window with keybindings and controls."""
    help_text = [
        "Keybinds:",
        "  Arrow keys: Move selection",
        "  a: Add card",
        "  d: Delete card",
        "  e: Edit card",
        "  m: Move card right",
        "  b: Move card left",
        "  c: Add column",
        "  [: Move column left",
        "  ]: Move column right",
        "  s: Save board",
        "  o: Open board",
        "  z: Undo",
        "  x: Redo",
        "  p: Change card priority",
        "  h: Show this help menu",
        "  q: Quit",
        "",
        "Press any key to return..."
    ]
    
    # Create centered window for help text
    height, width = stdscr.getmaxyx()
    win_height = len(help_text) + 2
    win_width = max(len(line) for line in help_text) + 4
    win = curses.newwin(win_height, win_width, (height - win_height) // 2, (width - win_width) // 2)
    win.box()
    
    # Display help text
    for idx, line in enumerate(help_text):
        win.addstr(idx + 1, 2, line)
    win.refresh()
    win.getch()

def main(stdscr):
    """
    Main application function implementing the Kanban board interface.
    """
    # Initialize color pairs for priority levels
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Low priority
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Medium priority
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)     # High priority
    
    # Initialize board with default columns
    board = KanbanBoard()
    board.add_column("To Do")
    board.add_column("In Progress")
    board.add_column("Done")
    board.add_card(0, "Task 1", "Description for Task 1", 3)
    board.add_card(1, "Task 2", "Description for Task 2", 2)
    board.add_card(2, "Task 3", "Description for Task 3", 1)

    # Initialize undo/redo stacks and selection state
    undo_stack = []
    redo_stack = []
    selected_col = 0
    selected_card = 0

    def snapshot():
        """Create a snapshot of current board state for undo/redo functionality."""
        undo_stack.append(copy.deepcopy(board))
        redo_stack.clear()

    # Main event loop
    while True:
        draw_board(stdscr, board, selected_col, selected_card)
        key = stdscr.getch()

        # Create snapshot before modifications
        if key in (ord('a'), ord('d'), ord('e'), ord('c'), ord('m'), ord('b'), ord('['), ord(']')):
            snapshot()
            
        # Handle user input
        if key == ord('q'):
            # Quit with save option
            stdscr.addstr(15, 0, "Save before exit? (y/n): ")
            stdscr.refresh()
            confirm = stdscr.getch()
            if confirm in (ord('y'), ord('Y')):
                save_name = get_input(stdscr, 16, 0, "Name:", 10)
                board.save(f"{save_name}.kanban")
                break
            elif confirm in (ord('n'), ord('N')):
                break
            stdscr.clear()
        
        # Navigation controls
        elif key == curses.KEY_RIGHT and selected_col < len(board.columns) - 1:
            selected_col += 1
            selected_card = 0
        elif key == curses.KEY_LEFT and selected_col > 0:
            selected_col -= 1
            selected_card = 0
        elif key == curses.KEY_DOWN and selected_card < len(board.columns[selected_col].cards) - 1:
            selected_card += 1
        elif key == curses.KEY_UP and selected_card > 0:
            selected_card -= 1
            
        # Card movement
        elif key == ord('m'):  # Move card right
            if selected_col < len(board.columns) - 1 and board.columns[selected_col].cards:
                card = board.columns[selected_col].cards.pop(selected_card)
                board.columns[selected_col + 1].cards.append(card)
                if selected_card >= len(board.columns[selected_col].cards):
                    selected_card = max(0, len(board.columns[selected_col].cards) - 1)
                selected_col += 1
        elif key == ord('b'):  # Move card left
            if selected_col > 0 and board.columns[selected_col].cards:
                card = board.columns[selected_col].cards.pop(selected_card)
                board.columns[selected_col - 1].cards.append(card)
                if selected_card >= len(board.columns[selected_col].cards):
                    selected_card = max(0, len(board.columns[selected_col].cards) - 1)
                selected_col -= 1
                
        # Card management
        elif key == ord('d'):  # Delete card
            if board.columns[selected_col].cards:
                board.columns[selected_col].cards.pop(selected_card)
                if selected_card >= len(board.columns[selected_col].cards):
                    selected_card = max(0, len(board.columns[selected_col].cards) - 1)
        elif key == ord('a'):  # Add card
            title = get_input(stdscr, 15, 0, "Title: ", 20)
            description = get_input(stdscr, 16, 0, "Description: ", 40)
            priority_str = get_input(stdscr, 17, 0, "Priority (1=Low, 2=Med, 3=High): ", 1)
            priority = int(priority_str) if priority_str in ("1", "2", "3") else 1
            board.add_card(0, title, description, priority)
        elif key == ord('e'):  # Edit card
            if board.columns[selected_col].cards:
                card = board.columns[selected_col].cards[selected_card]
                new_title = get_input(stdscr, 15, 0, f"Edit Title ({card.title}): ", 20)
                new_description = get_input(stdscr, 16, 0, f"Edit Description ({card.description}): ", 40)
                card.title = new_title if new_title else card.title
                card.description = new_description if new_description else card.description
                stdscr.clear()
                
        # Board management
        elif key == ord('s'):  # Save board
            save_name = get_input(stdscr, 15, 0, "Filename:", 10)
            board.save(f"{save_name}.kanban")
        elif key == ord('o'):  # Open board
            file_path = file_picker(stdscr)
            if file_path:
                board = KanbanBoard()
                board.load(file_path)
        elif key == ord('c'):  # Add column
            col_name = get_input(stdscr, 15, 0, "New column name: ", 20)
            if col_name:
                board.add_column(col_name)
                selected_col = len(board.columns) - 1
                selected_card = 0
            stdscr.clear()
            
        # Column movement
        elif key == ord('['):  # Move column left
            if selected_col > 0:
                board.columns[selected_col - 1], board.columns[selected_col] = board.columns[selected_col], \
                board.columns[selected_col - 1]
                selected_col -= 1
        elif key == ord(']'):  # Move column right
            if selected_col < len(board.columns) - 1:
                board.columns[selected_col + 1], board.columns[selected_col] = board.columns[selected_col], \
                board.columns[selected_col + 1]
                selected_col += 1
                
        # Undo/Redo
        elif key == ord('z'):  # Undo
            if undo_stack:
                redo_stack.append(copy.deepcopy(board))
                board = undo_stack.pop()
        elif key == ord('x'):  # Redo
            if redo_stack:
                undo_stack.append(copy.deepcopy(board))
                board = redo_stack.pop()
                
        # Other functions
        elif key == ord('p'):  # Change priority
            if board.columns[selected_col].cards:
                card = board.columns[selected_col].cards[selected_card]
                card.priority = card.priority % 3 + 1
        elif key == ord('h'):  # Show help
            show_help(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)