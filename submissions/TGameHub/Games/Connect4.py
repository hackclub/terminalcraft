import curses
import numpy as np

ROWS, COLS = 6, 7
EMPTY, PLAYER1, PLAYER2 = ' ', 'X', 'O'

class Connect4:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.board = np.full((ROWS, COLS), EMPTY)
        self.current_player = PLAYER1
        self.cursor_col = 0
        curses.curs_set(0)
        self.play_game()

    def draw_board(self):
        self.stdscr.clear()
        try:
            height, width = self.stdscr.getmaxyx()
            if height < ROWS + 3 or width < COLS * 4:
                raise ValueError("Window too small")
            for row in range(ROWS):
                for col in range(COLS):
                    self.stdscr.addstr(row + 1, col * 4, f'[{self.board[row, col]}]')
            self.stdscr.addstr(ROWS + 2, self.cursor_col * 4, ' ^ ')
        except ValueError as e:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, str(e))
            self.stdscr.addstr(1, 0, "Please resize the window and press any key to continue.")
        self.stdscr.refresh()

    def drop_piece(self, col):
        for row in range(ROWS - 1, -1, -1):
            if self.board[row, col] == EMPTY:
                self.board[row, col] = self.current_player
                return True
        return False

    def check_win(self, player):
        for row in range(ROWS):
            for col in range(COLS - 3):
                if all(self.board[row, col + i] == player for i in range(4)):
                    return True
        for row in range(ROWS - 3):
            for col in range(COLS):
                if all(self.board[row + i, col] == player for i in range(4)):
                    return True
        for row in range(ROWS - 3):
            for col in range(COLS - 3):
                if all(self.board[row + i, col + i] == player for i in range(4)):
                    return True
        for row in range(3, ROWS):
            for col in range(COLS - 3):
                if all(self.board[row - i, col + i] == player for i in range(4)):
                    return True
        return False

    def play_game(self):
        while True:
            self.draw_board()
            key = self.stdscr.getch()
            if key == curses.KEY_LEFT and self.cursor_col > 0:
                self.cursor_col -= 1
            elif key == curses.KEY_RIGHT and self.cursor_col < COLS - 1:
                self.cursor_col += 1
            elif key == ord(' '):
                if self.drop_piece(self.cursor_col):
                    if self.check_win(self.current_player):
                        self.draw_board()
                        self.stdscr.addstr(ROWS + 4, 0, f'{self.current_player} wins! Press any key to exit.')
                        self.stdscr.getch()
                        break
                    self.current_player = PLAYER1 if self.current_player == PLAYER2 else PLAYER2

def play():
    curses.wrapper(Connect4)