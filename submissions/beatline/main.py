import curses
import time
import json
import argparse
from pathlib import Path
from audio.engine import AudioEngine
from audio.fileplayer import FileAudioEngine
from utils.beat import BeatDetector
from visualizers.waveform import drawWaveform
from visualizers.spectrum import drawSpectrum
from visualizers.pulse import drawPulse
from visualizers.circlebands import drawCircleBands
from visualizers.zones import drawBandZones
from visualizers.squares import drawEnergySquares  

configPath = Path("config.json")

modes = ["waveform", "spectrum", "pulse", "circlebands", "zones", "squares"] 
colorThemes = {
    "neon": ["cyan", "magenta", "blue"],
    "matrix": ["green", "black"],
    "dark": ["white", "black"]
}

def loadConfig():
    if configPath.exists():
        with open(configPath) as f:
            return json.load(f)
    return {
        "beatSensitivity": 1.0,
        "defaultMode": "waveform",
        "colorTheme": "neon"
    }

config = loadConfig()

parser = argparse.ArgumentParser(description="Beatline - Terminal Music Visualizer")
parser.add_argument("--audio", type=str, help="Path to audio file to use instead of microphone")
args = parser.parse_args()

def get_color_pair():
    return curses.color_pair(1)

def render(stdscr, audio, detector, mode, input_label, fg_color):
    samples = audio.read_chunk()
    beat = detector.detect(samples)
    stdscr.clear()

    stdscr.attron(fg_color)
    stdscr.addstr(0, 0, f"Input: {input_label}")
    stdscr.attroff(fg_color)

    if mode == "waveform":
        drawWaveform(stdscr, samples, fg_color)
    elif mode == "spectrum":
        drawSpectrum(stdscr, samples, fg_color)
    elif mode == "pulse":
        drawPulse(stdscr, samples, fg_color)
    elif mode == "circlebands":
        drawCircleBands(stdscr, samples, fg_color)
    elif mode == "zones":
        drawBandZones(stdscr, samples, fg_color)
    elif mode == "squares":  
        drawEnergySquares(stdscr, samples, fg_color)

    stdscr.attron(fg_color)
    try:
        max_y, max_x = stdscr.getmaxyx()
        footer = f"[1] Waveform  [2] Spectrum  [3] Pulse  [4] CircleBands  [5] Zones  [6] Squares  | [C] Theme ({config['colorTheme']})  [Q] Quit"
        stdscr.addstr(max_y - 1, 0, footer[:max_x - 1])
    except curses.error:
        pass
    stdscr.attroff(fg_color)
    stdscr.refresh()

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    curses.start_color()

    if not curses.has_colors():
        raise RuntimeError("Terminal does not support colors")

    theme = config["colorTheme"]
    color = colorThemes.get(theme, ["white"])[0]
    color_map = {
        "black": curses.COLOR_BLACK,
        "red": curses.COLOR_RED,
        "green": curses.COLOR_GREEN,
        "yellow": curses.COLOR_YELLOW,
        "blue": curses.COLOR_BLUE,
        "magenta": curses.COLOR_MAGENTA,
        "cyan": curses.COLOR_CYAN,
        "white": curses.COLOR_WHITE
    }
    fg = color_map.get(color, curses.COLOR_WHITE)
    if fg is None:
        fg = curses.COLOR_WHITE
    curses.init_pair(1, fg, curses.COLOR_BLACK)

    input_label = "Microphone"
    try:
        if args.audio:
            audio = FileAudioEngine(args.audio)
            input_label = f"File: {args.audio}"
        else:
            audio = AudioEngine.create(use_loopback=False)
    except RuntimeError as e:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Error: {str(e)}. Using microphone.")
        stdscr.refresh()
        time.sleep(2)
        audio = AudioEngine.create(use_loopback=False)

    detector = BeatDetector()
    detector.sensitivity = config["beatSensitivity"]
    mode = config["defaultMode"]

    fg_color = get_color_pair()

    while True:
        render(stdscr, audio, detector, mode, input_label, fg_color)
        ch = stdscr.getch()
        if ch == ord('q'):
            break
        elif ch == ord('1'):
            mode = "waveform"
        elif ch == ord('2'):
            mode = "spectrum"
        elif ch == ord('3'):
            mode = "pulse"
        elif ch == ord('4'):
            mode = "circlebands"
        elif ch == ord('5'):
            mode = "zones"
        elif ch == ord('6'): 
            mode = "squares"
        elif ch in (ord('c'), ord('C')):
            themes = list(colorThemes.keys())
            idx = (themes.index(config["colorTheme"]) + 1) % len(themes)
            config["colorTheme"] = themes[idx]
            configPath.write_text(json.dumps(config, indent=4))
            theme = config["colorTheme"]
            color = colorThemes.get(theme, ["white"])[0]
            fg = color_map.get(color, curses.COLOR_WHITE)
            if fg is None:
                fg = curses.COLOR_WHITE
            curses.init_pair(1, fg, curses.COLOR_BLACK)
            fg_color = get_color_pair()

if __name__ == "__main__":
    curses.wrapper(main)