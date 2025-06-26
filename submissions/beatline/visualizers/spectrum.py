def drawSpectrum(stdscr, samples, color):
    height, width = stdscr.getmaxyx()
    step = max(1, len(samples) // width)

    for i in range(min(width, len(samples))):
        val = max(samples[i * step:i * step + step], default=0)
        val = max(0.0, min(val, 1.0))  # clamp to [0, 1]
        bar_height = int(val * (height - 2))

        for y in range(height - 2, height - 2 - bar_height, -1):
            if 0 <= y < height and 0 <= i < width:
                stdscr.addch(y, i, ord('*'), color)