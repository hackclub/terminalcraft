#!/usr/bin/env python3
import os
import time
import curses
import math
import random
BALL_CHARS = {
    'small': 'o',
    'medium': 'O',
    'large': '@'
}
TRAIL_CHARS = '.·'
class Ball:
    """A class representing a bouncing ball."""
    def __init__(self, x, y, x_vel, y_vel, size='medium', color=1):
        self.x = x
        self.y = y
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.size = size
        self.color = color
        self.gravity = 0.2
        self.elasticity = 0.8
        self.trail = []
        self.max_trail_length = 10
    def update(self, width, height):
        """Update the ball's position and velocity."""
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
        self.x += self.x_vel
        self.y += self.y_vel
        self.y_vel += self.gravity
        if self.x < 0:
            self.x = 0
            self.x_vel = -self.x_vel * self.elasticity
        elif self.x >= width:
            self.x = width - 1
            self.x_vel = -self.x_vel * self.elasticity
        if self.y < 0:
            self.y = 0
            self.y_vel = -self.y_vel * self.elasticity
        elif self.y >= height - 1:  
            self.y = height - 2  
            self.y_vel = -self.y_vel * self.elasticity
            if abs(self.y_vel) > 0.5:  
                self.x_vel += (random.random() - 0.5) * 0.5
        self.x_vel *= 0.99
        if abs(self.y_vel) < 0.3 and self.y >= height - 2:
            self.y_vel = -1.5  
    def draw(self, screen):
        """Draw the ball and its trail."""
        for i, (trail_x, trail_y) in enumerate(self.trail):
            if i < len(self.trail) - 2:
                try:
                    char_index = i % len(TRAIL_CHARS)
                    screen.addch(int(trail_y), int(trail_x), TRAIL_CHARS[char_index], 
                                curses.color_pair(self.color) | curses.A_DIM)
                except curses.error:
                    pass
        try:
            screen.addch(int(self.y), int(self.x), BALL_CHARS[self.size], 
                        curses.color_pair(self.color) | curses.A_BOLD)
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
def draw_floor(screen, width, height):
    """Draw a floor for the ball to bounce on."""
    floor_y = height - 1
    try:
        screen.addstr(floor_y, 0, "=" * width)
    except curses.error:
        pass
def draw_walls(screen, width, height):
    """Draw walls on the sides."""
    for y in range(height - 1):  
        try:
            screen.addch(y, 0, '|')
            screen.addch(y, width - 1, '|')
        except curses.error:
            pass
def main(screen):
    """Main function."""
    try:
        width, height = get_terminal_size()
        width = min(width, 80)  
        height = min(height, 24)  
        balls = [
            Ball(width // 4, height // 4, 1.0, 0.0, 'large', 1),
            Ball(width // 2, height // 3, -0.8, 0.5, 'medium', 2),
            Ball(3 * width // 4, height // 2, 0.5, -1.0, 'small', 3)
        ]
        frame_num = 0
        while True:
            key = screen.getch()
            if key == ord('q'):
                break
            elif key == ord(' '):  
                x = random.randint(5, width - 5)
                y = random.randint(5, height // 2)
                x_vel = random.uniform(-1.5, 1.5)
                y_vel = random.uniform(-1.0, 0.0)
                size = random.choice(['small', 'medium', 'large'])
                color = random.randint(1, 7)
                balls.append(Ball(x, y, x_vel, y_vel, size, color))
            screen.clear()
            draw_floor(screen, width, height)
            draw_walls(screen, width, height)
            for ball in balls:
                ball.update(width, height)
                ball.draw(screen)
            try:
                screen.addstr(0, 2, "Press 'q' to quit, SPACE to add ball")
            except curses.error:
                pass
            screen.refresh()
            frame_num += 1
            time.sleep(0.03)
    except KeyboardInterrupt:
        pass
if __name__ == "__main__":
    try:
        screen = initialize_screen()
        main(screen)
    finally:
        cleanup_screen(screen)
        print("Bouncing ball simulation ended.")