#!/usr/bin/env python3
import os
import time
import sys
import random
import curses
def initialize_screen():
    """Initialize the curses screen."""
    screen = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
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
def generate_frame(width, height, frame_num):
    """Generate an ASCII art frame."""
    ascii_chars = ' .:-=+*#%@'
    frame = []
    for y in range(height):
        line = []
        for x in range(width):
            wave = (x + frame_num) % width
            distance = abs(wave - x) / width
            noise = random.random() * 0.3
            intensity = (0.5 + 0.5 * (1 - distance)) + noise
            char_index = min(int(intensity * len(ascii_chars)), len(ascii_chars) - 1)
            line.append(ascii_chars[char_index])
        frame.append(''.join(line))
    return frame
def display_frame(screen, frame):
    """Display a frame on the screen."""
    for y, line in enumerate(frame):
        try:
            screen.addstr(y, 0, line)
        except curses.error:
            pass
    screen.refresh()
def main(screen):
    """Main function."""
    try:
        frame_num = 0
        while True:
            key = screen.getch()
            if key == ord('q'):
                break
            width, height = get_terminal_size()
            width = min(width, 80)  
            height = min(height, 24)  
            frame = generate_frame(width, height, frame_num)
            display_frame(screen, frame)
            frame_num += 1
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
if __name__ == "__main__":
    try:
        screen = initialize_screen()
        main(screen)
    finally:
        cleanup_screen(screen)
        print("Video simulation ended.")