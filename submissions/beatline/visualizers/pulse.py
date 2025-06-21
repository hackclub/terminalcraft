import numpy as np
import curses

frame_counter = 0
last_boom_frame = -10

def drawPulse(stdscr, samples, color):
    global frame_counter, last_boom_frame
    height, width = stdscr.getmaxyx()
    peak = np.max(np.abs(samples))
    frame_counter += 1

    intensity = min(peak / 1.0, 1.0)
    attr = curses.color_pair(1)
    if intensity < 0.2:
        attr |= curses.A_DIM
    elif intensity < 0.5:
        attr |= 0
    elif intensity < 0.8:
        attr |= curses.A_BOLD
    else:
        attr |= curses.A_REVERSE

    center_y = height // 2
    center_x = width // 2

    ring_width = 2

    if peak > 0.1:
        last_boom_frame = frame_counter
        pulse_strength = int(intensity * 4) + 1
    else:
        pulse_strength = 0

    pulse_age = frame_counter - last_boom_frame
    radius = pulse_age * (1 + pulse_strength)

    for y in range(height):
        for x in range(0, width, 2):
            dy = y - center_y
            dx = (x - center_x) // 2
            dist = (dx**2 + dy**2) ** 0.5

            if radius - ring_width <= dist <= radius + ring_width:
                try:
                    stdscr.addstr(y, x, "██", attr)
                except:
                    pass
            else:
                try:
                    stdscr.addstr(y, x, "  ", curses.color_pair(1) | curses.A_DIM)
                except:
                    pass