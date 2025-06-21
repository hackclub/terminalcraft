#!/usr/bin/env python3
import os
import time
import curses
import random
from datetime import datetime
SAMPLE_TEXTS = [
    "The quick brown fox jumps over the lazy dog.",
    "Programming is the art of telling another human what one wants the computer to do.",
    "The best way to predict the future is to invent it.",
    "Simplicity is the ultimate sophistication.",
    "Code is like humor. When you have to explain it, it's bad.",
    "First, solve the problem. Then, write the code.",
    "Any fool can write code that a computer can understand. Good programmers write code that humans can understand.",
    "Experience is the name everyone gives to their mistakes.",
    "The only way to learn a new programming language is by writing programs in it.",
    "Sometimes it pays to stay in bed on Monday, rather than spending the rest of the week debugging Monday's code."
]
class TypingTest:
    """A class representing a typing test."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.reset_test()
    def reset_test(self):
        """Reset the typing test with a new text."""
        self.text = random.choice(SAMPLE_TEXTS)
        self.user_input = ""
        self.start_time = None
        self.end_time = None
        self.current_pos = 0
        self.errors = 0
        self.test_complete = False
        self.wpm = 0
        self.accuracy = 100.0
    def start(self):
        """Start the typing test."""
        self.start_time = datetime.now()
    def add_char(self, char):
        """Add a character to the user input."""
        if self.start_time is None:
            self.start()
        if not self.test_complete:
            self.user_input += char
            if len(self.user_input) <= len(self.text) and char != self.text[self.current_pos]:
                self.errors += 1
            self.current_pos += 1
            if self.current_pos >= len(self.text):
                self.end_time = datetime.now()
                self.test_complete = True
                self.calculate_results()
    def remove_char(self):
        """Remove the last character from user input."""
        if self.start_time is not None and not self.test_complete and self.user_input:
            self.user_input = self.user_input[:-1]
            self.current_pos -= 1
    def calculate_results(self):
        """Calculate typing speed and accuracy."""
        if self.start_time and self.end_time:
            time_taken = (self.end_time - self.start_time).total_seconds() / 60
            self.wpm = int(len(self.text) / 5 / time_taken)
            correct_chars = len(self.text) - self.errors
            self.accuracy = round(correct_chars / len(self.text) * 100, 1)
    def draw(self, screen):
        """Draw the typing test on the screen."""
        screen.clear()
        for x in range(self.width):
            try:
                screen.addch(0, x, '-')
                screen.addch(self.height - 1, x, '-')
            except curses.error:
                pass
        for y in range(self.height):
            try:
                screen.addch(y, 0, '|')
                screen.addch(y, self.width - 1, '|')
            except curses.error:
                pass
        title = " Terminal Typing Test "
        try:
            screen.addstr(1, self.width // 2 - len(title) // 2, title, curses.A_BOLD)
        except curses.error:
            pass
        instructions = " Type the text below | Press ESC to restart | Ctrl+C to quit "
        try:
            screen.addstr(2, self.width // 2 - len(instructions) // 2, instructions)
        except curses.error:
            pass
        try:
            screen.addstr(3, 1, "-" * (self.width - 2))
        except curses.error:
            pass
        wrapped_text = []
        current_line = ""
        for word in self.text.split():
            if len(current_line) + len(word) + 1 <= self.width - 4:  
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                wrapped_text.append(current_line)
                current_line = word
        if current_line:
            wrapped_text.append(current_line)
        for i, line in enumerate(wrapped_text):
            try:
                screen.addstr(5 + i, 2, line)
            except curses.error:
                pass
        try:
            screen.addstr(7 + len(wrapped_text), 1, "-" * (self.width - 2))
        except curses.error:
            pass
        user_input_y = 9 + len(wrapped_text)
        for i, char in enumerate(self.user_input):
            if i < len(self.text):
                if char == self.text[i]:
                    attr = curses.color_pair(1)  
                else:
                    attr = curses.color_pair(2)  
                try:
                    screen.addch(user_input_y, 2 + i % (self.width - 4), char, attr)
                    if (i + 1) % (self.width - 4) == 0:
                        user_input_y += 1
                except curses.error:
                    pass
        if not self.test_complete:
            cursor_x = 2 + self.current_pos % (self.width - 4)
            cursor_y = user_input_y + self.current_pos // (self.width - 4)
            try:
                screen.addch(cursor_y, cursor_x, '_', curses.A_BLINK)
            except curses.error:
                pass
        if self.test_complete:
            results = f" Results: {self.wpm} WPM | Accuracy: {self.accuracy}% "
            try:
                screen.addstr(self.height - 3, self.width // 2 - len(results) // 2, 
                             results, curses.color_pair(3) | curses.A_BOLD)
            except curses.error:
                pass
            restart_msg = " Press ESC to try again "
            try:
                screen.addstr(self.height - 2, self.width // 2 - len(restart_msg) // 2, restart_msg)
            except curses.error:
                pass
        screen.refresh()
def initialize_screen():
    """Initialize the curses screen."""
    screen = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) 
    curses.curs_set(0)  
    curses.noecho()
    curses.cbreak()
    screen.keypad(True)
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
        typing_test = TypingTest(width, height)
        while True:
            typing_test.draw(screen)
            key = screen.getch()
            if key == 27:  
                typing_test.reset_test()
            elif key == curses.KEY_BACKSPACE or key == 127:  
                typing_test.remove_char()
            elif 32 <= key <= 126:  
                typing_test.add_char(chr(key))
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
if __name__ == "__main__":
    try:
        screen = initialize_screen()
        main(screen)
    finally:
        cleanup_screen(screen)
        print("Typing test ended.")