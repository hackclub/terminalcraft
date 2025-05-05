#!/usr/bin/env python3

import curses
import random
import time


def main(stdscr):
    curses.curs_set(0)
    stdscr.timeout(100)
    stdscr.keypad(True)

    try:
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(10, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(11, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(12, curses.COLOR_BLACK, curses.COLOR_WHITE)
        use_colors = True
    except:
        use_colors = False

    max_y, max_x = stdscr.getmaxyx()

    rows = min(16, max_y - 6)
    cols = min(30, max_x - 6)
    mines = int((rows * cols) * 0.15)

    game_win = curses.newwin(rows + 2, cols * 2 + 2, 2, (max_x - (cols * 2 + 2)) // 2)
    game_win.keypad(True)

    stdscr.clear()
    welcome_msg = "MINESWEEPER - Press any key to start"
    stdscr.addstr(max_y // 2, (max_x - len(welcome_msg)) // 2, welcome_msg)
    stdscr.refresh()
    stdscr.getch()

    def init_board():
        board = [["?" for _ in range(cols)] for _ in range(rows)]
        mines_pos = []

        mine_count = 0
        while mine_count < mines:
            r, c = random.randint(0, rows - 1), random.randint(0, cols - 1)
            if (r, c) not in mines_pos:
                mines_pos.append((r, c))
                mine_count += 1

        return board, mines_pos

    def count_adjacent_mines(row, col, mines_pos):
        count = 0
        for r in range(max(0, row - 1), min(rows, row + 2)):
            for c in range(max(0, col - 1), min(cols, col + 2)):
                if (r, c) in mines_pos and (r, c) != (row, col):
                    count += 1
        return count

    def reveal_cells(board, row, col, mines_pos, revealed):
        if (row, col) in revealed:
            return

        revealed.add((row, col))

        if (row, col) in mines_pos:
            return

        adjacent = count_adjacent_mines(row, col, mines_pos)
        if adjacent == 0:
            board[row][col] = " "
            for r in range(max(0, row - 1), min(rows, row + 2)):
                for c in range(max(0, col - 1), min(cols, col + 2)):
                    if (r, c) != (row, col):
                        reveal_cells(board, r, c, mines_pos, revealed)
        else:
            board[row][col] = str(adjacent)

    game_over = False
    win = False
    start_time = time.time()

    while True:
        board, mines_pos = init_board()
        flags = set()
        revealed = set()
        cursor_row, cursor_col = 0, 0
        game_over = False
        win = False
        start_time = time.time()

        while not game_over and not win:
            game_win.clear()
            game_win.box()

            elapsed = int(time.time() - start_time)
            mines_left = mines - len(flags)
            info_msg = f"Time: {elapsed}s | Mines: {mines_left}"
            stdscr.addstr(0, (max_x - len(info_msg)) // 2, info_msg)
            stdscr.refresh()

            for r in range(rows):
                for c in range(cols):
                    cell_char = board[r][c]
                    attr = curses.color_pair(1)

                    if cell_char.isdigit():
                        attr = curses.color_pair(int(cell_char) + 1)
                    elif cell_char == "F":
                        attr = curses.color_pair(11)
                        cell_char = "F"
                    elif cell_char == "X":
                        attr = curses.color_pair(10)

                    if r == cursor_row and c == cursor_col:
                        if use_colors:
                            attr = curses.color_pair(12)
                        else:
                            attr = curses.A_REVERSE

                    game_win.addstr(
                        r + 1, c * 2 + 1, cell_char + " ", attr if use_colors else 0
                    )

            game_win.refresh()

            key = stdscr.getch()

            if key == ord("q"):
                return

            if key == ord("p"):
                game_win.addstr(rows // 2, cols - 10, "PAUSED - Press 'p' to resume")
                game_win.refresh()

                stdscr.timeout(-1)
                while True:
                    ch = stdscr.getch()
                    if ch == ord("p"):
                        break
                    elif ch == ord("q"):
                        return

                stdscr.timeout(100)
                continue

            if game_over or win:
                if key == ord("r"):
                    break
                elif key == ord("q"):
                    return
                continue

            if key == curses.KEY_UP and cursor_row > 0:
                cursor_row -= 1
            elif key == curses.KEY_DOWN and cursor_row < rows - 1:
                cursor_row += 1
            elif key == curses.KEY_LEFT and cursor_col > 0:
                cursor_col -= 1
            elif key == curses.KEY_RIGHT and cursor_col < cols - 1:
                cursor_col += 1
            elif key == ord("f") or key == curses.KEY_DC:
                if (cursor_row, cursor_col) not in revealed:
                    if (cursor_row, cursor_col) in flags:
                        flags.remove((cursor_row, cursor_col))
                        board[cursor_row][cursor_col] = "?"
                    else:
                        flags.add((cursor_row, cursor_col))
                        board[cursor_row][cursor_col] = "F"
            elif key == ord(" ") or key == 10:
                if (cursor_row, cursor_col) not in flags:
                    if (cursor_row, cursor_col) in mines_pos:
                        game_over = True

                        for r, c in mines_pos:
                            if (r, c) not in flags:
                                board[r][c] = "X"

                        for r, c in flags:
                            if (r, c) not in mines_pos:
                                board[r][c] = "!"
                    else:
                        reveal_cells(board, cursor_row, cursor_col, mines_pos, revealed)

            if len(revealed) == (rows * cols) - len(mines_pos):
                win = True

                for r, c in mines_pos:
                    if (r, c) not in flags:
                        board[r][c] = "F"

            if game_over:
                msg = "GAME OVER! You hit a mine!"
                stdscr.addstr(
                    max_y - 2,
                    (max_x - len(msg)) // 2,
                    msg,
                    curses.color_pair(4) if use_colors else 0,
                )
                stdscr.addstr(max_y - 1, (max_x - 20) // 2, "Press 'r' to restart")
                stdscr.refresh()

            if win:
                elapsed = int(time.time() - start_time)
                msg = f"YOU WIN! Time: {elapsed}s"
                stdscr.addstr(
                    max_y - 2,
                    (max_x - len(msg)) // 2,
                    msg,
                    curses.color_pair(3) if use_colors else 0,
                )
                stdscr.addstr(max_y - 1, (max_x - 20) // 2, "Press 'r' to restart")
                stdscr.refresh()

        stdscr.timeout(-1)
        while True:
            key = stdscr.getch()
            if key == ord("r"):
                stdscr.timeout(100)
                break
            elif key == ord("q"):
                return


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"An error occurred: {e}")
        try:
            import os

            os.system("clear")
            print("Curses initialization failed. Falling back to simple version.")
            print("Press Enter to continue...")
            input()
            import sys

            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from simple_minesweeper import main as simple_main

            simple_main()
        except Exception as e2:
            print(f"Simple version also failed: {e2}")
