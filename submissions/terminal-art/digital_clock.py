#!/usr/bin/env python3
import curses
import time
import os
import random
from datetime import datetime
DIGITS = {
    '0': [
        " ##### ",
        "#     #",
        "#     #",
        "#     #",
        "#     #",
        "#     #",
        " ##### "
    ],
    '1': [
        "   #   ",
        "  ##   ",
        " # #   ",
        "   #   ",
        "   #   ",
        "   #   ",
        "#######"
    ],
    '2': [
        " ##### ",
        "#     #",
        "      #",
        " ##### ",
        "#      ",
        "#      ",
        "#######"
    ],
    '3': [
        " ##### ",
        "#     #",
        "      #",
        " ##### ",
        "      #",
        "#     #",
        " ##### "
    ],
    '4': [
        "#     #",
        "#     #",
        "#     #",
        "#######",
        "      #",
        "      #",
        "      #"
    ],
    '5': [
        "#######",
        "#      ",
        "#      ",
        "###### ",
        "      #",
        "#     #",
        " ##### "
    ],
    '6': [
        " ##### ",
        "#     #",
        "#      ",
        "###### ",
        "#     #",
        "#     #",
        " ##### "
    ],
    '7': [
        "#######",
        "      #",
        "     # ",
        "    #  ",
        "   #   ",
        "  #    ",
        " #     "
    ],
    '8': [
        " ##### ",
        "#     #",
        "#     #",
        " ##### ",
        "#     #",
        "#     #",
        " ##### "
    ],
    '9': [
        " ##### ",
        "#     #",
        "#     #",
        " ######",
        "      #",
        "#     #",
        " ##### "
    ],
    ':': [
        "       ",
        "   #   ",
        "   #   ",
        "       ",
        "   #   ",
        "   #   ",
        "       "
    ],
    'A': [
        " ##### ",
        "#     #",
        "#     #",
        "#######",
        "#     #",
        "#     #",
        "#     #"
    ],
    'P': [
        "###### ",
        "#     #",
        "#     #",
        "###### ",
        "#      ",
        "#      ",
        "#      "
    ],
    'M': [
        "#     #",
        "##   ##",
        "# # # #",
        "#  #  #",
        "#     #",
        "#     #",
        "#     #"
    ]
}
COLOR_SCHEMES = [
    (curses.COLOR_RED, curses.COLOR_BLACK),
    (curses.COLOR_GREEN, curses.COLOR_BLACK),
    (curses.COLOR_YELLOW, curses.COLOR_BLACK),
    (curses.COLOR_BLUE, curses.COLOR_BLACK),
    (curses.COLOR_MAGENTA, curses.COLOR_BLACK),
    (curses.COLOR_CYAN, curses.COLOR_BLACK),
    (curses.COLOR_WHITE, curses.COLOR_BLACK),
]
class DigitalClock:
    """A digital clock display using ASCII art."""
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.digit_width = 7
        self.digit_height = 7
        self.color_scheme = 0
        self.show_seconds = True
        self.show_date = False
        self.show_am_pm = True
        self.use_24h = False
        self.rainbow_mode = False
        self.animation_mode = 0  
        self.animation_frame = 0
    def get_time_string(self):
        """Get the current time as a string."""
        now = datetime.now()
        if self.use_24h:
            if self.show_seconds:
                return now.strftime("%H:%M:%S")
            else:
                return now.strftime("%H:%M")
        else:
            if self.show_seconds:
                return now.strftime("%I:%M:%S")
            else:
                return now.strftime("%I:%M")
    def get_ampm_string(self):
        """Get AM/PM indicator."""
        return datetime.now().strftime("%p")
    def get_date_string(self):
        """Get the current date as a string."""
        return datetime.now().strftime("%Y-%m-%d")
    def draw_digit(self, screen, digit, x, y, color_pair):
        """Draw a single digit at the specified position."""
        if digit not in DIGITS:
            return
        digit_art = DIGITS[digit]
        for i, line in enumerate(digit_art):
            for j, char in enumerate(line):
                attr = curses.A_NORMAL
                if self.animation_mode == 1:  
                    if self.animation_frame % 10 < 5:
                        attr = curses.A_BOLD
                elif self.animation_mode == 2:  
                    wave_pos = (self.animation_frame + j) % 14
                    if wave_pos < 7:
                        attr = curses.A_BOLD
                if char != ' ':
                    try:
                        if self.rainbow_mode:
                            rainbow_color = (color_pair + j + i) % 7 + 1
                            screen.addch(y + i, x + j, '#', 
                                       curses.color_pair(rainbow_color) | attr)
                        else:
                            screen.addch(y + i, x + j, '#', 
                                       curses.color_pair(color_pair) | attr)
                    except curses.error:
                        pass
    def draw_clock(self, screen):
        """Draw the digital clock on the screen."""
        time_str = self.get_time_string()
        total_width = len(time_str) * (self.digit_width + 1) - 1
        start_x = (self.width - total_width) // 2
        start_y = (self.height - self.digit_height) // 2
        x = start_x
        for digit in time_str:
            color_pair = (self.color_scheme % 7) + 1
            self.draw_digit(screen, digit, x, start_y, color_pair)
            x += self.digit_width + 1
        if self.show_am_pm and not self.use_24h:
            ampm = self.get_ampm_string()
            ampm_x = start_x + total_width + 2
            ampm_y = start_y + 2
            for i, char in enumerate(ampm):
                self.draw_digit(screen, char, ampm_x, ampm_y + i*8, 
                              (self.color_scheme % 7) + 1)
        if self.show_date:
            date_str = self.get_date_string()
            date_y = start_y + self.digit_height + 2
            date_x = (self.width - len(date_str)) // 2
            try:
                screen.addstr(date_y, date_x, date_str, 
                            curses.color_pair((self.color_scheme % 7) + 1) | 
                            curses.A_BOLD)
            except curses.error:
                pass
        self.animation_frame += 1
