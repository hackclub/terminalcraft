import numpy as np

def drawBandZones(stdscr, samples, color):
    height, width = stdscr.getmaxyx()
    height -= 2

    fft = np.abs(np.fft.rfft(samples))
    fft /= np.max(fft) if np.max(fft) > 0 else 1

    bands = {
        "SUB": fft[0:2],
        "BASS": fft[2:7],
        "L-MID": fft[7:12],
        "MID": fft[12:46],
        "H-MID": fft[46:91],
        "PRES": fft[91:137],
        "BRILL": fft[137:]
    }

    band_names = list(bands.keys())
    zone_width = width // len(band_names)

    for i, name in enumerate(band_names):
        energy = np.mean(bands[name])
        level = int(energy * height)
        start_x = i * zone_width

        for y in range(height - 1, height - 1 - level, -1):
            for x in range(start_x, start_x + zone_width):
                if 0 <= x < width and 0 <= y < height:
                    try:
                        stdscr.addch(y, x, ord('#'), color)
                    except:
                        pass

        label_x = start_x + max(0, (zone_width - len(name)) // 2)
        if height + 1 < stdscr.getmaxyx()[0]:
            try:
                stdscr.addstr(height, label_x, name[:zone_width], color)
            except:
                pass