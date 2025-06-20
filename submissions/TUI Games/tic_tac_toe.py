import curses
import time
import datetime

def draw_menu(stdscr, selected_option):
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()

    # ASCII art (same same asthetic ka 14)
    heading = [
        r" _______ _____ _____   _______       _____   _______ ____  ______ ",
        r"|__   __|_   _/ ____| |__   __|/\   / ____| |__   __/ __ \|  ____|",
        r"   | |    | || |   ______| |  /  \ | |   ______| | | |  | | |__   ",
        r"   | |    | || |  |______| | / /\ \| |  |______| | | |  | |  __|  ",
        r"   | |   _| || |____     | |/ ____ \ |____     | | | |__| | |____ ",
        r"   |_|  |_____\_____|    |_/_/    \_\_____|    |_|  \____/|______|"
    ]
    heading_width = len(heading[0])
    heading_x = (max_x - heading_width) // 2
    heading_y = 1

    # Draw the center heading in red
    stdscr.attron(curses.A_BOLD | curses.color_pair(2))
    for i, line in enumerate(heading):
        stdscr.addstr(heading_y + i, heading_x, line)
    stdscr.attroff(curses.A_BOLD | curses.color_pair(2))

    # Selection Menu options
    options = ["2 Players", "3 Players", "4 Players", "Exit Game"]
    instructions = "Arrow keys: Navigate | Enter: Select"
    instructions_x = (max_x - len(instructions)) // 2
    instructions_y = heading_y + len(heading) + 1
    stdscr.addstr(instructions_y, instructions_x, instructions)

    # Draw menu options
    menu_y = instructions_y + 2
    for i, option in enumerate(options):
        option_x = (max_x - len(option)) // 2
        if i == selected_option:
            stdscr.attron(curses.A_BOLD | curses.color_pair(4))
            stdscr.addstr(menu_y + i, option_x, option)
            stdscr.attroff(curses.A_BOLD | curses.color_pair(4))
        else:
            stdscr.addstr(menu_y + i, option_x, option)

    # Date and time display
    date_time = datetime.datetime.now().strftime("%I:%M %p %Z, %a, %b %d, %Y")
    date_time_x = (max_x - len(date_time)) // 2
    date_time_y = menu_y + len(options) + 1
    stdscr.addstr(date_time_y, date_time_x, date_time)

    # Draw signature at bottom right
    signature = "Hardwork By Kaustubh Kharvi"
    if max_y - 1 < max_y and max_x - len(signature) - 2 >= 0:
        stdscr.addstr(max_y - 1, max_x - len(signature) - 2, signature, curses.A_NORMAL)

    stdscr.refresh()
    return max_x, max_y

