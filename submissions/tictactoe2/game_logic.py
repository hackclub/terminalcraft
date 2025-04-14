import curses

def move_cursor(key, free_move, current_board, current_pos):
    row = current_pos // 9
    col = current_pos % 9

    if free_move:
        row_min, row_max = 0, 8
        col_min, col_max = 0, 8
    else:
        row_min = (current_board // 3) * 3
        col_min = (current_board % 3) * 3
        row_max = row_min + 2
        col_max = col_min + 2
    
    if key == curses.KEY_UP:
        if row > row_min:
            current_pos -= 9
    elif key == curses.KEY_DOWN:
        if row < row_max:
            current_pos += 9
    elif key == curses.KEY_LEFT:
        if col > col_min:
            current_pos -= 1
    elif key == curses.KEY_RIGHT:
        if col < col_max:
            current_pos += 1
    
    return current_pos

def update_winner(stdscr, current_pos, big_board, win_board, current_board, big_row, big_col):
    h, w = stdscr.getmaxyx()

    mini_board = big_board[big_row][big_col]
    winner = check_win(mini_board)
    if winner:
        win_board[current_board] = winner
    elif check_draw_board(mini_board):
        win_board[current_board] = "D"

    overall_winner = check_win([win_board[0:3], win_board[3:6], win_board[6:9]]) # change win_board into 3x3
    if overall_winner and overall_winner != "D":
        print_board(stdscr, current_pos, big_board)
        win_text = f"'{overall_winner}' wins!" 
        stdscr.addstr(h-1, w//2 - len(win_text)//2, win_text)
        stdscr.refresh()
        while True:
            key = stdscr.getch()
            if key == ord('q'):
                return True
    return False

def has_valid_moves(board):
    for row in board:
        if " " in row:
            return True
    return False

def check_draw_board(board):
    if check_win(board) is not None:
        return False
    return not has_valid_moves(board)

def check_win(board):
    for row in board:
        if row[0] == row[1] == row[2] != " ":
            return row[0]
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != " ":
            return board[0][col]
    # check diagonals
    if board[0][0] == board[1][1] == board[2][2] != " ":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != " ":
        return board[0][2]
    return None

def get_win_line(board):
    # returns the wining line from a board
    for r in range(3):
        if board[r][0] == board[r][1] == board[r][2] != " ":
            return [(r, 0), (r, 1), (r, 2)]
    for c in range(3):
        if board[0][c] == board[1][c] == board[2][c] != " ":
            return [(0, c), (1, c), (2, c)]
    if board[0][0] == board[1][1] == board[2][2] != " ":
        return [(0, 0), (1, 1), (2, 2)]
    if board[0][2] == board[1][1] == board[2][0] != " ":
        return [(0, 2), (1, 1), (2, 0)]
    return None

def draw_box(stdscr, top, left, bottom, right):
    stdscr.addch(top, left, '+', curses.A_BOLD)
    stdscr.addch(top, right, '+', curses.A_BOLD)
    stdscr.addch(bottom, left, '+', curses.A_BOLD)
    stdscr.addch(bottom, right, '+', curses.A_BOLD)

    for x in range(left + 1, right):
        stdscr.addch(top, x, '-', curses.A_BOLD)
        stdscr.addch(bottom, x, '-', curses.A_BOLD)

    for y in range(top + 1, bottom):
        stdscr.addch(y, left, '|', curses.A_BOLD)
        stdscr.addch(y, right, '|', curses.A_BOLD)

def print_board(stdscr, current_pos, board):
    h, w = stdscr.getmaxyx()

    mini_board_height = 5
    mini_board_width = 11

    board_start_y = h//2 - (mini_board_height + 1)//2 * 3
    board_start_x = w//2 - (mini_board_width + 1)//2 * 3

    current_row = current_pos // 9
    current_col = current_pos % 9
    
    cell_letters = [1, 5, 9] # location where the X or O is in the cell

    for row in range(3):
        for col in range(3):
            mini = board[row][col]

            top_y = board_start_y + row * (mini_board_height + 1) # spacing
            left_x = board_start_x + col * (mini_board_width + 1)
            bottom_y = top_y + mini_board_height
            right_x = left_x + mini_board_width

            draw_box(stdscr, top_y - 1, left_x - 1, bottom_y, right_x)

            win_line = get_win_line(mini)

            for m_row in range(3):
                y_location = top_y + m_row * 2 # each row adds 2 spaces (a letter and -)
                
                line_temp = list("   |   |   ") # line template
                
                # updating the template values based on the board
                for m_col in range(3):
                    pos = cell_letters[m_col]
                    line_temp[pos] = mini[m_row][m_col]
                
                # update cells
                for i, char in enumerate(line_temp):
                    x_location = left_x + i

                    # checks if a cell is part of a winline
                    in_win_line = False
                    if win_line is not None:
                        cell_index = cell_letters.index(i) if i in cell_letters else -1
                        if (m_row, cell_index) in win_line:
                            in_win_line = True

                    if i in cell_letters:
                        cell_index = cell_letters.index(i)
                        # current position cell
                        if (row * 3 + m_row == current_row and col * 3 + cell_index == current_col):
                            stdscr.attron(curses.color_pair(1))
                            stdscr.addch(y_location, x_location, char)
                            stdscr.attroff(curses.color_pair(1))
                        # winning cells
                        elif i in cell_letters and in_win_line:
                            stdscr.attron(curses.color_pair(2))
                            stdscr.addch(y_location, x_location, char)
                            stdscr.attroff(curses.color_pair(2))
                        else:
                            stdscr.addch(y_location, x_location, char)
                    else:
                        stdscr.addch(y_location, x_location, char)

                if m_row < 2:
                    divider = "---+---+---"
                    stdscr.addstr(y_location + 1, left_x, divider)
    
    stdscr.refresh()
