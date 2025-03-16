import time
import curses
from PIL import Image
import colorsys
import os
import threading

def get_terminal_width():
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80

def get_ascii_char(luminance):
    ascii_chars = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    index = int(luminance * (len(ascii_chars) - 1))
    return ascii_chars[index]

def get_color_code(r, g, b):
    r = int(r)
    g = int(g)
    b = int(b)

    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

    if s < 0.2:
        gray = int(round((r + g + b) / 3.0 / 256.0 * 24))
        return 232 + gray
    else:
        r_index = int(round(r / 255.0 * 5))
        g_index = int(round(g / 255.0 * 5))
        b_index = int(round(b / 255.0 * 5))
        color_index = 16 + r_index * 36 + g_index * 6 + b_index
        return color_index
    
def get_color_pair(r,g,b):
    return get_color_code(r,g,b)

def pomodoro_timer(stdscr, work_time=25, break_time=5, image_path="background.jpg"):
    pause_flag = False
    countdown_thread = None
    remaining_seconds = 0
    phase = "Work"
    exit_flag = False

    def display_time(stdscr, seconds, phase, box_y, box_x, box_height, box_width):
        minutes, seconds = divmod(seconds, 60)
        time_str = f"{minutes:02d}:{seconds:02d}"
        text = f"{phase}: {time_str}"

        stdscr.attron(curses.color_pair(curses.COLOR_WHITE))
        stdscr.border(curses.ACS_VLINE, curses.ACS_VLINE, curses.ACS_HLINE, curses.ACS_HLINE, box_y, box_x, box_height, box_x + box_width)
        stdscr.attroff(curses.color_pair(curses.COLOR_WHITE))

        x = box_x + (box_width // 2) - (len(text) // 2)
        y = box_y + (box_height // 2)
        stdscr.addstr(y, x, text)
        stdscr.refresh()

    def countdown(stdscr, seconds, phase, box_y, box_x, box_height, box_width):
        nonlocal pause_flag, remaining_seconds
        remaining_seconds = seconds
        while remaining_seconds > 0 and not pause_flag and not exit_flag:
            display_time(stdscr, remaining_seconds, phase, box_y, box_x, box_height, box_width)
            time.sleep(1)
            remaining_seconds = remaining_seconds - 1
        return
    
    def play_sound(phase):
        if phase == "Work":
            print("\a")
        else:
            print("\a\a")

    def toggle_pause():
        nonlocal pause_flag
        pause_flag = not pause_flag
        if not pause_flag and countdown_thread and not countdown_thread.is_alive():
            start_countdown()
    
    def start_countdown():
        nonlocal countdown_thread, pause_flag, remaining_seconds
        pause_flag = False
        height, width = stdscr.getmaxyx()
        box_width = 20
        box_height = 5
        box_x = (width // 2) - (box_width // 2)
        box_y = (height // 2) - (box_height // 2)
        if phase == "Work":
            seconds = remaining_seconds if remaining_seconds > 0 and phase == "Work" else work_time * 60
            countdown_thread = threading.Thread(target=countdown, args=(stdscr, seconds, "Work", box_y, box_x, box_height, box_width))
        else:
            seconds = remaining_seconds if remaining_seconds > 0 and phase == "Break" else break_time * 60
            countdown_thread = threading.Thread(target=countdown, args=(stdscr, seconds, "Break", box_y, box_x, box_height, box_width))
        countdown_thread.start()

    try:
        curses.curs_set(0)
        curses.start_color()
        for i in range(255):
            curses.init_pair(i + 1, i, curses.COLOR_BLACK)
        curses.init_pair(curses.COLOR_WHITE, curses.COLOR_WHITE, curses.COLOR_BLACK)

        img = Image.open(image_path).convert("RGB")
        terminal_width = get_terminal_width()
        img_width, img_height = img.size
        aspect_ratio = img_height / img_width
        new_height = int(terminal_width * aspect_ratio * 0.5)
        img = img.resize((terminal_width, new_height))

        start_countdown()

        while True:
            stdscr.clear()
            for y in range(new_height):
                for x in range(terminal_width):
                    r, g, b = img.getpixel((x, y))
                    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
                    ascii_char = get_ascii_char(luminance)
                    color_pair = get_color_pair(r, g, b) + 1
                    try:
                        stdscr.attron(curses.color_pair(color_pair))
                        stdscr.addch(y, x, ascii_char)
                        stdscr.attroff(curses.color_pair(color_pair))
                    except curses.error:
                        pass

            height, width = stdscr.getmaxyx()
            pause_button_x = (width // 2) - 5
            pause_button_y = (height // 2) + 4
            exit_button_x = (width // 2) - 5
            exit_button_y = (height // 2) + 5
            stdscr.addstr(pause_button_y, pause_button_x, "[P]ause")
            stdscr.addstr(exit_button_y, exit_button_x, "[E]xit")

            stdscr.refresh()

            key = stdscr.getch()
            if key == ord('p') or key == ord('P'):
                toggle_pause()
            elif key == ord('e') or key == ord('E'):
                exit_flag = True #set exit flag
                break
            elif countdown_thread and not countdown_thread.is_alive() and not pause_flag:
                play_sound(phase)
                phase = "Break" if phase == "Work" else "Work"
                remaining_seconds = 0
                start_countdown()

    except KeyboardInterrupt:
        pass
    finally:
        curses.curs_set(1)
        exit(0)

def start_timer(work_time=25, break_time=5, image_path="background.jpg"):
    import pathlib
    current = pathlib.Path(__file__).parent.resolve()
    curses.wrapper(lambda stdscr: pomodoro_timer(stdscr, work_time, break_time, str(current) + "\\background.jpg"))