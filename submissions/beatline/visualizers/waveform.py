import numpy as np

def drawWaveform(stdscr, samples, color):
    height, width = stdscr.getmaxyx()
    height -= 2

    chars = [' ', '.', '˙', ':', '-', '=', '+', '*', '#', '█']
    step = max(1, len(samples) // width)

    scaled = np.interp(samples[::step], [-1, 1], [0, height - 1])

    for x, val in enumerate(scaled[:width]):
        y = int(height - val - 1)
        intensity = int((val / (height - 1)) * (len(chars) - 1))
        intensity = max(0, min(intensity, len(chars) - 1))

        try:
            stdscr.addch(y, x, chars[intensity], color)
        except:
            pass