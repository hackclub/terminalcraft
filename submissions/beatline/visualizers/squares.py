import numpy as np
import curses

def drawEnergySquares(stdscr, samples, _):
    height, width = stdscr.getmaxyx()
    h_half = height // 2
    w_half = width // 2

    fft = np.abs(np.fft.rfft(samples))
    fft = np.log1p(fft)

    sub = np.mean(fft[0:10]) / 2.5
    bass = np.mean(fft[10:40]) / 3.0
    mids = np.mean(fft[40:100]) / 4.0
    treble = np.mean(fft[100:]) / 4.0

    def clip(x):
        return min(max(x, 0.0), 1.0)

    intensities = {
        "SUB": clip(sub),
        "BASS": clip(bass),
        "MIDS": clip(mids),
        "TREBLE": clip(treble)
    }

    def get_attr(intensity):
        if intensity < 0.2:
            return curses.color_pair(1) | curses.A_DIM
        elif intensity < 0.4:
            return curses.color_pair(1)
        elif intensity < 0.7:
            return curses.color_pair(1) | curses.A_BOLD
        else:
            return curses.color_pair(1) | curses.A_REVERSE

    def draw_square(y0, x0, y1, x1, intensity):
        attr = get_attr(intensity)
        for y in range(y0, y1):
            for x in range(x0, x1):
                try:
                    stdscr.addch(y, x, ord(' '), attr)
                except:
                    pass

    draw_square(0, 0, h_half, w_half, intensities["SUB"])
    draw_square(0, w_half, h_half, width, intensities["BASS"])
    draw_square(h_half, 0, height, w_half, intensities["MIDS"])
    draw_square(h_half, w_half, height, width, intensities["TREBLE"])

    try:
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(1, 2, "SUB")
        stdscr.addstr(1, w_half + 2, "BASS")
        stdscr.addstr(h_half + 1, 2, "MIDS")
        stdscr.addstr(h_half + 1, w_half + 2, "TREBLE")
        stdscr.attroff(curses.color_pair(1))
    except:
        pass