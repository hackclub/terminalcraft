import random
import os
from typing import List, Tuple, Set
import curses

class Minesweeper:
    def __init__(self):
        self.difficulty_levels = {
            'beginner': {'size': 9, 'mines': 10},
            'intermediate': {'size': 16, 'mines': 40},
            'expert': {'size': 22, 'mines': 99}
        }
        self.current_difficulty = 'beginner'
        self.board = []
        self.visible = []
        self.mines_locations = set()
        self.flags = set()
        self.game_over = False
        self.won = False
        self.first_move = True
        self.cursor_x = 0
        self.cursor_y = 0
        self.initialize_game()

    def initialize_game(self) -> None:
        size = self.difficulty_levels[self.current_difficulty]['size']
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        self.visible = [[False for _ in range(size)] for _ in range(size)]
        self.mines_locations = set()
        self.flags = set()
        self.game_over = False
        self.won = False
        self.first_move = True
        self.cursor_x = 0
        self.cursor_y = 0

    def place_mines(self, first_x: int, first_y: int) -> None:
        size = self.difficulty_levels[self.current_difficulty]['size']
        num_mines = self.difficulty_levels[self.current_difficulty]['mines']
        safe_zone = {(x, y) for x in range(max(0, first_x-1), min(size, first_x+2))
                           for y in range(max(0, first_y-1), min(size, first_y+2))}
        all_positions = {(x, y) for x in range(size) for y in range(size)} - safe_zone
        self.mines_locations = set(random.sample(list(all_positions), num_mines))
        for x, y in self.mines_locations:
            self.board[x][y] = -1
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    new_x, new_y = x + dx, y + dy
                    if (0 <= new_x < size and 0 <= new_y < size and 
                        self.board[new_x][new_y] != -1):
                        self.board[new_x][new_y] += 1

    def reveal(self, x: int, y: int) -> bool:
        size = self.difficulty_levels[self.current_difficulty]['size']
        if not (0 <= x < size and 0 <= y < size) or self.visible[x][y]:
            return True
        if self.first_move:
            self.place_mines(x, y)
            self.first_move = False
        self.visible[x][y] = True
        if self.board[x][y] == -1:
            self.game_over = True
            return False
        if self.board[x][y] == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    self.reveal(x + dx, y + dy)
        return True

    def toggle_flag(self, x: int, y: int) -> None:
        if not self.visible[x][y]:
            pos = (x, y)
            if pos in self.flags:
                self.flags.remove(pos)
            else:
                self.flags.add(pos)

    def check_win(self) -> bool:
        size = self.difficulty_levels[self.current_difficulty]['size']
        for x in range(size):
            for y in range(size):
                if self.board[x][y] != -1 and not self.visible[x][y]:
                    return False
        self.won = True
        return True

    def get_cell_display(self, x: int, y: int, is_cursor: bool) -> str:
        cell = ''
        if (x, y) in self.flags:
            cell = '🚩'
        elif not self.visible[x][y]:
            cell = '■'
        elif self.board[x][y] == -1:
            cell = '💣'
        elif self.board[x][y] == 0:
            cell = '·'
        else:
            cell = str(self.board[x][y])
        if is_cursor:
            return f'[{cell}]'
        return f' {cell} '

    def display_board(self, stdscr) -> None:
        stdscr.clear()
        size = self.difficulty_levels[self.current_difficulty]['size']
        stdscr.addstr(0, 0, "MINESWEEPER", curses.A_BOLD)
        stdscr.addstr(1, 0, f"Difficulty: {self.current_difficulty.capitalize()}")
        stdscr.addstr(3, 4, '  ' + ''.join(f'{i:3}' for i in range(size)))
        stdscr.addstr(4, 2, '  ┌' + '───' * size + '┐')
        for i in range(size):
            stdscr.addstr(i + 5, 0, f'{i:2}')
            stdscr.addstr(i + 5, 2, '│')
            for j in range(size):
                is_cursor = (i == self.cursor_y and j == self.cursor_x)
                cell = self.get_cell_display(i, j, is_cursor)
                screen_y = i + 5
                screen_x = j * 3 + 3
                if is_cursor:
                    stdscr.addstr(screen_y, screen_x, cell, curses.A_REVERSE)
                else:
                    stdscr.addstr(screen_y, screen_x, cell)
            stdscr.addstr(i + 5, size * 3 + 3, '│')
        stdscr.addstr(size + 5, 2, '  └' + '───' * size + '┘')
        status_y = size + 7
        mines_left = len(self.mines_locations) - len(self.flags)
        stdscr.addstr(status_y, 0, f"Mines remaining: {mines_left}")
        if self.game_over:
            stdscr.addstr(status_y + 1, 0, "Game Over! You hit a mine!")
        elif self.won:
            stdscr.addstr(status_y + 1, 0, "Congratulations! You won!")
        stdscr.addstr(status_y + 2, 0, "Controls: WASD to move, Space to reveal, F to flag, Q to quit")
        stdscr.refresh()

    def play(self, stdscr) -> None:
        curses.curs_set(0)
        stdscr.clear()
        size = self.difficulty_levels[self.current_difficulty]['size']
        while True:
            self.display_board(stdscr)
            if self.game_over or self.won:
                stdscr.getch()
                break
            try:
                key = stdscr.getch()
                if key in (ord('w'), ord('W')) and self.cursor_y > 0:
                    self.cursor_y -= 1
                elif key in (ord('s'), ord('S')) and self.cursor_y < size - 1:
                    self.cursor_y += 1
                elif key in (ord('a'), ord('A')) and self.cursor_x > 0:
                    self.cursor_x -= 1
                elif key in (ord('d'), ord('D')) and self.cursor_x < size - 1:
                    self.cursor_x += 1
                elif key == ord(' '):
                    if not self.reveal(self.cursor_y, self.cursor_x):
                        self.display_board(stdscr)
                        stdscr.getch()
                        break
                    self.check_win()
                elif key in (ord('f'), ord('F')):
                    self.toggle_flag(self.cursor_y, self.cursor_x)
                elif key in (ord('q'), ord('Q')):
                    break
            except curses.error:
                continue

def main(stdscr):
    while True:
        game = Minesweeper()
        curses.curs_set(1)
        stdscr.clear()
        stdscr.addstr(0, 0, "Select Difficulty:")
        stdscr.addstr(1, 0, "1. Beginner (9x9, 10 mines)")
        stdscr.addstr(2, 0, "2. Intermediate (16x16, 40 mines)")
        stdscr.addstr(3, 0, "3. Expert (22x22, 99 mines)")
        stdscr.addstr(4, 0, "Enter choice (1-3): ")
        stdscr.refresh()
        while True:
            try:
                choice = stdscr.getch()
                if choice in (ord('1'), ord('2'), ord('3')):
                    if choice == ord('1'):
                        game.current_difficulty = 'beginner'
                    elif choice == ord('2'):
                        game.current_difficulty = 'intermediate'
                    else:
                        game.current_difficulty = 'expert'
                    break
            except curses.error:
                continue
        game.initialize_game()
        game.play(stdscr)
        stdscr.clear()
        stdscr.addstr(0, 0, "Play again? (y/n): ")
        stdscr.refresh()
        while True:
            try:
                choice = stdscr.getch()
                if choice in (ord('y'), ord('Y'), ord('n'), ord('N')):
                    if choice in (ord('n'), ord('N')):
                        return
                    break
            except curses.error:
                continue

if __name__ == "__main__":
    curses.wrapper(main)
