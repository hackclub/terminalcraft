from __future__ import annotations
import cv2, ffpyplayer.player, time, sys, os, mimetypes, argparse
import numpy as np

from textual import containers, lazy
from textual.app import ComposeResult
from textual.binding import Binding
from textual.demo.page import PageScreen
from textual.theme import BUILTIN_THEMES
from textual.timer import Timer
from textual.widgets import (
    Footer,
    Label,
    ProgressBar,
    RichLog,
)

"""Parse arguments"""
parser = argparse.ArgumentParser(prog="play")
parser.add_argument("file")
parser.add_argument('-l', "--loop", action='store_true', help="Loop the media infinitely")
parser.add_argument("-s", "--scale",  default=0.05, type=float, help="Set the scale of the media render (default is 0.05, large scales may break the player)")

if len(sys.argv) < 2:
    parser.print_help()
    sys.exit()

args = parser.parse_args()

if args.scale <= 0:
    print("SCALE must be greater than 0.")
    sys.exit()

mediaName = args.file

if not os.path.exists(mediaName):
    print(f"{mediaName} does not exist.")
    sys.exit()

mimetypes.init()
typeGuess = mimetypes.guess_type(mediaName)[0]
if not typeGuess: # we couldn't find the file type, so it's probably a directory
    print(f"{mediaName} is not an audio, video, or image file.")
    sys.exit()

if typeGuess.split("/")[0] not in "audio/video/image":
    print(f"{mediaName} is not an audio, video, or image file.")
    sys.exit()
    

"""Load media"""
audio = ffpyplayer.player.MediaPlayer(mediaName, loglevel="fatal", ff_opts={'sync': 'audio', 'loop': 0 if args.loop else 1}) # 'framedrop': True, 

"""Media metadata"""
found_duration = False
duration = 0

"""RichLog to display the media"""
mediaFrame = RichLog(auto_scroll=False)

mediaName = mediaName.split("/")[-1]
mediaFrame.styles.width = len(mediaName)
mediaFrame.write(mediaName)

"""Time elapsed and total duration labels"""
currentTimeLabel = Label("--:--:-- ")
durationLabel = Label(" --:--:--")


from rich_pixels import Pixels
from PIL import Image

def formatFrame(frame):
    img, t = frame
    imgSize = img.get_size()
    
    memory = img.to_memoryview()
    img = np.asarray(memory[0])

    img = np.asarray(img).copy()
    img = img.reshape((imgSize[1], imgSize[0], 3), order="C")
    
    imgCopy = img.copy()

    scaledImg = cv2.resize(imgCopy, None, fx=args.scale, fy=args.scale, interpolation=cv2.INTER_AREA)
    return scaledImg