def draw_board(stdscr, board, selected_row, selected_col, current_player, num_players):
    stdscr.clear()
    
    # Get terminal dimensions (chota nahi chalega)
    max_y, max_x = stdscr.getmaxyx()
    
    # Reduced-size ASCII art (bohot bada bhi nahi chalega)
    heading = "TIC TAC TOE"
    heading_width = len(heading)
    heading_x = (max_x - heading_width) // 2
    heading_y = 1
    
    # Draw the heading in red
    stdscr.attron(curses.A_BOLD | curses.color_pair(2))
    stdscr.addstr(heading_y, heading_x, heading)
    stdscr.attroff(curses.A_BOLD | curses.color_pair(2))
    
    # Instructions (taaki sahi se khel sake)
    instructions = "Arrow keys: Move | Enter: Place | Q: Menu"
    instructions_x = (max_x - len(instructions)) // 2
    instructions_y = heading_y + 2
    stdscr.addstr(instructions_y, instructions_x, instructions)
    
    # Calculate the board dimensions and center it (acha dikhna chhaiye na)
    board_width = 26
    board_height = 12
    board_x = (max_x - board_width) // 2
    board_y = instructions_y + 2
    
    # Draw top border
    stdscr.addstr(board_y - 1, board_x, "┏━━━━━┳━━━━━┳━━━━━┓")
    
    # Draw the board cells and borders
    for row in range(3):
        for line in range(3):
            y_pos = board_y + row * 4 + line
            for col in range(3):
                cell = board[row][col]
                x_pos = board_x + col * 8
                if row == selected_row and col == selected_col:
                    stdscr.attron(curses.A_BOLD | curses.color_pair(4))
                    if cell == " ":
                        stdscr.addstr(y_pos, x_pos, "  *  ")
                    else:
                        stdscr.addstr(y_pos, x_pos, f" {cell} ")
                    stdscr.attroff(curses.A_BOLD | curses.color_pair(4))
                else:
                    if cell == "X":
                        stdscr.attron(curses.color_pair(2))
                        stdscr.addstr(y_pos, x_pos, f" {cell} ")
                        stdscr.attroff(curses.color_pair(2))
                    elif cell == "O":
                        stdscr.attron(curses.color_pair(3))
                        stdscr.addstr(y_pos, x_pos, f" {cell} ")
                        stdscr.attroff(curses.color_pair(3))
                    elif cell == "A":
                        stdscr.attron(curses.color_pair(5))
                        stdscr.addstr(y_pos, x_pos, f" {cell} ")
                        stdscr.attroff(curses.color_pair(5))
                    elif cell == "B":
                        stdscr.attron(curses.color_pair(6))
                        stdscr.addstr(y_pos, x_pos, f" {cell} ")
                        stdscr.attroff(curses.color_pair(6))
                    else:
                        stdscr.addstr(y_pos, x_pos, "    ")
        # Draw mid-row horizontal separators
        if row < 2:
            stdscr.addstr(board_y + row * 4 + 3, board_x, "┣━━━━━╋━━━━━╋━━━━━┫")
    
    # Draw bottom border
    stdscr.addstr(board_y + 11, board_x, "┗━━━━━┻━━━━━┻━━━━━┛")
    
    # Draw vertical separators
    for row in range(3):
        for line in range(4):  # Cover lines within each cell
            y_pos = board_y + row * 4 + line
            # Skip lines where horizontal borders are drawn
            if (row < 2 and line == 3) or (row == 0 and line == 0) or (row == 2 and line == 3):
                continue
            stdscr.addstr(y_pos, board_x + 6, "┃")
            stdscr.addstr(y_pos, board_x + 14, "┃")
    
    # Player info (pata toh chale kon khel rha)
    player_info = f"Player: {current_player}"
    player_info_x = (max_x - len(player_info)) // 2
    player_info_y = board_y + board_height + 1
    stdscr.attron(curses.A_BOLD)
    stdscr.addstr(player_info_y, player_info_x, player_info)
    if current_player == "X":
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(player_info_y, player_info_x + 8, "X")
        stdscr.attroff(curses.color_pair(2))
    elif current_player == "O":
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(player_info_y, player_info_x + 8, "O")
        stdscr.attroff(curses.color_pair(3))
    elif current_player == "A":
        stdscr.attron(curses.color_pair(5))
        stdscr.addstr(player_info_y, player_info_x + 8, "A")
        stdscr.attroff(curses.color_pair(5))
    elif current_player == "B":
        stdscr.attron(curses.color_pair(6))
        stdscr.addstr(player_info_y, player_info_x + 8, "B")
        stdscr.attroff(curses.color_pair(6))
    stdscr.attroff(curses.A_BOLD)

    # Date and time display
    date_time = datetime.datetime.now().strftime("%I:%M %p %Z, %a, %b %d, %Y")
    date_time_x = (max_x - len(date_time)) // 2
    date_time_y = player_info_y + 1
    stdscr.addstr(date_time_y, date_time_x, date_time)

    # Draw signature at bottom right
    signature = "Hardwork By Kaustubh Kharvi"
    if max_y - 1 < max_y and max_x - len(signature) - 2 >= 0:
        stdscr.addstr(max_y - 1, max_x - len(signature) - 2, signature, curses.A_NORMAL)

    stdscr.refresh()
    return board_x, board_y, max_x, max_y

def check_winner(board, player):
    for row in board:
        if all(cell == player for cell in row):
            return True
    for col in range(3):
        if all(board[row][col] == player for row in range(3)):
            return True
    if all(board[i][i] == player for i in range(3)):
        return True
    if all(board[i][2-i] == player for i in range(3)):
        return True
    return False

def is_board_full(board):
    return all(cell != " " for row in board for cell in row)

