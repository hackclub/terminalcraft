import curses
from game_logic import update_winner, print_board, move_cursor, has_valid_moves
from minmax import get_computer_move

def play_computer(stdscr, player_letter, easy):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    def make_board():
        return [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
    big_board = [[make_board() for _ in range(3)] for _ in range(3)]
    win_board = [" "] * 9

    computer_letter = "X" if player_letter == "O" else "O"
    current_pos = 0
    player = "X"
    free_move = True
    current_board = 0
    invalid_move_flag = False
    key = None

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

        if player == player_letter:
            key = stdscr.getch()

        if invalid_move_flag:
            stdscr.move(h-1, 0)
            stdscr.clrtoeol()
            invalid_move_flag = False

        if key == ord('q'):
            return
        
        if all(board != " " for board in win_board):
            win_text = "Game is a draw!"
            stdscr.addstr(h-1, w//2 - len(win_text)//2, win_text)
            stdscr.refresh()
            while True:
                stdscr.getch()
                if key == ord('q'):
                    return
        
        if player == player_letter:
            # Had to get the computer moves to test draw because it kept beating me :(
            # move = get_computer_move(big_board, win_board, current_board, computer_letter, player_letter)
            # big_row, big_col, mini_row, mini_col = move
            # stdscr.addstr(h-1, 0, f"Computer chose: Board {big_row * 3 + big_col}, Position {mini_row * 3 + mini_col}")

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

        else: # computer move, picks the first available square, easy mode
            if easy:
                if free_move:
                    made_move = False
                    for i in range(9):
                        if win_board[i] == " ":
                            for j in range(9):
                                big_row = i // 3
                                big_col = i % 3
                                mini_row = j // 3
                                mini_col = j % 3
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
                                    made_move = True
                                    break
                        if made_move:
                            break
                else:
                    for i in range(9):
                        mini_row = i // 3
                        mini_col = i % 3
                        if big_board[big_row][big_col][mini_row][mini_col] == " ":
                            big_board[big_row][big_col][mini_row][mini_col] = player
                            player = "O" if player == "X" else "X"
                            if update_winner(stdscr, current_pos, big_board, win_board, current_board, big_row, big_col):
                                return
                            current_board = mini_row * 3 + mini_col
                            current_pos = (current_board // 3) * 27 + (current_board % 3) * 3
                            if win_board[current_board] != " ":
                                free_move = True
                            break
            else:
                move = get_computer_move(big_board, win_board, current_board, computer_letter, player_letter)
                big_row, big_col, mini_row, mini_col = move
                big_board[big_row][big_col][mini_row][mini_col] = player
                player = "O" if player == "X" else "X"

                if free_move:
                    current_board = big_row * 3 + big_col

                if update_winner(stdscr, current_pos, big_board, win_board, current_board, big_row, big_col):
                    return
                
                current_board = mini_row * 3 + mini_col
                current_pos = (current_board // 3) * 27 + (current_board % 3) * 3
                if win_board[current_board] != " ":
                    free_move = True
                else:
                    free_move = False


