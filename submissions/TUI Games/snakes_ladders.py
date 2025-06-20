import curses
import random
import time

def draw_board(stdscr, players, current_player, board_size=100):
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    board_cols = 10
    board_rows = board_size // board_cols

    # Fetching game title with border
    title = "Snake and Ladder"
    stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(7))
    stdscr.addstr(1, 2, "=" * (width - 4), curses.color_pair(8))

    # Drawing Game board
    for row in range(board_rows):
        for col in range(board_cols):
            cell_num = board_size - (row * board_cols + col) - 1
            cell_str = f"{cell_num:2}"
            if cell_num in snakes:
                cell_str += " S"
                attr = curses.color_pair(1)
            elif cell_num in ladders:
                cell_str += " L"
                attr = curses.color_pair(2)
            else:
                attr = curses.A_NORMAL
            for i, (player, pos) in enumerate(players.items()):
                if pos == cell_num:
                    cell_str = f"P{i+1}"
                    attr = curses.color_pair(3 + i) | curses.A_BOLD
            x = col * 5 + width // 4
            y = row + 3
            if y < height and x < width:
                stdscr.addstr(y, x, cell_str, attr)

    # Draw player info and instructions
    info_y = board_rows + 4
    if info_y < height:
        stdscr.addstr(info_y, 4, f"Current Player: {current_player}", curses.color_pair(10) | curses.A_BOLD)
        stdscr.addstr(info_y + 1, 4, f"Roll: [SPACE]  Quit: [q]")

    # Draw the signature at bottom right
    signature = "Hardwork By Kaustubh Kharvi"
    if height - 1 < height and width - len(signature) - 2 >= 0:
        stdscr.addstr(height - 1, width - len(signature) - 2, signature, curses.A_NORMAL)

    stdscr.refresh()

def roll_dice():
    return random.randint(1, 6)

