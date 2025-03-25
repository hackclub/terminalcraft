#!/usr/bin/env python3

import os
import sys
import time
import random
import curses
import re
from enum import Enum

class GameMode(Enum):
    NORMAL = 1
    INSERT = 2
    VISUAL = 3
    COMMAND = 4
    EX = 5

class VimEscapeChallenge:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        
        if self.height < 15 or self.width < 60:
            raise ValueError("Window too small! Please resize your terminal to at least 60x15 characters.")
            
        self.current_mode = GameMode.NORMAL
        self.level = 1
        self.max_level = 5
        self.buffer = []
        self.cursor_y, self.cursor_x = 5, 0
        self.command_buffer = ""
        self.status_message = "Welcome to Vim Escape Challenge! You're trapped in Vim. Find the exit!"
        self.clues_found = 0
        self.total_clues = 3
        self.found_clues = set()
        self.game_won = False
        self.command_history = []
        self.registered_macros = {}
        self.marks = {}
        self.freeplay_mode = False
        self.has_completed_game = False
        self.setup_colors()
        self.load_level()
        
    def setup_colors(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    def load_level(self):
        self.buffer = []
        self.clues_found = 0
        self.found_clues = set()
        
        if self.freeplay_mode:
            self.load_freeplay_content()
            return
            
        if self.level == 1:
            self.buffer = [
                "=== LEVEL 1: THE BASICS ===",
                "",
                "You wake up trapped in a strange terminal... It seems to be Vim!",
                "Use your knowledge of Vim to escape. There are clues hidden in this text.",
                "",
                "Find 3 clues and then type :next to proceed to the next level.",
                "",
                "HINT: Try searching for words with '/'. The first clue is hidden near the word 'escape'.",
                "",
                "Sometimes the clue is invisible. You might need to move your cursor around to reveal it.",
                "",
                "# Hidden clue near 'escape' above - find with /escape",
                "",
                "# Another clue can be found by typing 'gg' to go to the top of the file",
                "",
                "# The final clue for this level can be revealed with 'G' to go to the bottom",
                "",
                "You need to master movement: h, j, k, l, w, b, e, 0, $, gg, G",
                "",
                "Good luck escaping Vim!"
            ]
            for _ in range(10):
                self.buffer.append("")
            self.buffer.append("# Bottom clue revealed with 'G'")
            
        elif self.level == 2:
            self.buffer = [
                "=== LEVEL 2: TEXT MANIPULATION ===",
                "",
                "Impressive! You've made it to level 2.",
                "Now you need to manipulate text to find the clues.",
                "",
                "Find 3 clues and then type :next to proceed.",
                "",
                "HINT: Try using 'dd' to delete a line that's blocking a clue.",
                "DELETE THIS LINE TO REVEAL A CLUE",
                "# First clue found by deleting a line",
                "",
                "HINT: The second clue requires changing text with 'c' commands.",
                "Change this text with 'cw' to find a clue",
                "",
                "HINT: The final clue requires using visual mode 'v' to select and 'y' to yank (copy) text.",
                "Select this special text with visual mode and yank it to reveal a clue: SPECIAL_VIM_CLUE",
                "",
                "Remember your text manipulation commands:",
                "d (delete), c (change), y (yank), p (put/paste), u (undo)"
            ]
            
        elif self.level == 3:
            self.buffer = [
                "=== LEVEL 3: ADVANCED NAVIGATION ===",
                "",
                "You're getting better! Level 3 will challenge your navigation skills.",
                "",
                "Find 3 clues and then type :next to proceed.",
                "",
                "HINT: Use 'f' followed by a character to find that character on the current line.",
                "Find the letter 'Z' in this line to discover a clue: abcdefghijklmnopqrstuvwxyZ",
                "",
                "HINT: Use marks to navigate. Place a mark with 'mx' (where x is any letter).",
                "Then return to that mark with `x. Mark this spot and then go elsewhere before returning.",
                "",
                "HINT: Search and replace with ':%s/find/replace/g'",
                "Replace all instances of 'puzzle' with 'solution' in this file to find the final clue.",
                "",
                "This puzzle requires careful attention.",
                "The puzzle is not easy to solve.",
                "Every puzzle has a solution.",
                "",
                "Advanced navigation includes:",
                "f/F (find), t/T (till), marks, search and replace"
            ]
            
        elif self.level == 4:
            self.buffer = [
                "=== LEVEL 4: MACROS AND REGISTERS ===",
                "",
                "Impressive navigation skills! Now for some real Vim power.",
                "",
                "Find 3 clues and then type :next to proceed.",
                "",
                "HINT: Use macros to record a sequence of commands.",
                "- Press 'qa' to start recording a macro into register 'a'",
                "- Perform some commands",
                "- Press 'q' again to stop recording",
                "- Press '@a' to execute the macro",
                "",
                "Record a macro that moves to the end of a line and adds ' - CHECKED' to reveal a clue.",
                "Apply this to the following three lines:",
                "First item",
                "Second item",
                "Third item",
                "",
                "HINT: Use registers to store text. Yank text into register 'b' with '\"by'.",
                "Then paste it with '\"bp'.",
                "",
                "HINT: The final clue requires executing a command multiple times.",
                "Use the number prefix: '3j' to move down 3 lines, etc.",
                "Go down exactly 5 lines with a single command to find a clue.",
                "",
                "",
                "",
                "",
                "",
                "# Clue found with 5j movement",
                "",
                "Macros and registers are powerful tools for repetitive tasks!"
            ]
            
        elif self.level == 5:
            self.buffer = [
                "=== LEVEL 5: FINAL ESCAPE ===",
                "",
                "This is the final challenge! Combine all your Vim skills to escape.",
                "",
                "You need to find and execute the secret escape command.",
                "",
                "HINT: The command is hidden in this text as invisible characters.",
                "You'll need to use 'ga' on suspicious spaces to reveal ASCII values.",
                "",
                "HINT: Use visual block mode (Ctrl+V) to select columns of text.",
                "There's a pattern of characters in column 10 of several lines below:",
                "",
                "Line one   E",
                "Line two   S",
                "Line three C",
                "Line four  A",
                "Line five  P",
                "Line six   E",
                "",
                "HINT: The final part requires executing an Ex command that combines:",
                "- setting a vim option",
                "- using a special keyword",
                "",
                "Try remembering the commands, or experiment with :set commands.",
                "",
                "When you find the escape command, execute it to win the game!",
                "",
                "Good luck, Vim master!"
            ]
    def load_freeplay_content(self):
        """Load content for freeplay mode"""
        self.buffer = [
            "=== VIM FREEPLAY MODE ===",
            "",
            "Congratulations on completing the Vim Escape Challenge!",
            "You've now unlocked Freeplay Mode where you can practice Vim commands freely.",
            "",
            "Here are some things you can try:",
            "",
            "1. Movement: h, j, k, l, w, b, e, 0, $, gg, G",
            "2. Editing: i (insert), d (delete), c (change), y (yank), p (paste)",
            "3. Visual selection: v (character), V (line), Ctrl+v (block)",
            "4. Commands: :s/find/replace/ (substitute), :q (quit)",
            "5. Search: /pattern (forward)",
            "6. Marks: m{a-z} (set mark), `{a-z} (jump to position)",
            "7. Macros: q{a-z} (record), @{a-z} (play)",
            "",
            "Feel free to modify this text and practice!",
            "",
            "--- Sample Text for Practice ---",
            "",
            "The quick brown fox jumps over the lazy dog.",
            "Pack my box with five dozen liquor jugs.",
            "How vexingly quick daft zebras jump!",
            "",
            "def example_function(argument):",
            "    # This is a comment",
            "    result = process(argument)",
            "    return result",
            "",
            "<html>",
            "  <head>",
            "    <title>Sample HTML</title>",
            "  </head>",
            "  <body>",
            "    <h1>Hello World</h1>",
            "    <p>This is a paragraph</p>",
            "  </body>",
            "</html>",
            "",
            "To reset the freeplay buffer, type :reset",
            "Restart the level to return to the challenge mode.",
            "Use :cheat123aaa to cheat and skip levels or unlock Freeplay mode.",
            "",
            "Happy practicing!"
        ]

    def display(self):
        self.stdscr.clear()
        self.height, self.width = self.stdscr.getmaxyx()
        
        if self.height < 15 or self.width < 60:
            self.stdscr.clear()
            try:
                self.stdscr.addstr(0, 0, "Window too small!")
                self.stdscr.addstr(1, 0, "Please resize to at least 60x15")
                self.stdscr.refresh()
                return
            except curses.error:
                pass
        
        visible_start = max(0, self.cursor_y - (self.height - 3))
        visible_end = min(len(self.buffer), visible_start + (self.height - 2))
        
        for i, line_idx in enumerate(range(visible_start, visible_end)):
            try:
                self.stdscr.addstr(i, 0, self.buffer[line_idx][:self.width-1])
            except curses.error:
                pass
        
        mode_name = 'INSERT' if self.current_mode == GameMode.INSERT else 'NORMAL' if self.current_mode == GameMode.NORMAL else 'VISUAL' if self.current_mode == GameMode.VISUAL else 'COMMAND'
        
        if self.freeplay_mode:
            status_bar = f" {mode_name} | FREEPLAY MODE "
        else:
            status_bar = f" {mode_name} | Level: {self.level}/{self.max_level} | Clues: {self.clues_found}/{self.total_clues} "
            
        status_bar = status_bar + " " * (self.width - len(status_bar) - 1)
        
        try:
            self.stdscr.attron(curses.color_pair(2))
            self.stdscr.addstr(self.height-2, 0, status_bar)
            self.stdscr.attroff(curses.color_pair(2))
            
            if self.current_mode == GameMode.COMMAND or self.current_mode == GameMode.EX:
                self.stdscr.addstr(self.height-1, 0, ":" + self.command_buffer)
            else:
                message_color = 3 if "found" in self.status_message.lower() else 4 if "error" in self.status_message.lower() else 1
                self.stdscr.attron(curses.color_pair(message_color))
                self.stdscr.addstr(self.height-1, 0, self.status_message[:self.width-1])
                self.stdscr.attroff(curses.color_pair(message_color))
        except curses.error:
            pass

        if self.current_mode == GameMode.COMMAND or self.current_mode == GameMode.EX:
            cursor_pos = 1 + len(self.command_buffer)
            if cursor_pos >= self.width:
                cursor_pos = self.width - 1
            self.stdscr.move(self.height-1, cursor_pos)
        else:
            display_y = self.cursor_y - visible_start
            
            if display_y >= 0 and display_y < self.height - 2:
                if len(self.buffer) > 0 and self.cursor_y < len(self.buffer):
                    line_length = len(self.buffer[self.cursor_y])
                    if self.cursor_x > line_length:
                        self.cursor_x = max(0, line_length)
                        
                try:
                    self.stdscr.move(display_y, self.cursor_x)
                except curses.error:
                    self.stdscr.move(0, 0)
            else:
                self.stdscr.move(0, 0)
        
        self.stdscr.refresh()

    def check_for_clues(self, action=None):
        if self.freeplay_mode:
            return
            
        if self.level == 1:
            if action == "search" and "escape" in self.status_message.lower():
                self.reveal_clue("Search skills help you find hidden patterns.", "level1_search")
            
            if action == "goto_top":
                self.reveal_clue("Navigation to document boundaries reveals secrets.", "level1_top")
                
            if action == "goto_bottom":
                self.reveal_clue("Use :next to proceed when all clues are found.", "level1_bottom")
                
        elif self.level == 2:
            if action == "delete_line" and any("first clue" in line.lower() for line in self.buffer):
                self.reveal_clue("Deletion can reveal what lies beneath.", "level2_delete")
                
            if action == "change_word":
                self.reveal_clue("Changing content creates new possibilities.", "level2_change")
                
            if action == "yank" and "SPECIAL_VIM_CLUE" in self.status_message:
                self.reveal_clue("Copy operations preserve important information.", "level2_yank")
                
        elif self.level == 3:
            if action == "find_char" and "Z" in self.status_message:
                self.reveal_clue("Precise character navigation is essential.", "level3_find")
                
            if action == "jump_to_mark":
                self.reveal_clue("Marks let you return to important locations.", "level3_mark")
                
            if action == "search_replace" and all("solution" in line for line in self.buffer if "puzzle" in line):
                self.reveal_clue("Global substitutions transform the entire document.", "level3_replace")
                
        elif self.level == 4:
            if action == "execute_macro" and sum(" - CHECKED" in line for line in self.buffer) >= 3:
                self.reveal_clue("Macros automate repetitive tasks effectively.", "level4_macro")
                
            if action == "paste_register":
                self.reveal_clue("Registers store and retrieve important content.", "level4_register")
                
            if action == "multiple_command" and "5j" in self.status_message:
                self.reveal_clue("Command multipliers increase efficiency.", "level4_multiple")
                
        elif self.level == 5:
            if action == "examine_char":
                self.reveal_clue("Hidden characters can be revealed with inspection.", "level5_examine")
                
            if action == "visual_block" and "ESCAPE" in self.status_message:
                self.reveal_clue("Column-based selection uncovers vertical patterns.", "level5_visual")
                
            if "escape vim" in self.status_message.lower() or "set exit" in self.status_message.lower():
                self.reveal_clue("The escape command is: :set escapevim", "level5_final")
                
            if action == "win_game":
                self.game_won = True
                self.has_completed_game = True
                self.status_message = "Congratulations! You've escaped from Vim! Type :freeplay to continue."

    def reveal_clue(self, clue_message, clue_id):
        if clue_id not in self.found_clues:
            self.found_clues.add(clue_id)
            self.clues_found += 1
            
            saved_buffer = self.buffer.copy()
            saved_cursor_y, saved_cursor_x = self.cursor_y, self.cursor_x
            
            notification = [
                "╔═════════════════════════════════════════════════════╗",
                "║                   CLUE DISCOVERED!                  ║",
                f"║  [{self.clues_found}/{self.total_clues}] {clue_message[:41]}  ║",
                "║                                                     ║",
                "║             Press any key to continue...            ║",
                "╚═════════════════════════════════════════════════════╝"
            ]
            
            start_y = max(0, (self.height - len(notification)) // 2)
            start_x = max(0, (self.width - len(notification[0])) // 2)
            
            self.buffer = notification
            self.cursor_y = len(notification) - 1
            self.cursor_x = 0
            self.display()
            
            self.stdscr.getch()
            
            self.buffer = saved_buffer
            self.cursor_y, self.cursor_x = saved_cursor_y, saved_cursor_x
            
            self.status_message = f"Clue found! ({self.clues_found}/{self.total_clues}) {clue_message}"
        else:
            self.status_message = f"Clue already found. ({self.clues_found}/{self.total_clues}) {clue_message}"

    def process_normal_mode(self, key):
        buffer_empty = len(self.buffer) == 0
        
        if key == ord('i'):
            self.current_mode = GameMode.INSERT
            self.status_message = "-- INSERT MODE --"
        elif key == ord('v'):
            self.current_mode = GameMode.VISUAL
            self.status_message = "-- VISUAL MODE --"
        elif key == ord(':'):
            self.current_mode = GameMode.COMMAND
            self.command_buffer = ""
        elif key == ord('/'):
            self.current_mode = GameMode.COMMAND
            self.command_buffer = "/"
        elif key == ord('h') and self.cursor_x > 0:
            self.cursor_x -= 1
        elif key == ord('l'):
            if not buffer_empty and self.cursor_y < len(self.buffer) and self.cursor_x < len(self.buffer[self.cursor_y]) - 1:
                self.cursor_x += 1
        elif key == ord('j') and not buffer_empty and self.cursor_y < len(self.buffer) - 1:
            self.cursor_y += 1
            if self.cursor_y < len(self.buffer) and self.cursor_x > 0:
                self.cursor_x = min(self.cursor_x, max(0, len(self.buffer[self.cursor_y]) - 1))
        elif key == ord('k') and self.cursor_y > 0 and not buffer_empty:
            self.cursor_y -= 1
            if self.cursor_x > 0:
                self.cursor_x = min(self.cursor_x, max(0, len(self.buffer[self.cursor_y]) - 1))
        elif key == ord('w'):
            if not buffer_empty and self.cursor_y < len(self.buffer):
                line = self.buffer[self.cursor_y]
                start = self.cursor_x + 1
                if start >= len(line):
                    if self.cursor_y < len(self.buffer) - 1:
                        self.cursor_y += 1
                        self.cursor_x = 0
                else:
                    match = re.search(r'\b\w', line[start:])
                    if match:
                        self.cursor_x = start + match.start()
                    else:
                        self.cursor_x = len(line) - 1
        elif key == ord('b'):
            if not buffer_empty and self.cursor_y < len(self.buffer):
                line = self.buffer[self.cursor_y]
                if self.cursor_x == 0:
                    if self.cursor_y > 0:
                        self.cursor_y -= 1
                        self.cursor_x = len(self.buffer[self.cursor_y]) - 1
                else:
                    part = line[:self.cursor_x]
                    matches = list(re.finditer(r'\b\w', part))
                    if matches:
                        self.cursor_x = matches[-1].start()
                    else:
                        self.cursor_x = 0
        elif key == ord('0'):
            self.cursor_x = 0
        elif key == ord('$'):
            if not buffer_empty and self.cursor_y < len(self.buffer):
                self.cursor_x = max(0, len(self.buffer[self.cursor_y]) - 1)
        elif key == ord('g'):
            next_key = self.stdscr.getch()
            if next_key == ord('g'):
                self.cursor_y = 0
                self.cursor_x = 0
                self.check_for_clues(action="goto_top")
        elif key == ord('G'):
            if not buffer_empty:
                self.cursor_y = len(self.buffer) - 1
                self.cursor_x = 0
                self.check_for_clues(action="goto_bottom")
        elif key == ord('d'):
            next_key = self.stdscr.getch()
            if next_key == ord('d'):
                if not buffer_empty and self.cursor_y < len(self.buffer):
                    deleted_line = self.buffer.pop(self.cursor_y)
                    if self.cursor_y >= len(self.buffer) and self.cursor_y > 0:
                        self.cursor_y -= 1
                    self.check_for_clues(action="delete_line")
                    self.status_message = f"Deleted: {deleted_line}"
        elif key == ord('c'):
            next_key = self.stdscr.getch()
            if next_key == ord('w'):
                self.current_mode = GameMode.INSERT
                if not buffer_empty and self.cursor_y < len(self.buffer):
                    line = self.buffer[self.cursor_y]
                    start = self.cursor_x
                    match = re.search(r'\b\W', line[start:])
                    end = len(line) if not match else start + match.start()
                    self.buffer[self.cursor_y] = line[:start] + line[end:]
                    self.check_for_clues(action="change_word")
        elif key == ord('y'):
            next_key = self.stdscr.getch()
            if next_key == ord('y'):
                if not buffer_empty and self.cursor_y < len(self.buffer):
                    self.status_message = f"Yanked: {self.buffer[self.cursor_y]}"
                    if "SPECIAL_VIM_CLUE" in self.buffer[self.cursor_y]:
                        self.check_for_clues(action="yank")
        elif key == ord('f'):
            char_to_find = self.stdscr.getch()
            if not buffer_empty and self.cursor_y < len(self.buffer):
                line = self.buffer[self.cursor_y]
                start = self.cursor_x + 1
                if start < len(line):
                    pos = line.find(chr(char_to_find), start)
                    if pos != -1:
                        self.cursor_x = pos
                        if chr(char_to_find) == 'Z':
                            self.status_message = "Found Z!"
                            self.check_for_clues(action="find_char")
        elif key == ord('m'):
            mark_key = self.stdscr.getch()
            mark_char = chr(mark_key)
            self.marks[mark_char] = (self.cursor_y, self.cursor_x)
            self.status_message = f"Mark '{mark_char}' set"
        elif key == ord('`'):
            mark_key = self.stdscr.getch()
            mark_char = chr(mark_key)
            if mark_char in self.marks:
                self.cursor_y, self.cursor_x = self.marks[mark_char]
                self.check_for_clues(action="jump_to_mark")
                self.status_message = f"Jumped to mark '{mark_char}'"
            else:
                self.status_message = f"Mark '{mark_char}' not set"
        elif key == ord('q'):
            reg_key = self.stdscr.getch()
            reg_char = chr(reg_key)
            if hasattr(self, 'recording_macro') and self.recording_macro:
                self.recording_macro = False
                self.status_message = f"Finished recording to register {reg_char}"
            else:
                self.recording_macro = True
                self.status_message = f"Recording to register {reg_char}"
        elif key == ord('@'):
            reg_key = self.stdscr.getch()
            self.status_message = f"Executed macro from register {chr(reg_key)}"
            if self.level == 4:
                self.check_for_clues(action="execute_macro")
        elif key == ord('g') and ord('a'):
            self.status_message = "Examining character (ga)"
            self.check_for_clues(action="examine_char")
        elif key == 22:
            self.status_message = "Visual Block mode"
            if not buffer_empty and any("ESCAPE" in line for line in self.buffer):
                self.check_for_clues(action="visual_block")
        elif key in range(49, 58):
            num = key - 48
            next_cmd = self.stdscr.getch()
            if next_cmd == ord('j'):
                if not buffer_empty:
                    target_y = min(self.cursor_y + num, len(self.buffer) - 1)
                    self.cursor_y = target_y
                    self.status_message = f"{num}j"
                    if num == 5:
                        self.check_for_clues(action="multiple_command")

    def process_insert_mode(self, key):
        if key == 27:
            self.current_mode = GameMode.NORMAL
            self.status_message = "-- NORMAL MODE --"
        elif key in (curses.KEY_BACKSPACE, 127):
            if len(self.buffer) > 0 and self.cursor_x > 0:
                line = self.buffer[self.cursor_y]
                self.buffer[self.cursor_y] = line[:self.cursor_x-1] + line[self.cursor_x:]
                self.cursor_x -= 1
        elif key == 10:
            if len(self.buffer) > 0:
                line = self.buffer[self.cursor_y]
                self.buffer[self.cursor_y] = line[:self.cursor_x]
                self.buffer.insert(self.cursor_y + 1, line[self.cursor_x:])
                self.cursor_y += 1
                self.cursor_x = 0
        else:
            if len(self.buffer) > 0:
                line = self.buffer[self.cursor_y]
                self.buffer[self.cursor_y] = line[:self.cursor_x] + chr(key) + line[self.cursor_x:]
                self.cursor_x += 1

    def process_visual_mode(self, key):
        if key == 27:
            self.current_mode = GameMode.NORMAL
            self.status_message = "-- NORMAL MODE --"
        elif key == ord('h') and self.cursor_x > 0:
            self.cursor_x -= 1
        elif key == ord('l'):
            if len(self.buffer) > 0 and self.cursor_x < len(self.buffer[self.cursor_y]) - 1:
                self.cursor_x += 1
        elif key == ord('j') and self.cursor_y < len(self.buffer) - 1:
            self.cursor_y += 1
        elif key == ord('k') and self.cursor_y > 0:
            self.cursor_y -= 1
        elif key == ord('y'):
            self.current_mode = GameMode.NORMAL
            self.status_message = "Yanked text: SPECIAL_VIM_CLUE"
            self.check_for_clues(action="yank")

    def process_command_mode(self, key):
        if key == 27:
            self.current_mode = GameMode.NORMAL
            self.status_message = "-- NORMAL MODE --"
            self.command_buffer = ""
        elif key in (curses.KEY_BACKSPACE, 127):
            if len(self.command_buffer) > 0:
                if self.command_buffer[0] == '/':
                    if len(self.command_buffer) > 1:
                        self.command_buffer = self.command_buffer[:-1]
                else:
                    self.command_buffer = self.command_buffer[:-1]
        elif key == 10:
            if self.command_buffer.startswith('/'):
                search_term = self.command_buffer[1:]
                if search_term:
                    found = False
                    for i, line in enumerate(self.buffer):
                        if search_term in line:
                            self.cursor_y = i
                            self.cursor_x = line.find(search_term)
                            found = True
                            break
                    if found:
                        self.status_message = f"Found '{search_term}'"
                        self.check_for_clues(action="search")
                    else:
                        self.status_message = f"Pattern not found: '{search_term}'"
            else:
                if self.command_buffer == "next" and not self.freeplay_mode:
                    if self.clues_found >= self.total_clues:
                        self.level = min(self.level + 1, self.max_level)
                        self.load_level()
                        self.status_message = f"Level {self.level} loaded!"
                    else:
                        self.status_message = f"You need to find all {self.total_clues} clues first!"
                elif self.command_buffer == "freeplay":
                    if self.has_completed_game or self.game_won:
                        self.freeplay_mode = True
                        self.load_freeplay_content()
                        self.status_message = "Entered Freeplay Mode! Practice your Vim skills freely."
                    else:
                        self.status_message = "You need to complete all levels first to unlock Freeplay Mode!"
                elif self.command_buffer == "challenge" and self.freeplay_mode:
                    self.freeplay_mode = False
                    self.level = 1
                    self.load_level()
                    self.status_message = "Restarted Challenge Mode! Level 1 loaded."
                elif self.command_buffer == "reset" and self.freeplay_mode:
                    self.load_freeplay_content()
                    self.status_message = "Freeplay buffer reset!"
                elif self.command_buffer == "q" or self.command_buffer == "quit":
                    sys.exit(0)
                elif self.command_buffer.startswith("s/"):
                    parts = self.command_buffer[2:].split('/')
                    if len(parts) >= 2:
                        find_text, replace_text = parts[0], parts[1]
                        count = 0
                        for i, line in enumerate(self.buffer):
                            if find_text in line:
                                self.buffer[i] = line.replace(find_text, replace_text)
                                count += 1
                        self.status_message = f"Replaced {count} occurrences of '{find_text}' with '{replace_text}'"
                        self.check_for_clues(action="search_replace")
                elif self.command_buffer == "set escapevim" and self.level == 5 and not self.freeplay_mode:
                    self.check_for_clues(action="win_game")
                elif self.command_buffer == "cheat123aaa":
                    self.handle_cheat_code()
                else:
                    self.status_message = f"Unknown command: '{self.command_buffer}'"
            
            self.command_history.append(self.command_buffer)
            self.command_buffer = ""
            self.current_mode = GameMode.NORMAL
        else:
            self.command_buffer += chr(key)

    def handle_cheat_code(self):
        """Process the cheat code command with a secret menu"""
        self.current_mode = GameMode.NORMAL
        
        cheat_menu = [
            "=== SECRET CHEAT MENU ===",
            "",
            "1: Skip to level 1",
            "2: Skip to level 2",
            "3: Skip to level 3", 
            "4: Skip to level 4",
            "5: Skip to level 5",
            "F: Unlock Freeplay mode",
            "W: Win the game immediately",
            "ESC: Cancel",
            "",
            "Enter your choice:"
        ]
        
        saved_buffer = self.buffer.copy()
        saved_cursor_y, saved_cursor_x = self.cursor_y, self.cursor_x
        
        self.buffer = cheat_menu
        self.cursor_y = len(cheat_menu) - 1
        self.cursor_x = 0
        self.display()
        
        choice = self.stdscr.getch()
        
        if choice == 27:
            self.buffer = saved_buffer
            self.cursor_y, self.cursor_x = saved_cursor_y, saved_cursor_x
            self.status_message = "Cheat cancelled"
        elif choice == ord('1'):
            self.level = 1
            self.freeplay_mode = False
            self.load_level()
            self.status_message = "Cheat activated: Skipped to Level 1"
        elif choice == ord('2'):
            self.level = 2
            self.freeplay_mode = False
            self.load_level()
            self.status_message = "Cheat activated: Skipped to Level 2"
        elif choice == ord('3'):
            self.level = 3
            self.freeplay_mode = False
            self.load_level()
            self.status_message = "Cheat activated: Skipped to Level 3"
        elif choice == ord('4'):
            self.level = 4
            self.freeplay_mode = False
            self.load_level()
            self.status_message = "Cheat activated: Skipped to Level 4"
        elif choice == ord('5'):
            self.level = 5
            self.freeplay_mode = False
            self.load_level()
            self.status_message = "Cheat activated: Skipped to Level 5"
        elif choice in (ord('F'), ord('f')):
            self.has_completed_game = True
            self.freeplay_mode = True
            self.load_freeplay_content()
            self.status_message = "Cheat activated: Freeplay mode unlocked"
        elif choice in (ord('W'), ord('w')):
            self.has_completed_game = True
            self.game_won = True
            self.status_message = "Cheat activated: Game won!"
        else:
            self.buffer = saved_buffer
            self.cursor_y, self.cursor_x = saved_cursor_y, saved_cursor_x
            self.status_message = "Invalid cheat option"

    def main_loop(self):
        while True:
            if self.game_won and not self.freeplay_mode:
                self.display()
                time.sleep(3)
                self.game_won = False
                self.has_completed_game = True
                self.status_message = "Type :freeplay to continue in freeplay mode, or :q to quit."

            self.display()
            
            key = self.stdscr.getch()
            
            if self.current_mode == GameMode.NORMAL:
                self.process_normal_mode(key)
            elif self.current_mode == GameMode.INSERT:
                self.process_insert_mode(key)
            elif self.current_mode == GameMode.VISUAL:
                self.process_visual_mode(key)
            elif self.current_mode == GameMode.COMMAND or self.current_mode == GameMode.EX:
                self.process_command_mode(key)

def main(stdscr):
    curses.curs_set(1)
    stdscr.clear()
    
    try:
        game = VimEscapeChallenge(stdscr)
        
        game.main_loop()
    except ValueError as e:
        stdscr.clear()
        try:
            stdscr.addstr(0, 0, str(e))
            stdscr.addstr(1, 0, "Press any key to exit...")
            stdscr.refresh()
            stdscr.getch()
        except curses.error:
            pass

if __name__ == "__main__":
    curses.wrapper(main)
