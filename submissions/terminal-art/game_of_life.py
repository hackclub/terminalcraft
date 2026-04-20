#!/usr/bin/env python3
import curses
import random
import time
import os
class GameOfLife:
    """Conway's Game of Life simulation in the terminal."""
    def __init__(self, height, width, density=0.3):
        self.height = height
        self.width = width
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.next_grid = [[0 for _ in range(width)] for _ in range(height)]
        self.density = density
        self.generation = 0
        self.population = 0
    def randomize(self):
        """Initialize the grid with random cells."""
        self.grid = [[1 if random.random() < self.density else 0 
                     for _ in range(self.width)] 
                     for _ in range(self.height)]
        self.count_population()
    def count_population(self):
        """Count the current population of live cells."""
        self.population = sum(sum(row) for row in self.grid)
    def get_neighbors(self, row, col):
        """Count the number of live neighbors for a cell."""
        count = 0
        for i in range(max(0, row-1), min(self.height, row+2)):
            for j in range(max(0, col-1), min(self.width, col+2)):
                if (i, j) != (row, col) and self.grid[i][j] == 1:
                    count += 1
        return count
    def update(self):
        """Update the grid based on Conway's Game of Life rules."""
        for i in range(self.height):
            for j in range(self.width):
                neighbors = self.get_neighbors(i, j)
                if self.grid[i][j] == 1:  
                    if neighbors < 2 or neighbors > 3:
                        self.next_grid[i][j] = 0  
                    else:
                        self.next_grid[i][j] = 1  
                else:  
                    if neighbors == 3:
                        self.next_grid[i][j] = 1  
                    else:
                        self.next_grid[i][j] = 0  
        self.grid, self.next_grid = self.next_grid, self.grid
        self.generation += 1
        self.count_population()
    def draw(self, screen):
        """Draw the current state of the grid on the screen."""
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] == 1:
                    try:
                        screen.addch(i, j, '■', curses.A_BOLD | curses.color_pair(2))
                    except curses.error:
                        pass
                else:
                    try:
                        screen.addch(i, j, ' ')
                    except curses.error:
                        pass
def initialize_screen():
    """Initialize the curses screen."""
    screen = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  
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
def draw_info(screen, game, height, width, speed):
    """Draw information about the simulation."""
    info_text = [
        f"Conway's Game of Life | Gen: {game.generation} | Pop: {game.population}",
        "Controls: r=randomize, c=clear, +/-=speed, q=quit"
    ]
    for i, text in enumerate(info_text):
        try:
            screen.addstr(height - len(info_text) + i, 0, text.ljust(width), 
                         curses.color_pair(3) | curses.A_BOLD)
        except curses.error:
            pass
def main(screen):
    """Main function."""
    try:
        width, height = get_terminal_size()
        height = min(height, 40)  
        width = min(width, 80)    
        game_height = height - 2  
        game = GameOfLife(game_height, width)
        game.randomize()
        speed = 0.1  
        running = True
        paused = False
        while running:
            screen.clear()
            game.draw(screen)
            draw_info(screen, game, height, width, speed)
            screen.refresh()
            key = screen.getch()
            if key == ord('q'):
                running = False
            elif key == ord('r'):
                game.randomize()
            elif key == ord('c'):
                game.grid = [[0 for _ in range(width)] for _ in range(game_height)]
                game.count_population()
            elif key == ord('+') or key == ord('='):
                speed = max(0.01, speed - 0.05)  
            elif key == ord('-'):
                speed = min(1.0, speed + 0.05)   
            elif key == ord(' '):
                paused = not paused
            elif key == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, _ = curses.getmouse()
                    if my < game_height and mx < width:
                        game.grid[my][mx] = 1 - game.grid[my][mx]
                        game.count_population()
                except:
                    pass
            if not paused:
                game.update()
            time.sleep(speed)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup_screen(screen)
if __name__ == "__main__":
    try:
        curses.mousemask(curses.ALL_MOUSE_EVENTS)
    except:
        pass
    curses.wrapper(main)