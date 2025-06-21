#!/usr/bin/env python3
import os
import time
import curses
import random
class Raindrop:
    """A class representing a raindrop."""
    def __init__(self, x, y, speed, length, color=4):
        self.x = x
        self.y = y
        self.speed = speed
        self.length = length
        self.color = color
        self.char = '|'
        self.trail_chars = ['.']
        self.splash_active = False
        self.splash_frame = 0
        self.splash_frames = ['_', '-', '.', ' ']
    def update(self, height):
        """Update the raindrop's position."""
        self.y += self.speed
        if self.y >= height - 2 and not self.splash_active:
            self.splash_active = True
            self.splash_frame = 0
        if self.splash_active:
            self.splash_frame += 1
            if self.splash_frame >= len(self.splash_frames) * 2:  
                self.y = random.randint(-20, -1)
                self.x = random.randint(0, 79)
                self.speed = random.uniform(0.5, 2.0)
                self.length = random.randint(3, 8)
                self.splash_active = False
                self.splash_frame = 0
    def draw(self, screen, height):
        """Draw the raindrop on the screen."""
        if self.splash_active:
            splash_char = self.splash_frames[(self.splash_frame // 2) % len(self.splash_frames)]
            try:
                screen.addch(height - 2, int(self.x), splash_char, 
                           curses.color_pair(self.color) | curses.A_BOLD)
                if self.length > 5 and int(self.x) > 0:
                    screen.addch(height - 2, int(self.x) - 1, splash_char, 
                               curses.color_pair(self.color) | curses.A_DIM)
                if self.length > 5 and int(self.x) < 79:
                    screen.addch(height - 2, int(self.x) + 1, splash_char, 
                               curses.color_pair(self.color) | curses.A_DIM)
            except curses.error:
                pass
        else:
            for i in range(self.length):
                trail_y = int(self.y) - i
                if 0 <= trail_y < height - 1:  
                    try:
                        if i == 0:
                            screen.addch(trail_y, int(self.x), self.char, 
                                       curses.color_pair(self.color) | curses.A_BOLD)
                        else:
                            trail_char = self.trail_chars[0]
                            screen.addch(trail_y, int(self.x), trail_char, 
                                       curses.color_pair(self.color) | curses.A_DIM)
                    except curses.error:
                        pass
def initialize_screen():
    """Initialize the curses screen."""
    screen = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)   
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)   
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)  
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
def draw_ground(screen, width, height):
    """Draw the ground at the bottom of the screen."""
    try:
        screen.addstr(height - 1, 0, "_" * width, curses.color_pair(1))
    except curses.error:
        pass
def draw_clouds(screen, width, frame_num):
    """Draw clouds at the top of the screen."""
    cloud_chars = [' ', '.', ':', '=', '#']
    cloud_pattern = []
    for x in range(width):
        wave = (x + frame_num // 5) % width
        distance = abs(wave - x) / width
        density = 0.7 + 0.3 * (1 - distance)
        density += random.random() * 0.2
        char_index = min(int(density * len(cloud_chars)), len(cloud_chars) - 1)
        cloud_pattern.append(cloud_chars[char_index])
    try:
        screen.addstr(0, 0, ''.join(cloud_pattern), curses.color_pair(1) | curses.A_DIM)
    except curses.error:
        pass
def main(screen):
    """Main function."""
    try:
        width, height = get_terminal_size()
        width = min(width, 80)  
        height = min(height, 24)  
        raindrops = []
        for _ in range(100):
            x = random.randint(0, width - 1)
            y = random.randint(-20, height - 3)  
            speed = random.uniform(0.5, 2.0)
            length = random.randint(3, 8)
            color = random.randint(1, 4)
            raindrops.append(Raindrop(x, y, speed, length, color))
        frame_num = 0
        rain_intensity = 100  
        while True:
            key = screen.getch()
            if key == ord('q'):
                break
            elif key == ord('+') or key == ord('='):
                rain_intensity = min(200, rain_intensity + 10)
                while len(raindrops) < rain_intensity:
                    x = random.randint(0, width - 1)
                    y = random.randint(-20, 0)  
                    speed = random.uniform(0.5, 2.0)
                    length = random.randint(3, 8)
                    color = random.randint(1, 4)
                    raindrops.append(Raindrop(x, y, speed, length, color))
            elif key == ord('-'):
                rain_intensity = max(10, rain_intensity - 10)
                while len(raindrops) > rain_intensity:
                    raindrops.pop()
            screen.clear()
            draw_clouds(screen, width, frame_num)
            draw_ground(screen, width, height)
            for raindrop in raindrops:
                raindrop.update(height)
                raindrop.draw(screen, height)
            try:
                screen.addstr(height-1, 0, f"Raindrops: {len(raindrops)} - Press '+'/'-' to adjust, 'q' to quit")
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
        print("Rain simulation ended.")