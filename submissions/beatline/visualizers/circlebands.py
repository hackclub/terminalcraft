import numpy as np
import math

def drawCircleBands(stdscr, samples, color):
    height, width = stdscr.getmaxyx()
    center_y, center_x = height // 2, width // 2
    radius = min(center_y, center_x) - 2

    fft = np.log1p(np.abs(np.fft.rfft(samples)))
    fft /= np.max(fft) if np.max(fft) > 0 else 1

    sectors = 96
    angle_step = 2 * math.pi / sectors
    band_step = max(1, len(fft) // sectors)

    for i in range(sectors):
        angle = i * angle_step
        energy = np.mean(fft[i * band_step:(i + 1) * band_step])
        length = int(energy * radius)

        for r in range(1, length + 1):
            y = int(center_y + r * math.sin(angle))
            x = int(center_x + r * math.cos(angle))
            if 0 <= y < height and 0 <= x < width:
                char = '●' if r > radius * 0.7 else '*' if r > radius * 0.4 else '.'
                try:
                    stdscr.addch(y, x, ord(char), color)
                except:
                    pass

            try:
                stdscr.addstr(center_y - radius - 1, center_x - 3, "TREBLE", color)
                stdscr.addstr(center_y + radius + 1, center_x - 2, "BASS", color)
                stdscr.addstr(center_y, center_x - radius - 6, "SUB", color)
                stdscr.addstr(center_y, center_x + radius + 1, "MID", color)
            except:
                pass