def initialize_screen():
    """Initialize the curses screen."""
    screen = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    for i, (fg, bg) in enumerate(COLOR_SCHEMES, start=1):
        curses.init_pair(i, fg, bg)
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
def draw_stars(screen, height, width, num_stars=30):
    """Draw random stars in the background."""
    for _ in range(num_stars):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        char = random.choice(['*', '.', '+'])
        color = random.randint(1, 7)
        try:
            screen.addch(y, x, char, curses.color_pair(color) | curses.A_DIM)
        except curses.error:
            pass
def draw_info(screen, height, width, clock):
    """Draw information about controls."""
    info_text = [
        "Controls: c=color, s=seconds, d=date, a=AM/PM, h=24h, r=rainbow, m=animation, q=quit"
    ]
    for i, text in enumerate(info_text):
        try:
            screen.addstr(height - 1 - len(info_text) + i, 0, text.ljust(width), 
                         curses.color_pair(7) | curses.A_BOLD)
        except curses.error:
            pass
def main(screen):
    """Main function."""
    try:
        width, height = get_terminal_size()
        width = min(width, 80)  
        height = min(height, 24)  
        clock = DigitalClock(height, width)
        running = True
        show_stars = False
        while running:
            screen.clear()
            if show_stars:
                draw_stars(screen, height, width)
            clock.draw_clock(screen)
            draw_info(screen, height, width, clock)
            screen.refresh()
            key = screen.getch()
            if key == ord('q'):
                running = False
            elif key == ord('c'):
                clock.color_scheme = (clock.color_scheme + 1) % len(COLOR_SCHEMES)
            elif key == ord('s'):
                clock.show_seconds = not clock.show_seconds
            elif key == ord('d'):
                clock.show_date = not clock.show_date
            elif key == ord('a'):
                clock.show_am_pm = not clock.show_am_pm
            elif key == ord('h'):
                clock.use_24h = not clock.use_24h
            elif key == ord('r'):
                clock.rainbow_mode = not clock.rainbow_mode
            elif key == ord('m'):
                clock.animation_mode = (clock.animation_mode + 1) % 3
            elif key == ord('*'):
                show_stars = not show_stars
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup_screen(screen)
if __name__ == "__main__":
    curses.wrapper(main)