#!/usr/bin/env python3
import os
import time
import curses
import random
from collections import deque
class SnakeGame:
    """A class representing the snake game."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.score = 0
        self.game_over = False
        self.win = False
        self.snake = deque([(width // 2, height // 2)])
        self.direction = 1
        self.food = self.create_food()
        self.speed = 0.1
        self.max_score = 20
    def create_food(self):
        """Create a new food at a random position."""
        while True:
            food = (random.randint(1, self.width - 2), random.randint(1, self.height - 2))
            if food not in self.snake:
                return food
    def change_direction(self, key):
        """Change the snake's direction based on key press."""
        if key == curses.KEY_UP and self.direction != 2:
            self.direction = 0
        elif key == curses.KEY_RIGHT and self.direction != 3:
            self.direction = 1
        elif key == curses.KEY_DOWN and self.direction != 0:
            self.direction = 2
        elif key == curses.KEY_LEFT and self.direction != 1:
            self.direction = 3
    def move_snake(self):
        """Move the snake in the current direction."""
        head_x, head_y = self.snake[0]
        if self.direction == 0:  
            new_head = (head_x, head_y - 1)
        elif self.direction == 1:  
            new_head = (head_x + 1, head_y)
        elif self.direction == 2:  
            new_head = (head_x, head_y + 1)
        elif self.direction == 3:  
            new_head = (head_x - 1, head_y)
        if (new_head[0] <= 0 or new_head[0] >= self.width - 1 or
            new_head[1] <= 0 or new_head[1] >= self.height - 1):
            self.game_over = True
            return
        if new_head in list(self.snake)[:-1]:
            self.game_over = True
            return
        self.snake.appendleft(new_head)
        if new_head == self.food:
            self.score += 1
            if self.score >= self.max_score:
                self.win = True
                return
            self.food = self.create_food()
            self.speed = max(0.05, self.speed * 0.95)
        else:
            self.snake.pop()
    def draw(self, screen):
        """Draw the game on the screen."""
        screen.clear()
        for x in range(self.width):
            try:
                screen.addch(0, x, '#')
                screen.addch(self.height - 1, x, '#')
            except curses.error:
                pass
        for y in range(self.height):
            try:
                screen.addch(y, 0, '#')
                screen.addch(y, self.width - 1, '#')
            except curses.error:
                pass
        for i, (x, y) in enumerate(self.snake):
            try:
                if i == 0:  
                    screen.addch(y, x, '@', curses.color_pair(1) | curses.A_BOLD)
                else:  
                    screen.addch(y, x, 'O', curses.color_pair(2))
            except curses.error:
                pass
        try:
            screen.addch(self.food[1], self.food[0], '*', curses.color_pair(3) | curses.A_BOLD)
        except curses.error:
            pass
        score_text = f" Score: {self.score} "
        try:
            screen.addstr(0, self.width // 2 - len(score_text) // 2, score_text)
        except curses.error:
            pass
        if self.game_over:
            game_over_text = " GAME OVER - Press 'r' to restart or 'q' to quit "
            try:
                screen.addstr(self.height // 2, self.width // 2 - len(game_over_text) // 2, 
                             game_over_text, curses.color_pair(4) | curses.A_BOLD)
            except curses.error:
                pass
        elif self.win:
            win_text = " YOU WIN! - Press 'r' to restart or 'q' to quit "
            try:
                screen.addstr(self.height // 2, self.width // 2 - len(win_text) // 2, 
                             win_text, curses.color_pair(3) | curses.A_BOLD)
            except curses.error:
                pass
        screen.refresh()
def initialize_screen():
    """Initialize the curses screen."""
    screen = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)   
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) 
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)    
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
        game = SnakeGame(width, height)
        last_update = time.time()
        while True:
            key = screen.getch()
            if key == ord('q'):
                break
            elif key == ord('r'):
                game = SnakeGame(width, height)
                last_update = time.time()
            elif key in [curses.KEY_UP, curses.KEY_RIGHT, curses.KEY_DOWN, curses.KEY_LEFT]:
                game.change_direction(key)
            current_time = time.time()
            if current_time - last_update > game.speed and not game.game_over and not game.win:
                game.move_snake()
                last_update = current_time
            game.draw(screen)
            time.sleep(0.03)
    except KeyboardInterrupt:
        pass
if __name__ == "__main__":
    try:
        screen = initialize_screen()
        main(screen)
    finally:
        cleanup_screen(screen)
        print("Snake game ended.")