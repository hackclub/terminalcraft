import curses
import json
import time
from collections import deque

class TermPaint:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.canvas = [[(' ', 1) for _ in range(self.width - 1)] for _ in range(self.height - 1)]
        self.cursor_x = 0
        self.cursor_y = 0
        self.current_char = '#'
        self.current_color = 1
        self.running = True
        self.undo_stack = []
        self.redo_stack = []
        self.grid_enabled = False
        self.auto_save_enabled = False
        self.drawing_line = False
        self.line_start = (0, 0)
        self.last_save_time = time.time()
        
        curses.start_color()
        self.init_colors()
        curses.curs_set(0)
        self.stdscr.keypad(True)
        curses.mousemask(curses.ALL_MOUSE_EVENTS)
        
        self.run()

    def init_colors(self):
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Grid color

    def draw_canvas(self):
        self.stdscr.clear()
        for y, row in enumerate(self.canvas):
            for x, (char, color) in enumerate(row):
                # Draw grid if enabled
                if self.grid_enabled and x % 2 == 0 and y % 2 == 0:
                    self.stdscr.addstr(y, x, '+', curses.color_pair(8) | curses.A_DIM)
                else:
                    self.stdscr.addstr(y, x, char, curses.color_pair(color))
        # Draw cursor
        self.stdscr.addstr(self.cursor_y, self.cursor_x, self.current_char, curses.A_REVERSE)
        self.stdscr.refresh()

    def handle_input(self):
        key = self.stdscr.getch()
        
        if key == curses.KEY_UP:
            self.cursor_y = max(0, self.cursor_y - 1)
        elif key == curses.KEY_DOWN:
            self.cursor_y = min(self.height - 2, self.cursor_y + 1)
        elif key == curses.KEY_LEFT:
            self.cursor_x = max(0, self.cursor_x - 1)
        elif key == curses.KEY_RIGHT:
            self.cursor_x = min(self.width - 2, self.cursor_x + 1)
        elif key == ord(' '):
            self.undo_stack.append((self.cursor_x, self.cursor_y, self.canvas[self.cursor_y][self.cursor_x]))
            self.canvas[self.cursor_y][self.cursor_x] = (self.current_char, self.current_color)
        elif key == ord('c'):
            self.canvas = [[(' ', 1) for _ in range(self.width - 1)] for _ in range(self.height - 1)]
        elif key == ord('s'):
            self.save_to_file()
        elif key == ord('q'):
            self.running = False
        elif key == ord('u'):
            self.undo()
        elif key == ord('r'):
            self.redo()
        elif key == ord('x'):
            self.change_character()
        elif key == ord('z'):
            self.grid_enabled = not self.grid_enabled
        elif key == ord('a'):
            self.auto_save_enabled = not self.auto_save_enabled
        elif key in (ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7')):
            self.current_color = key - ord('0')
        elif key == ord('f'):
            self.flood_fill()
        elif key == ord('l'):
            self.handle_line_drawing()
        elif key == ord('h'):
            self.show_help()
        elif key == ord('o'):
            self.load_from_file()
        elif key == curses.KEY_MOUSE:
            self.handle_mouse()
        elif key == curses.KEY_RESIZE:
            self.handle_resize()

    def handle_resize(self):
        self.height, self.width = self.stdscr.getmaxyx()
        new_width = self.width - 1
        new_height = self.height - 1
        
        # Resize canvas
        new_canvas = []
        for y in range(new_height):
            new_row = []
            for x in range(new_width):
                if y < len(self.canvas) and x < len(self.canvas[y]):
                    new_row.append(self.canvas[y][x])
                else:
                    new_row.append((' ', 1))
            new_canvas.append(new_row)
        self.canvas = new_canvas
        self.cursor_x = min(self.cursor_x, new_width - 1)
        self.cursor_y = min(self.cursor_y, new_height - 1)

    def handle_mouse(self):
        try:
            _, x, y, _, _ = curses.getmouse()
            if x < self.width - 1 and y < self.height - 1:
                self.cursor_x = x
                self.cursor_y = y
        except:
            pass

    def flood_fill(self):
        x, y = self.cursor_x, self.cursor_y
        if y >= len(self.canvas) or x >= len(self.canvas[y]):
            return
        
        target_char, target_color = self.canvas[y][x]
        if target_char == self.current_char and target_color == self.current_color:
            return
        
        queue = deque([(x, y)])
        visited = set()
        
        while queue:
            x, y = queue.popleft()
            if (x, y) in visited or y < 0 or y >= len(self.canvas) or x < 0 or x >= len(self.canvas[y]):
                continue
                
            current_char, current_color = self.canvas[y][x]
            if current_char != target_char or current_color != target_color:
                continue
                
            self.undo_stack.append((x, y, self.canvas[y][x]))
            self.canvas[y][x] = (self.current_char, self.current_color)
            visited.add((x, y))
            
            queue.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])

    def handle_line_drawing(self):
        if not self.drawing_line:
            self.drawing_line = True
            self.line_start = (self.cursor_x, self.cursor_y)
        else:
            self.draw_line(*self.line_start, self.cursor_x, self.cursor_y)
            self.drawing_line = False

    def draw_line(self, x0, y0, x1, y1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        
        while True:
            self.undo_stack.append((x0, y0, self.canvas[y0][x0]))
            self.canvas[y0][x0] = (self.current_char, self.current_color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def show_help(self):
        help_text = [
            "TermPaint Commands:",
            "Arrows: Move cursor",
            "Space: Draw",
            "c: Clear canvas",
            "s: Save",
            "o: Load",
            "q: Quit",
            "u: Undo",
            "r: Redo",
            "x: Change character",
            "z: Toggle grid",
            "a: Toggle auto-save",
            "1-7: Change color",
            "f: Flood fill",
            "l: Draw line (press twice)",
            "h: Help",
            "Click: Move cursor",
            "Press any key to return."
        ]
        h = len(help_text) + 2
        w = max(len(line) for line in help_text) + 2
        y = (self.height - h) // 2
        x = (self.width - w) // 2
        help_win = curses.newwin(h, w, y, x)
        help_win.box()
        for i, line in enumerate(help_text):
            help_win.addstr(i+1, 1, line)
        help_win.refresh()
        self.stdscr.getch()

    def change_character(self):
        self.stdscr.addstr(self.height - 1, 0, "Enter new character: ")
        self.stdscr.refresh()
        curses.echo()
        self.current_char = chr(self.stdscr.getch())
        curses.noecho()
        self.stdscr.move(self.height - 1, 0)
        self.stdscr.clrtoeol()

    def undo(self):
        if self.undo_stack:
            x, y, prev = self.undo_stack.pop()
            self.redo_stack.append((x, y, self.canvas[y][x]))
            self.canvas[y][x] = prev

    def redo(self):
        if self.redo_stack:
            x, y, redo = self.redo_stack.pop()
            self.undo_stack.append((x, y, self.canvas[y][x]))
            self.canvas[y][x] = redo

    def save_to_file(self):
        with open("termpaint_output.json", "w") as f:
            json.dump(self.canvas, f)

    def load_from_file(self):
        try:
            with open("termpaint_output.json", "r") as f:
                self.canvas = json.load(f)
        except Exception as e:
            self.stdscr.addstr(self.height - 1, 0, f"Load error: {str(e)}")
            self.stdscr.getch()

    def run(self):
        while self.running:
            self.draw_canvas()
            self.handle_input()
            if self.auto_save_enabled and time.time() - self.last_save_time >= 5:
                self.save_to_file()
                self.last_save_time = time.time()

if __name__ == "__main__":
    curses.wrapper(TermPaint)
