#!/usr/bin/env python3
import os
import time
import random
import curses
def initialize_screen():
    """Initialize the curses screen."""
    screen = curses.initscr()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)   
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)     
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK) 
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
class FireSimulation:
    """A class for simulating fire in the terminal."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.buffer = [[0 for _ in range(width)] for _ in range(height)]
        for x in range(width):
            self.buffer[height-1][x] = random.randint(80, 100)
    def update(self):
        """Update the fire simulation."""
        for x in range(self.width):
            self.buffer[self.height-1][x] = random.randint(80, 100)
        for y in range(self.height-2, -1, -1):
            for x in range(self.width):
                decay = random.randint(1, 4)
                below = self.buffer[y+1][x]
                below_left = self.buffer[y+1][(x-1) % self.width]
                below_right = self.buffer[y+1][(x+1) % self.width]
                new_value = (below + below_left + below_right) // 3 - decay
                self.buffer[y][x] = max(0, new_value)  
    def render(self, screen):
        """Render the fire simulation on the screen."""
        for y in range(self.height):
            for x in range(self.width):
                value = self.buffer[y][x]
                if value > 80:  
                    char = '@'
                    color_pair = 1
                elif value > 60:  
                    char = '#'
                    color_pair = 2
                elif value > 40:  
                    char = '+'  
                    color_pair = 3
                elif value > 20:  
                    char = '.'
                    color_pair = 4
                else:  
                    char = ' '
                    color_pair = 0
                try:
                    screen.addch(y, x, char, curses.color_pair(color_pair))
                except curses.error:
                    pass
        screen.refresh()
def main(screen):
    """Main function."""
    try:
        height, width = screen.getmaxyx()
        fire = FireSimulation(width, height)
        while True:
            key = screen.getch()
            if key == ord('q'):
                break
            fire.update()
            fire.render(screen)
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
if __name__ == "__main__":
    try:
        screen = initialize_screen()
        main(screen)
    finally:
        cleanup_screen(screen)
        print("Fire simulation ended.")