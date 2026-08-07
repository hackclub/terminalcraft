#!/usr/bin/env python3
import os
import time
import random
import curses
import string
def initialize_screen():
    """Initialize the curses screen."""
    screen = curses.initscr()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.curs_set(0)  
    curses.noecho()
    curses.cbreak()
    screen.keypad(True)
    screen.timeout(100)  
    return screen
def cleanup_screen(screen):
    """Clean up the curses screen."""
    screen.keypad(False)
    curses.nocbreak()
    curses.echo()
    curses.endwin()
class MatrixColumn:
    """A class representing a column in the Matrix effect."""
    def __init__(self, height, x_pos):
        self.x_pos = x_pos
        self.height = height
        self.speed = random.randint(1, 3)
        self.head_pos = random.randint(-height, 0)
        self.length = random.randint(5, 15)
        self.chars = []
        self.update_chars()
    def update_chars(self):
        """Update the characters in the column."""
        charset = string.ascii_letters + string.digits + '!@#$%^&*()'
        self.chars = [random.choice(charset) for _ in range(self.length)]
    def update(self):
        """Update the column position."""
        self.head_pos += self.speed
        for i in range(len(self.chars)):
            if random.random() < 0.1:  
                self.chars[i] = random.choice(string.ascii_letters + string.digits + '!@#$%^&*()')
        if self.head_pos - self.length > self.height:
            self.head_pos = random.randint(-self.length, 0)
            self.speed = random.randint(1, 3)
            self.length = random.randint(5, 15)
            self.update_chars()
def render_matrix(screen, columns):
    """Render the Matrix effect on the screen."""
    screen.clear()
    for column in columns:
        if 0 <= column.head_pos < column.height:
            screen.addstr(column.head_pos, column.x_pos, column.chars[0], 
                         curses.color_pair(1) | curses.A_BOLD)
        for i in range(1, column.length):
            pos = column.head_pos - i
            if 0 <= pos < column.height:
                if i < column.length // 3:
                    attr = curses.color_pair(1) | curses.A_BOLD
                elif i < column.length * 2 // 3:
                    attr = curses.color_pair(1)
                else:
                    attr = curses.color_pair(1) | curses.A_DIM
                screen.addstr(pos, column.x_pos, column.chars[i % len(column.chars)], attr)
    screen.refresh()
def main(screen):
    """Main function."""
    try:
        height, width = screen.getmaxyx()
        columns = []
        for x in range(0, width - 1, 2):  
            columns.append(MatrixColumn(height, x))
        while True:
            key = screen.getch()
            if key == ord('q'):
                break
            for column in columns:
                column.update()
            render_matrix(screen, columns)
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
if __name__ == "__main__":
    try:
        screen = initialize_screen()
        main(screen)
    finally:
        cleanup_screen(screen)
        print("Matrix simulation ended.")