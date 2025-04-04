#!/usr/bin/env python3

import curses
import os
import sys
import subprocess


def draw_phone(stdscr, selected, max_y, max_x):
    stdscr.clear()

    phone_width = 25
    phone_height = 20

    start_x = (max_x - phone_width) // 2
    start_y = (max_y - phone_height) // 2

    stdscr.addstr(start_y, start_x, "┌─────────────────────┐")
    stdscr.addstr(start_y + 1, start_x, "│                     │")
    stdscr.addstr(start_y + 2, start_x, "│   ┌─────────────┐   │")
    stdscr.addstr(start_y + 3, start_x, "│   │             │   │")
    stdscr.addstr(start_y + 4, start_x, "│   │  GAME MENU  │   │")
    stdscr.addstr(start_y + 5, start_x, "│   │             │   │")

    if selected == 0:
        stdscr.addstr(start_y + 6, start_x, "│   │ ▶ Snake      │   │")
    else:
        stdscr.addstr(start_y + 6, start_x, "│   │   Snake      │   │")

    if selected == 1:
        stdscr.addstr(start_y + 7, start_x, "│   │ ▶ Minesweeper│   │")
    else:
        stdscr.addstr(start_y + 7, start_x, "│   │   Minesweeper│   │")

    if selected == 2:
        stdscr.addstr(start_y + 8, start_x, "│   │ ▶ Exit       │   │")
    else:
        stdscr.addstr(start_y + 8, start_x, "│   │   Exit       │   │")

    stdscr.addstr(start_y + 9, start_x, "│   │             │   │")
    stdscr.addstr(start_y + 10, start_x, "│   └─────────────┘   │")
    stdscr.addstr(start_y + 11, start_x, "│                     │")
    stdscr.addstr(start_y + 12, start_x, "│    ┌───┐ ┌───┐     │")
    stdscr.addstr(start_y + 13, start_x, "│    │ ↑ │ │sel│     │")
    stdscr.addstr(start_y + 14, start_x, "│    └───┘ └───┘     │")
    stdscr.addstr(start_y + 15, start_x, "│ ┌───┐ ┌───┐ ┌───┐  │")
    stdscr.addstr(start_y + 16, start_x, "│ │ ← │ │ ↓ │ │ → │  │")
    stdscr.addstr(start_y + 17, start_x, "│ └───┘ └───┘ └───┘  │")
    stdscr.addstr(start_y + 18, start_x, "│                     │")
    stdscr.addstr(start_y + 19, start_x, "└─────────────────────┘")

    stdscr.addstr(start_y + 21, start_x, "  Use UP/DOWN to navigate")
    stdscr.addstr(start_y + 22, start_x, "  Press ENTER to select")

    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)

    selected = 0
    total_options = 3

    max_y, max_x = stdscr.getmaxyx()

    while True:
        draw_phone(stdscr, selected, max_y, max_x)

        key = stdscr.getch()

        if key == curses.KEY_UP and selected > 0:
            selected -= 1
        elif key == curses.KEY_DOWN and selected < total_options - 1:
            selected += 1
        elif key == 10:  # Enter key
            if selected == 0:  # Snake
                stdscr.clear()
                stdscr.addstr(max_y // 2, max_x // 2 - 10, "Loading Snake Game...")
                stdscr.refresh()
                curses.endwin()

                try:
                    subprocess.run([sys.executable, "snake.py"])
                except Exception as e:
                    stdscr = curses.initscr()
                    stdscr.clear()
                    stdscr.addstr(
                        max_y // 2, max_x // 2 - 15, f"Error loading game: {e}"
                    )
                    stdscr.refresh()
                    stdscr.getch()

            elif selected == 1:  # Minesweeper
                stdscr.clear()
                stdscr.addstr(
                    max_y // 2, max_x // 2 - 12, "Loading Minesweeper Game..."
                )
                stdscr.refresh()
                curses.endwin()

                try:
                    subprocess.run([sys.executable, "minesweeper.py"])
                except Exception as e:
                    stdscr = curses.initscr()
                    stdscr.clear()
                    stdscr.addstr(
                        max_y // 2, max_x // 2 - 15, f"Error loading game: {e}"
                    )
                    stdscr.refresh()
                    stdscr.getch()

            elif selected == 2:  # Exit
                stdscr.clear()
                stdscr.addstr(max_y // 2, max_x // 2 - 8, "Thanks for playing!")
                stdscr.addstr(
                    max_y // 2 + 1, max_x // 2 - 12, "Disconnecting in 3 seconds..."
                )
                stdscr.refresh()
                curses.napms(3000)
                return


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"An error occurred: {e}")
