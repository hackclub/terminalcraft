"""Edit version of https://github.com/amazingly-abhay/sudoku-cli/ """
import random
import curses

def generate_board(difficulty='easy'):
    board = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
    empty_cells = {'easy': 10, 'medium': 20, 'hard': 30}.get(difficulty, 10)
    for _ in range(empty_cells):
        x, y = random.randint(0, 8), random.randint(0, 8)
        board[x][y] = 0
    return board

def is_valid_move(board, row, col, num):
    if num in board[row]:
        return False
    if num in [board[i][col] for i in range(9)]:
        return False
    box_x, box_y = (col // 3) * 3, (row // 3) * 3
    for i in range(3):
        for j in range(3):
            if board[box_y + i][box_x + j] == num:
                return False
    return True

def is_solved(board):
    return all(0 not in row for row in board)

def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    try:
        height, width = stdscr.getmaxyx()
        if height < 15 or width < 40:
            stdscr.addstr(0, 0, "Terminal too small. Resize and restart.")
            stdscr.refresh()
            stdscr.getch()
            return
    except:
        return
    
    difficulty = 'medium'
    board = generate_board(difficulty)
    cursor_x, cursor_y = 0, 0
    while not is_solved(board):
        stdscr.clear()
        for i in range(9):
            for j in range(9):
                char = str(board[i][j]) if board[i][j] != 0 else '.'
                if i == cursor_y and j == cursor_x:
                    stdscr.addstr(i, j * 2, char, curses.A_REVERSE)
                else:
                    stdscr.addstr(i, j * 2, char)
        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_UP and cursor_y > 0:
            cursor_y -= 1
        elif key == curses.KEY_DOWN and cursor_y < 8:
            cursor_y += 1
        elif key == curses.KEY_LEFT and cursor_x > 0:
            cursor_x -= 1
        elif key == curses.KEY_RIGHT and cursor_x < 8:
            cursor_x += 1
        elif ord('1') <= key <= ord('9'):
            num = key - ord('0')
            if is_valid_move(board, cursor_y, cursor_x, num):
                board[cursor_y][cursor_x] = num
        elif key == ord('q'):
            break
    if is_solved(board):
        stdscr.addstr(10, 0, "Congratulations! You solved the Sudoku.")
        stdscr.refresh()
        stdscr.getch()

def play():
    curses.wrapper(main())
