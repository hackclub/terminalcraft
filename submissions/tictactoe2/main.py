import curses
from game_logic import update_winner, print_board, move_cursor, has_valid_moves
from computer import play_computer

def play_human(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    def make_board():
        return [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
    big_board = [[make_board() for _ in range(3)] for _ in range(3)]
    win_board = [" "] * 9

    current_pos = 0
    player = "X"
    free_move = True
    current_board = 0
    invalid_move_flag = False

    while True:      
        row = current_pos // 9
        col = current_pos % 9
        
        big_row = row // 3
        big_col = col // 3
        
        mini_row = row % 3
        mini_col = col % 3
        
        # debugging
        # stdscr.addstr(h-3, 0, f"Mini Board Row: {big_row}, Mini Board Col: {big_col}")
        # stdscr.addstr(h-4, 0, f"Mini Row: {mini_row}, Mini Col: {mini_col}")
        # stdscr.addstr(h-5, 0, f"Row: {row}, Col: {col}")
        # stdscr.addstr(h-6, 0, f"Win Board: {win_board[big_row * 3 + big_col]}")
        # stdscr.addstr(h-7, 0, f"Current Board: {current_board}")

        stdscr.addstr(h-2, 0, f"Current Player: {player}")

        print_board(stdscr, current_pos, big_board)
        key = stdscr.getch()

        if invalid_move_flag:
            stdscr.move(h-1, 0)
            stdscr.clrtoeol()
            invalid_move_flag = False

        if key == ord('q'):
            return
        
        # check for a draw
        active_mini_board = big_board[big_row][big_col]
        if not has_valid_moves(active_mini_board):
            free_move = True
            if all(not has_valid_moves(board) for row in big_board for board in row):
                win_text = "Game is a draw!"
                stdscr.addstr(h-1, w//2 - len(win_text)//2, win_text)
                stdscr.refresh()
                stdscr.getch()
                return
        
        if free_move:
            current_pos = move_cursor(key, free_move, current_board, current_pos)
            current_board = big_row * 3 + big_col

            if (key == curses.KEY_ENTER or key in [10, 13]):
                if win_board[big_row * 3 + big_col] == " ":
                    if big_board[big_row][big_col][mini_row][mini_col] == " ":
                        big_board[big_row][big_col][mini_row][mini_col] = player
                        player = "O" if player == "X" else "X"

                        if update_winner(stdscr, current_pos, big_board, win_board, current_board, big_row, big_col):
                            return

                        free_move = False
                        current_board = mini_row * 3 + mini_col
                        current_pos = (current_board // 3) * 27 + (current_board % 3) * 3

                        if win_board[current_board] != " ":
                            free_move = True
                    else:
                        invalid_text = "Invalid move"
                        stdscr.addstr(h-1, w//2 - len(invalid_text)//2, invalid_text)
                        invalid_move_flag = True
                else:
                    invalid_text = f"'{win_board[big_row * 3 + big_col]}' won this board. Pick a different board"
                    stdscr.addstr(h-1, w//2 - len(invalid_text)//2, invalid_text)
                    invalid_move_flag = True
                    
        else: # player is restricted to a certain miniboard
            current_pos = move_cursor(key, free_move, current_board, current_pos)

            if key in [curses.KEY_ENTER, 10, 13]:
                if big_board[big_row][big_col][mini_row][mini_col] == " ":
                    big_board[big_row][big_col][mini_row][mini_col] = player
                    player = "O" if player == "X" else "X"

                    if update_winner(stdscr, current_pos, big_board, win_board, current_board, big_row, big_col):
                        return
                    
                    current_board = mini_row * 3 + mini_col
                    current_pos = (current_board // 3) * 27 + (current_board % 3) * 3

                    if win_board[current_board] != " ":
                        free_move = True

                else:
                    invalid_text = "Invalid move"
                    stdscr.addstr(h-1, w//2 - len(invalid_text)//2, invalid_text)
                    invalid_move_flag = True

def rules(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    rules = [
        "Tic Tac Toe 2 Rules:",
        "",
        "1. The big board has 9 mini boards (3x3 grid).",
        "2. On your turn, mark an empty cell in the active mini board.",
        "3. Your cell's position sends your opponent to that corresponding mini board.",
        "   (e.g., top-left cell sends them to the top-left board.)",
        "4. If that board is already won or full, they may choose any board.",
        "5. Win a mini board (3 in a row) to claim it on the big board.",
        "6. Win the game by claiming 3 mini boards in a row.",
        "",
        "Press q to return to the main menu",
        "Use the arrow keys to move around",
        "Press enter to select a cell"
    ]
    
    y = 1
    for idx, line in enumerate(rules):
        x = 1
        stdscr.addstr(y + idx, x, line)

    x = w//2 - len("Return")//2
    y = h - 2
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(y, x, "Return")
    stdscr.attroff(curses.color_pair(1))

    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key == curses.KEY_ENTER or key in [10, 13] or key == ord('q'):
            return

def play_computer_menu(stdscr):
    h, w = stdscr.getmaxyx()
    text = "Play As:"

    current_selection = "X"
    y = h//2 + 2
    o_x = w//2 + 1
    x_x = w//2 - 2

    while True:
        stdscr.clear()
        
        stdscr.addstr(h//2, w//2-len(text)//2, text)

        if current_selection == "X":
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x_x, "X")
            stdscr.attroff(curses.color_pair(1))

            stdscr.addstr(y, o_x, "O")
        else:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, o_x, "O")
            stdscr.attroff(curses.color_pair(1))

            stdscr.addstr(y, x_x, "X")
        
        key = stdscr.getch()

        if key == curses.KEY_RIGHT and current_selection == "X":
            current_selection = "O"
        elif key == curses.KEY_LEFT and current_selection == "O":
            current_selection = "X"
        elif key == ord('q'):
            return
        elif key == curses.KEY_ENTER or key in [10, 13]:
            choose_difficulty_menu(stdscr, current_selection)

def choose_difficulty_menu(stdscr, player_letter):
    h, w = stdscr.getmaxyx()
    text = "Choose difficultly:"

    current_selection = "Easy"
    y = h//2 + 2
    o_x = w//2 + 3
    x_x = w//2 - 4

    while True:
        stdscr.clear()
        
        stdscr.addstr(h//2, w//2-len(text)//2, text)

        if current_selection == "Easy":
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x_x, "Easy")
            stdscr.attroff(curses.color_pair(1))

            stdscr.addstr(y, o_x, "Hard")
        else:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, o_x, "Hard")
            stdscr.attroff(curses.color_pair(1))

            stdscr.addstr(y, x_x, "Easy")
        
        key = stdscr.getch()

        if key == curses.KEY_RIGHT and current_selection == "Easy":
            current_selection = "Hard"
        elif key == curses.KEY_LEFT and current_selection == "Hard":
            current_selection = "Easy"
        elif key == ord('q'):
            return
        elif key == curses.KEY_ENTER or key in [10, 13]:
            diffculty = True if current_selection == "Easy" else False
            play_computer(stdscr, player_letter, diffculty)

def print_menu(stdscr, current_row):
    h, w = stdscr.getmaxyx()

    for idx, row in enumerate(menu):
        x = w//2 - len(row)//2
        y = h//2 - len(menu)//2 + idx

        if idx == current_row:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, row)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, row)
    
    stdscr.refresh()

def main(stdscr):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    stdscr.clear()

    current_row = 0
    print_menu(stdscr, current_row)

    while True:
        key = stdscr.getch()
        stdscr.clear()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if menu[current_row] == "Exit":
                break
            elif menu[current_row] == "Rules":
                rules(stdscr)
                stdscr.clear()
            elif menu[current_row] == "Player Vs Player":
                play_human(stdscr)
                stdscr.clear()
            elif menu[current_row] == "Play Vs Computer":
                play_computer_menu(stdscr)
                stdscr.clear()
        
        print_menu(stdscr, current_row)

if __name__ == '__main__':
    menu = ["Player Vs Player", "Play Vs Computer", "Rules", "Exit"]

    curses.wrapper(main)