def main_game(stdscr, num_players):
    global snakes, ladders
    snakes = {16: 6, 47: 26, 49: 11, 56: 53, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 98: 78}
    ladders = {1: 38, 4: 14, 9: 31, 21: 42, 28: 84, 36: 44, 51: 67, 71: 91, 80: 100}

    players = {f"Player {i+1}": 0 for i in range(num_players)}
    current_player = list(players.keys())[0]
    turn = 0

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)  # Snakes (khatra laal)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Ladders (seedhi upar ki)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Player 1
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_RED)  # Player 2
    if num_players >= 3:
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # Player 3
    if num_players == 4:
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_MAGENTA)  # Player 4
    curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Title
    curses.init_pair(8, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # Borders
    curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Menu highlight
    curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_GREEN)  # Current player highlighter

    roll_message = ""
    snake_message = ""
    while True:
        height, width = stdscr.getmaxyx()
        draw_board(stdscr, players, current_player)
        if roll_message and curses.LINES - 1 < height:
            stdscr.addstr(curses.LINES - 1, (width - len(roll_message)) // 2, roll_message, curses.A_BOLD | curses.color_pair(7))
        elif snake_message and curses.LINES - 1 < height:
            stdscr.addstr(curses.LINES - 1, (width - len(snake_message)) // 2, snake_message, curses.A_BOLD | curses.color_pair(1))
        stdscr.refresh()
        key = stdscr.getch()
        if key == ord('q'):
            return None
        elif key == ord(' '):
            roll = roll_dice()
            roll_message = f"{current_player} rolled: {roll}"
            snake_message = ""
            if curses.LINES - 1 < height:
                stdscr.addstr(curses.LINES - 1, (width - len(roll_message)) // 2, roll_message, curses.A_BOLD | curses.color_pair(7))
            stdscr.refresh()
            time.sleep(1)

            players[current_player] += roll
            if players[current_player] > 100:
                players[current_player] -= roll
            elif players[current_player] == 100:
                draw_board(stdscr, players, current_player)
                if curses.LINES - 2 < height:
                    stdscr.addstr(curses.LINES - 2, (width - len(f"{current_player} wins!")) // 2, f"{current_player} wins!", curses.A_BOLD | curses.color_pair(7))
                stdscr.refresh()
                stdscr.getch()
                return current_player

            # Checks for snakes or ladders (kuch hai toh agar)
            if players[current_player] in snakes:
                old_pos = players[current_player]
                players[current_player] = snakes[players[current_player]]
                snake_message = f"{current_player} hit a snake! Slid from {old_pos} to {players[current_player]}"
                draw_board(stdscr, players, current_player)
                if curses.LINES - 1 < height:
                    stdscr.addstr(curses.LINES - 1, (width - len(snake_message)) // 2, snake_message, curses.A_BOLD | curses.color_pair(1))
                stdscr.refresh()
                time.sleep(1.5)
            elif players[current_player] in ladders:
                players[current_player] = ladders[players[current_player]]

            turn = (turn + 1) % num_players
            current_player = list(players.keys())[turn]
            roll_message = ""

def main_menu(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    menu_items = ["Start Game (2 Players)", "Start Game (3 Players)", "Start Game (4 Players)", "Exit"]
    current_item = 0

    # Initializes additional color pairs
    curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Title
    curses.init_pair(8, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # Borders
    curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Menu highlight
    curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_GREEN)  # Current player highlight

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Checks if terminal is too small
        if height < 15 or width < 50:
            stdscr.addstr(0, 0, "Terminal too small! Resize to at least 100x20 for best display (min 50x15).", curses.A_BOLD)
            # Draws signature even in smaller terminal
            signature = "Hardwork By Kaustubh Kharvi"
            if height - 1 < height and width - len(signature) - 2 >= 0:
                stdscr.addstr(height - 1, width - len(signature) - 2, signature, curses.A_NORMAL)
            stdscr.refresh()
            stdscr.getch()
            continue

        # ASCII art title (isme bhi usi asthetic ke karan hai)
        ascii_art = [
            "   _____ _   _          _  ________             _               _____  _____  ______ _____  ",
            "  / ____| \\ | |   /\\   | |/ /  ____|   ___     | |        /\\   |  __ \\|  __ \\|  ____|  __ \\ ",
            " | (___ |  \\| |  /  \\  | ' /| |__     ( _ )    | |       /  \\  | |  | | |  | | |__  | |__) |",
            "  \\___ \\| . ` | / /\\ \\ |  < |  __|    / _ \\/\\  | |      / /\\ \\ | |  | | |  | |  __| |  _  / ",
            "  ____) | |\\  |/ ____ \\| . \\| |____  | (_>  <  | |____ / ____ \\| |__| | |__| | |____| | \\ \\ ",
            " |_____/|_| \\_/_/    \\_\\_|\\_|______|  \\___/\\/  |______/_/    \\_\\_____/|_____/|______|_|  \\_\\",
            ""
        ]
        for i, line in enumerate(ascii_art):
            if i < height:
                x = (width - len(line)) // 2
                if x >= 0 and x + len(line) < width:
                    stdscr.addstr(i, x, line, curses.A_BOLD | curses.color_pair(7))

        # Draw border
        border_y = len(ascii_art)
        if border_y < height:
            stdscr.addstr(border_y, 2, "=" * (width - 4), curses.color_pair(8))

        # Draw menu items
        menu_start_y = border_y + 2
        for idx, item in enumerate(menu_items):
            x = (width - len(item)) // 2
            y = menu_start_y + idx
            if y < height and x >= 0 and x + len(item) < width:
                if idx == current_item:
                    stdscr.addstr(y, x, item, curses.A_REVERSE | curses.color_pair(9))
                else:
                    stdscr.addstr(y, x, item, curses.color_pair(7))

        # Draw bottom border
        bottom_border_y = menu_start_y + len(menu_items) + 1
        if bottom_border_y < height:
            stdscr.addstr(bottom_border_y, 2, "=" * (width - 4), curses.color_pair(8))

        # Draw signature at bottom right
        signature = "Hardwork By Kaustubh Kharvi"
        if height - 1 < height and width - len(signature) - 2 >= 0:
            stdscr.addstr(height - 1, width - len(signature) - 2, signature, curses.A_NORMAL)

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and current_item > 0:
            current_item -= 1
        elif key == curses.KEY_DOWN and current_item < len(menu_items) - 1:
            current_item += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_item == len(menu_items) - 1:
                return None
            winner = main_game(stdscr, current_item + 2)
            if winner:
                stdscr.clear()
                win_msg = f"{winner} wins! Press any key to continue"
                if height // 2 < height:
                    stdscr.addstr(height // 2, (width - len(win_msg)) // 2, win_msg, curses.A_BOLD | curses.color_pair(7))
                # Draw signature on windows screen
                signature = "Hardwork By Kaustubh Kharvi"
                if height - 1 < height and width - len(signature) - 2 >= 0:
                    stdscr.addstr(height - 1, width - len(signature) - 2, signature, curses.A_NORMAL)
                stdscr.refresh()
                stdscr.getch()

def main(stdscr):
    curses.start_color()
    while True:
        if main_menu(stdscr) is None:
            break

if __name__ == "__main__":
    curses.wrapper(main)
