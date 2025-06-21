#!/usr/bin/env python3
import os
import time
import curses
import math
DANCING_MAN_FRAMES = [
    [
        "    o    ",
        "   /|\   ",
        "   / \   ",
        "  /   \  "
    ],
    [
        "   \o/   ",
        "    |    ",
        "    |    ",
        "   / \   "
    ],
    [
        "    o/   ",
        "   /|    ",
        "   / \   ",
        "  /   \  "
    ],
    [
        "   \o    ",
        "    |\   ",
        "   / \   ",
        "  /   \  "
    ],
    [
        "    o    ",
        "   /|\   ",
        "    |    ",
        "   / \   "
    ],
    [
        "    o    ",
        "   /|\   ",
        "  /   \  ",
        " /     \ "
    ],
    [
        "    o    ",
        "    |\   ",
        "    |    ",
        "   / \   "
    ],
    [
        "    o    ",
        "   /|    ",
        "    |    ",
        "   / \   "
    ]
]
def initialize_screen():
    """Initialize the curses screen."""
    screen = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
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
def draw_dancing_man(screen, x, y, frame_index):
    """Draw the dancing man at the specified position with the given frame."""
    frame = DANCING_MAN_FRAMES[frame_index % len(DANCING_MAN_FRAMES)]
    for i, line in enumerate(frame):
        try:
            screen.addstr(y + i, x, line, curses.color_pair(1) | curses.A_BOLD)
        except curses.error:
            pass
def draw_floor(screen, width, height):
    """Draw a floor for the dancing man."""
    floor_y = height - 2
    try:
        screen.addstr(floor_y, 0, "_" * width)
    except curses.error:
        pass
def draw_disco_lights(screen, width, height, frame_num):
    """Draw disco lights at the top of the screen."""
    colors = [curses.COLOR_RED, curses.COLOR_GREEN, curses.COLOR_YELLOW, 
              curses.COLOR_BLUE, curses.COLOR_MAGENTA, curses.COLOR_CYAN]
    for i, color in enumerate(colors, start=2):
        curses.init_pair(i, color, curses.COLOR_BLACK)
    for x in range(0, width, 4):
        color_index = ((x + frame_num) % len(colors)) + 2
        try:
            screen.addstr(0, x, "*", curses.color_pair(color_index) | curses.A_BOLD)
        except curses.error:
            pass
def main(screen):
    """Main function."""
    try:
        frame_num = 0
        dance_speed = 3  
        while True:
            key = screen.getch()
            if key == ord('q'):
                break
            elif key == ord('+') or key == ord('='):
                dance_speed = max(1, dance_speed - 1)  
            elif key == ord('-'):
                dance_speed = min(10, dance_speed + 1)  
            screen.clear()
            width, height = get_terminal_size()
            width = min(width, 80)  
            height = min(height, 24)  
            man_x = width // 2 - 5 + int(math.sin(frame_num / 10) * 10)
            man_y = height - 8
            draw_disco_lights(screen, width, height, frame_num)
            draw_floor(screen, width, height)
            dance_frame = (frame_num // dance_speed) % len(DANCING_MAN_FRAMES)
            draw_dancing_man(screen, man_x, man_y, dance_frame)
            try:
                screen.addstr(height-1, 0, "Press 'q' to quit, '+'/'-' to adjust speed")
            except curses.error:
                pass
            screen.refresh()
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
        print("Dancing man simulation ended.")