def main(stdscr):
    curses.curs_set(0)  # Hide cursor 
    # Initialize colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Unused
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # X ka color and title
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)   # O ka color
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_YELLOW) # Selected cell highlight
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)  # A ka color
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # B ka color
    
    # Check terminal size
    max_y, max_x = stdscr.getmaxyx()
    if max_y < 20 or max_x < 90:
        stdscr.clear()
        stdscr.addstr(0, 0, "Error: Terminal too small. Resize to at least 90x20.")
        stdscr.addstr(1, 0, "Press any key to exit.")
        # Draw signature at bottom right
        signature = "Hardwork By Kaustubh Kharvi"
        if max_y - 1 < max_y and max_x - len(signature) - 2 >= 0:
            stdscr.addstr(max_y - 1, max_x - len(signature) - 2, signature, curses.A_NORMAL)
        stdscr.refresh()
        stdscr.getch()
        return

    while True:
        # Player selection menu
        selected_option = 0
        while True:
            max_x, max_y = draw_menu(stdscr, selected_option)
            if max_y < 20 or max_x < 90:
                stdscr.clear()
                stdscr.addstr(0, 0, "Error: Terminal too small. Resize to at least 90x20.")
                stdscr.addstr(1, 0, "Press any key to exit.")
                # Draw signatuer at bottom right
                signature = "Hardwork By Kaustubh Kharvi"
                if max_y - 1 < max_y and max_x - len(signature) - 2 >= 0:
                    stdscr.addstr(max_y - 1, max_x - len(signature) - 2, signature, curses.A_NORMAL)
                stdscr.refresh()
                stdscr.getch()
                return
            key = stdscr.getch()
            if key == curses.KEY_UP and selected_option > 0:
                selected_option -= 1
            elif key == curses.KEY_DOWN and selected_option < 3:  # 4 options
                selected_option += 1
            elif key == 10:  # Enter key
                if selected_option == 3:  # Exit Game
                    return
                num_players = selected_option + 2  # Maps (0->2, 1->3, 2->4)
                break
            elif key == curses.KEY_RESIZE:
                stdscr.clear()
                max_y, max_x = stdscr.getmaxyx()

        # Initialize game
        board = [[" " for _ in range(3)] for _ in range(3)]
        current_player = "X"
        player_symbols = ["X", "O", "A", "B"][:num_players]
        selected_row, selected_col = 0, 0
        player_index = 0

        while True:
            board_x, board_y, max_x, max_y = draw_board(stdscr, board, selected_row, selected_col, current_player, num_players)
            if max_y < 20 or max_x < 90:
                stdscr.clear()
                stdscr.addstr(0, 0, "Error: Terminal too small. Resize to at least 90x20.")
                stdscr.addstr(1, 0, "Press any key to exit.")
                # Draw signature at bottom right
                signature = "Hardwork By Kaustubh Kharvi"
                if max_y - 1 < max_y and max_x - len(signature) - 2 >= 0:
                    stdscr.addstr(max_y - 1, max_x - len(signature) - 2, signature, curses.A_NORMAL)
                stdscr.refresh()
                stdscr.getch()
                return
            key = stdscr.getch()

            # Handle resizer
            if key == curses.KEY_RESIZE:
                stdscr.clear()
                continue

            # Navigation
            if key == curses.KEY_UP and selected_row > 0:
                selected_row -= 1
            elif key == curses.KEY_DOWN and selected_row < 2:
                selected_row += 1
            elif key == curses.KEY_LEFT and selected_col > 0:
                selected_col -= 1
            elif key == curses.KEY_RIGHT and selected_col < 2:
                selected_col += 1
            elif key == 10:  # Enter key
                if board[selected_row][selected_col] == " ":
                    board[selected_row][selected_col] = current_player
                    if check_winner(board, current_player):
                        draw_board(stdscr, board, selected_row, selected_col, current_player, num_players)
                        stdscr.attron(curses.A_BOLD | curses.color_pair(2 if current_player == "X" else 3 if current_player == "O" else 5 if current_player == "A" else 6))
                        win_msg = f"Player {current_player} wins! R: Retry | M: Menu | Q: Quit"
                        win_msg_x = (max_x - len(win_msg)) // 2
                        stdscr.addstr(board_y + 13, win_msg_x, win_msg)
                        stdscr.attroff(curses.A_BOLD | curses.color_pair(2 if current_player == "X" else 3 if current_player == "O" else 5 if current_player == "A" else 6))
                        # Draw signature at bottom right
                        signature = "Hardwork By Kaustubh Kharvi"
                        if max_y - 1 < max_y and max_x - len(signature) - 2 >= 0:
                            stdscr.addstr(max_y - 1, max_x - len(signature) - 2, signature, curses.A_NORMAL)
                        stdscr.refresh()
                        while True:
                            key = stdscr.getch()
                            if key == ord('r') or key == ord('R'):
                                break  # Retry: Break inner loop to start new game 
                            elif key == ord('m') or key == ord('M'):
                                break  # Menu: Break inner loop to return to menu
                            elif key == ord('q') or key == ord('Q'):
                                return  # Quit: Exit the game
                        if key == ord('m') or key == ord('M'):
                            break  # Return to menu
                        continue  # Start new game
                    if is_board_full(board):
                        draw_board(stdscr, board, selected_row, selected_col, current_player, num_players)
                        stdscr.attron(curses.A_BOLD)
                        draw_msg = "Draw! R: Retry | M: Menu | Q: Quit"
                        draw_msg_x = (max_x - len(draw_msg)) // 2
                        stdscr.addstr(board_y + 13, draw_msg_x, draw_msg)
                        stdscr.attroff(curses.A_BOLD)
                        # Draw signature at bottom right
                        signature = "Hardwork By Kaustubh Kharvi"
                        if max_y - 1 < max_y and max_x - len(signature) - 2 >= 0:
                            stdscr.addstr(max_y - 1, max_x - len(signature) - 2, signature, curses.A_NORMAL)
                        stdscr.refresh()
                        while True:
                            key = stdscr.getch()
                            if key == ord('r') or key == ord('R'):
                                break  # Retry: Break inner loop to start new game
                            elif key == ord('m') or key == ord('M'):
                                break  # Menu: Break inner loop to return to menu
                            elif key == ord('q') or key == ord('Q'):
                                return  # Quit: Exit the game
                        if key == ord('m') or key == ord('M'):
                            break  # Return to menu
                        continue  # Start new game
                    player_index = (player_index + 1) % num_players
                    current_player = player_symbols[player_index]
            elif key == ord('q') or key == ord('Q'):
                break  # Return to menu

if __name__ == "__main__":
    curses.wrapper(main)