def formatTimestamp(duration):
    timestamp = [str(round(n)).zfill(2) for n in [duration//3600, (duration%3600)//60, duration%60]]
    return ":".join(timestamp)

stop = False
exitFunction = None
frame = None
def mediaTick(progressBar):
    global stop, duration, found_duration, frame
    frame, deltaTime = audio.get_frame()

    currentTime = audio.get_pts()

    if found_duration: # only show current time once we know total duration
        currentTimestamp = formatTimestamp(currentTime)
        currentTimeLabel.update(currentTimestamp + " ")
    else:
        metadata = audio.get_metadata()
        # sys.exit(metadata)
        duration = metadata['duration']

        timestamp = formatTimestamp(duration)
        durationLabel.update(" " + timestamp)

        found_duration = True
    
    if currentTime > 0:
        progressBar.set_progress(total=duration, progress=currentTime) # update progressbar as long as audio is playing
    
    if deltaTime == "paused":
        return
    elif deltaTime == "eof" or (currentTime == duration and duration > 0):
        stop = True
        audio.set_pause(True)
    elif frame is None:
        # if audio.get_metadata()['title']:
        return
    elif not stop:
        scaledImg = formatFrame(frame)

        rows, cols,_ = scaledImg.shape

        """
        imgText = ""

        for i in range(rows):
            for j in range(cols):
                R, G, B = scaledImg[i,j]
                luminance = 1
                luminance = 0.299*R/255 + 0.587*G/255 + 0.114*B/255 # https://stackoverflow.com/a/596241
                char = '░'
                if luminance > 3/4:
                    char = '█'
                elif luminance > 1/2:
                    char = '▓'
                elif luminance > 1/4:
                    char = '▒'

                hexCode = ''.join([hex(k)[2:].zfill(2) for k in scaledImg[i,j]])
                
                imgText += f"[#{hexCode}]{char+char}[/]"
                # imgText += char+char

            imgText += "\n"
        """

        mediaFrame.clear()
        mediaFrame.write(Pixels.from_image(Image.fromarray(scaledImg)))

        mediaFrame.styles.width = cols
        mediaFrame.styles.height = np.ceil(rows/2)
        
        time.sleep(deltaTime)



class ProgressBars(containers.VerticalGroup):
    DEFAULT_CSS = """
    ProgressBars {
        layout: horizontal;
        align: center middle;
        Bar {
            &> .bar--complete {
                color: $primary;
                background: $surface;
            }
            width: 88;
        }
    }

    """

    progressTimer: Timer

    def compose(self) -> ComposeResult:
            yield currentTimeLabel
            yield ProgressBar(show_eta=False, show_percentage=False)
            yield durationLabel

    def on_mount(self) -> None:
        """Set up the timer to advance every 0.1 seconds"""
        self.progressTimer = self.set_interval(0.01, lambda: mediaTick(self))
    
    def set_progress(self, total, progress) -> None:
        """Advance the progress bar"""
        self.query_one(ProgressBar).update(total=total, progress=progress)
        if stop:
            self.query_one(ProgressBar).update(total=total, progress=total)
        

class Picture(containers.VerticalGroup):
    DEFAULT_CSS = """
    Picture {
        RichLog {
            scrollbar-size: 0 0;
            height: 1;
        }
    }
    """

    def compose(self) -> ComposeResult:
        with containers.Center():
            yield mediaFrame
    

class PlayerScreen(PageScreen):
    """The Player screen"""

    CSS = """
    PlayerScreen { 
        Markdown { background: transparent; }
        & > VerticalScroll {
            scrollbar-gutter: stable;
            & > * {                          
                &:even { background: $boost; }
            }
        }
    }
    """

    BINDINGS = [Binding("escape", "blur", "Unfocus any focused widget", show=False)]

    def compose(self) -> ComposeResult:
        with lazy.Reveal(containers.VerticalScroll(can_focus=True)):
            with containers.Middle():
                yield Picture()
                yield Label()
                yield ProgressBars()
        yield Footer()
    
    


if __name__ == "__main__":
    from textual.app import App

    class MediaPlayer(App, inherit_bindings=False):
        BINDINGS = [
            Binding("space", "pause", "Pause"),
            Binding("left", "seek_left", "5s", priority=True),
            Binding("right", "seek_right", " ", priority=True),


            Binding("c", "None", "Code", priority=True, show=False),
            Binding("ctrl+q", "exit_player", "Quit", priority=True),
        ]
        def get_default_screen(self) -> Screen:
            global exitFunction
            exitFunction = self.exit_player

            return PlayerScreen()
        
        def action_pause(self):
            audio.toggle_pause()

        def action_seek_left(self):
            global stop
            audio.seek(-5)
            audio.set_pause(False)
            stop = False
        
        def action_seek_right(self):
            global stop
            if duration - audio.get_pts() > 5:
                audio.seek(5)
                audio.set_pause(False)
                stop = False

        def exit_player(self):
            audio.close_player()
            self.exit()

        action_exit_player = exit_player

    app = MediaPlayer()
    app.run()