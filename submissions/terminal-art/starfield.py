#!/usr/bin/env python3
import os
import time
import curses
import random
import math
class Star:
    """A class representing a star in the starfield."""
    def __init__(self, x, y, z, color=7):
        self.x = x  
        self.y = y  
        self.z = z  
        self.prev_x = x
        self.prev_y = y
        self.prev_z = z
        self.color = color
    def update(self, speed):
        """Update the star's position."""
        self.prev_x = self.x
        self.prev_y = self.y
        self.prev_z = self.z
        self.z -= speed
        if self.z <= 0:
            self.x = random.uniform(-1.0, 1.0)
            self.y = random.uniform(-1.0, 1.0)
            self.z = 1.0
    def draw(self, screen, width, height):
        """Draw the star on the screen."""
        if self.z > 0:
            screen_x = int((self.x / self.z) * width / 2 + width / 2)
            screen_y = int((self.y / self.z) * height / 2 + height / 2)
            if 0 <= screen_x < width and 0 <= screen_y < height:
                brightness = 1.0 - self.z
                if brightness > 0.8:
                    char = '@'
                    attr = curses.A_BOLD
                elif brightness > 0.5:
                    char = '*'
                    attr = curses.A_BOLD
                elif brightness > 0.3:
                    char = '+'
                    attr = curses.A_NORMAL
                else:
                    char = '.'
                    attr = curses.A_DIM
                try:
                    screen.addch(screen_y, screen_x, char, 
                                curses.color_pair(self.color) | attr)
                except curses.error:
                    pass
                if self.prev_z > 0 and brightness > 0.5:
                    prev_x = int((self.prev_x / self.prev_z) * width / 2 + width / 2)
                    prev_y = int((self.prev_y / self.prev_z) * height / 2 + height / 2)
                    if (0 <= prev_x < width and 0 <= prev_y < height and
                        (prev_x != screen_x or prev_y != screen_y)):
                        try:
                            screen.addch(prev_y, prev_x, '.', 
                                        curses.color_pair(self.color) | curses.A_DIM)
                        except curses.error:
                            pass
def initialize_screen():
    """Initialize the curses screen."""
    screen = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    colors = [curses.COLOR_RED, curses.COLOR_GREEN, curses.COLOR_YELLOW, 
              curses.COLOR_BLUE, curses.COLOR_MAGENTA, curses.COLOR_CYAN, 
              curses.COLOR_WHITE]
    for i, color in enumerate(colors, start=1):
        curses.init_pair(i, color, curses.COLOR_BLACK)
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
def get_terminal_size():
    """Get the terminal size."""
    return os.get_terminal_size()
def main(screen):
    """Main function."""
    try:
        width, height = get_terminal_size()
        width = min(width, 80)  
        height = min(height, 24)  
        stars = []
        for _ in range(100):
            x = random.uniform(-1.0, 1.0)
            y = random.uniform(-1.0, 1.0)
            z = random.uniform(0.0, 1.0)
            color = random.randint(1, 7)
            stars.append(Star(x, y, z, color))
        speed = 0.01
        while True:
            key = screen.getch()
            if key == ord('q'):
                break
            elif key == ord('+') or key == ord('='):
                speed = min(0.05, speed + 0.005)  
            elif key == ord('-'):
                speed = max(0.001, speed - 0.005)  
            screen.clear()
            for star in stars:
                star.update(speed)
                star.draw(screen, width, height)
            try:
                screen.addstr(0, 0, f"Speed: {speed:.3f} - Press '+'/'-' to adjust, 'q' to quit")
            except curses.error:
                pass
            screen.refresh()
            time.sleep(0.03)
    except KeyboardInterrupt:
        pass
if __name__ == "__main__":
    try:
        screen = initialize_screen()
        main(screen)
    finally:
        cleanup_screen(screen)
        print("Starfield simulation ended.")