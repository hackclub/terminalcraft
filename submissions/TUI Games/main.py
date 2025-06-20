import curses
import sys
import importlib.util
import os

def load_game_module(game_file):
    """Load a game module dynamically from a file."""
    spec = importlib.util.spec_from_file_location("game_module", game_file)
    if spec is None:
        raise ImportError(f"Cannot load module from {game_file}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["game_module"] = module
    spec.loader.exec_module(module)
    return module

def draw_ascii_title(stdscr, max_x):
    """Draw ASCII art title centered at the top, with a plain text label above."""

    # ASCII art to make it look Asthetic ka 14
    ascii_art = [
        r" __  __          _____ _   _      __  __ ______ _   _ _    _ ",
        r"|  \/  |   /\   |_   _| \ | |    |  \/  |  ____| \ | | |  | |",
        r"| \  / |  /  \    | | |  \| |    | \  / | |__  |  \| | |  | |",
        r"| |\/| | / /\ \   | | | . ` |    | |\/| |  __| | . ` | |  | |",
        r"| |  | |/ ____ \ _| |_| |\  |    | |  | | |____| |\  | |__| |",
        r"|_|  |_/_/    \_\_____|_| \_|    |_|  |_|______|_| \_|\_____/ ",
    ]
    start_y = 2
    for idx, line in enumerate(ascii_art):
        x = (max_x - len(line)) // 2  #  Art On The Center the line
        y = start_y + idx
        # Draws each character individually & applies color to only non-spaces 
        for char_idx, char in enumerate(line):
            if char != " ":
                stdscr.addstr(y, x + char_idx, char, curses.color_pair(2))
            else:
                stdscr.addstr(y, x + char_idx, char)

def draw_menu_border(stdscr, start_y, end_y, start_x, end_x):
    """Draw a simple border around the menu."""
    stdscr.addstr(start_y, start_x, "┌" + "─" * (end_x - start_x - 1) + "┐")
    for y in range(start_y + 1, end_y):
        stdscr.addstr(y, start_x, "│")
        stdscr.addstr(y, end_x - 1, "│")
    stdscr.addstr(end_y, start_x, "└" + "─" * (end_x - start_x - 1) + "┘")

def main(stdscr):
    # Setting up curses
    curses.curs_set(0)  # Hiding cursor (kisko dikkat na ho hamse)
    stdscr.timeout(100)  # Taking Non-blocking input
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Highlighting color for good looks
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Title Line coloring
    selected_color = curses.color_pair(1) | curses.A_BOLD
    normal_color = curses.color_pair(0) | curses.A_NORMAL

    # Menu selection options
    menu_items = ["Tic-Tac-Toe", "Snakes & Ladders", "Exit"]
    current_selection = 0
    max_y, max_x = stdscr.getmaxyx()

    # Calculating the menu dimensions to fit the terminal
    menu_width = max(len(item) for item in menu_items) + 4
    menu_start_x = (max_x - menu_width) // 2
    menu_end_x = menu_start_x + menu_width
    menu_start_y = max_y // 2 - 2
    menu_end_y = menu_start_y + len(menu_items) + 1

    # Credit text to display in bottom-right corner
    credit_text = "Hardwork By Kaustubh Kharvi"

    while True:
        stdscr.clear()
        # Draw ASCII title from the text
        draw_ascii_title(stdscr, max_x)

        # Drawing menu border to fit the terminal
        draw_menu_border(stdscr, menu_start_y, menu_end_y, menu_start_x, menu_end_x)

        # Display menu items
        for idx, item in enumerate(menu_items):
            y_pos = menu_start_y + 1 + idx
            x_pos = (max_x - len(item)) // 2
            if idx == current_selection:
                stdscr.addstr(y_pos, x_pos, item, selected_color)
            else:
                stdscr.addstr(y_pos, x_pos, item, normal_color)

        # Displaying instructions
        instructions = "Use ↑↓ to navigate, Enter to select"
        stdscr.addstr(max_y - 2, (max_x - len(instructions)) // 2, instructions, curses.color_pair(0))

        # Displaying credit text in bottom-right corner (mehnat ka fal)
        max_y, max_x = stdscr.getmaxyx()  # Refreshing dimensions in case of resize
        credit_x = max_x - len(credit_text) - 1  # 1-character margin from right edge
        credit_y = max_y - 1  # Bottom row
        stdscr.addstr(credit_y, credit_x, credit_text)

        stdscr.refresh()

        # Handles input
        try:
            key = stdscr.getch()
        except:
            key = -1

        if key == curses.KEY_UP and current_selection > 0:
            current_selection -= 1
        elif key == curses.KEY_DOWN and current_selection < len(menu_items) - 1:
            current_selection += 1
        elif key in (curses.KEY_ENTER, 10, 13):
            if current_selection == 0:  # Tic-Tac-Toe Game
                try:
                    tictactoe = load_game_module("tic_tac_toe.py")
                    stdscr.clear()
                    stdscr.refresh()
                    tictactoe.main(stdscr)  # Pass stdscr to Tic-Tac-Toe
                except (ImportError, AttributeError) as e:
                    stdscr.addstr(max_y // 2, (max_x - len("Tic-Tac-Toe not found!")) // 2, "Tic-Tac-Toe not found!", curses.color_pair(1))
                    stdscr.refresh()
                    stdscr.getch()
            elif current_selection == 1:  # Snakes & Ladders Game
                try:
                    snakes = load_game_module("snakes_ladders.py")
                    stdscr.clear()
                    stdscr.refresh()
                    snakes.main(stdscr)  # Pass stdscr to Snakes & Ladders
                except (ImportError, AttributeError) as e:
                    stdscr.addstr(max_y // 2, (max_x - len("Snakes & Ladders not found!")) // 2, "Snakes & Ladders not found!", curses.color_pair(1))
                    stdscr.refresh()
                    stdscr.getch()
            elif current_selection == 2:  # Exit
                break

if __name__ == "__main__":
    curses.wrapper(main)
    
