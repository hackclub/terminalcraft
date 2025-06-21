import os
import sys
import warnings
warnings.filterwarnings('ignore')
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import contextlib
import io
# Suppress stderr globally (for moviepy, pygame, etc.)
class SuppressStderr:
    def __enter__(self):
        self._stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr.close()
        sys.stderr = self._stderr

with SuppressStderr():
    import time
    from PIL import Image
    import threading
    import platform
    import pygame
    from moviepy import VideoFileClip
    import py7zr
    import queue
    import colorama
    import multiprocessing
    import json

# finds stuff, works with PyInstaller too (hopefully)
def find_resource_path(rel):
    try:
        base = sys._MEIPASS
    except AttributeError:
        base = os.path.abspath('.')
    return os.path.join(base, rel)

# pulls ffmpeg from zip, dumps in root, sets env, done
def extract_and_set_ffmpeg_bin():
    sysname = platform.system().lower()
    arch = platform.machine().lower()
    if sysname == 'windows':
        zip_path = find_resource_path('windows.7z')
        ffmpeg_in_zip = 'ffmpeg.exe'
        out_name = 'ffmpeg.exe'
    elif sysname == 'darwin':
        zip_path = find_resource_path('mac.7z')
        ffmpeg_in_zip = 'ffmpeg'
        out_name = 'ffmpeg'
    elif sysname == 'linux':
        zip_path = find_resource_path('linux.7z')
        if 'arm' in arch:
            if '64' in arch:
                ffmpeg_in_zip = 'linux-arm-64/ffmpeg'
            else:
                ffmpeg_in_zip = 'linux-armhf-32/ffmpeg'
        elif '64' in arch:
            ffmpeg_in_zip = 'linux-64/ffmpeg'
        else:
            ffmpeg_in_zip = 'linux-32/ffmpeg'
        out_name = 'ffmpeg'
    else:
        zip_path = None
        ffmpeg_in_zip = None
        out_name = 'ffmpeg'
    if zip_path and ffmpeg_in_zip:
        out_path = os.path.abspath(out_name)
        if not os.path.exists(out_path):
            with py7zr.SevenZipFile(zip_path, 'r') as archive:
                archive.extract(targets=[ffmpeg_in_zip], path='.')
            if sysname != 'windows':
                os.chmod(out_path, 0o755)  # make executable
        os.environ['FFMPEG_BINARY'] = out_path
    else:
        os.environ['FFMPEG_BINARY'] = 'ffmpeg'  # fallback, yolo

# turns video into frames & audio, dumps in folder
def get_stuff_from_video(vid, out, speed=24, wide=160):
    if not os.path.exists(out):
        os.makedirs(out)
    audio = os.path.join(out, 'audio.ogg')
    print('Doing video things...')
    clip = VideoFileClip(vid)
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        clip.audio.write_audiofile(audio, codec='libvorbis')
        frame_paths = []
        for i, frame in enumerate(clip.iter_frames(fps=speed, dtype='uint8')):
            img = Image.fromarray(frame)
            # Reduce image size early
            ratio = img.height / img.width
            tall = int(ratio * wide * 0.55)
            img = img.resize((wide, tall))
            frame_path = os.path.join(out, f'frame_{i+1:05d}.png')
            img.save(frame_path)
            frame_paths.append(frame_path)
        # Multiprocessing: convert all frames to ASCII in parallel
        with multiprocessing.Pool() as pool:
            ascii_frames = pool.map(convert_frame_to_ascii, [(fp, wide) for fp in frame_paths])
        # Save ASCII frames as .txt for fast playback
        for i, ascii_txt in enumerate(ascii_frames):
            txt_path = os.path.join(out, f'frame_{i+1:05d}.txt')
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(ascii_txt)
    print('Done.')
    return out, audio

def load_options(options_path='options.json'):
    # Load options from options.json, fallback to defaults if missing/empty
    defaults = {
        'chars': "█▓▒░",
        'gamma': 1.2,
        'contrast': 1.5,
        'temp': 'temp',
        'wide': 160,
        'fps': 24
    }
    if not os.path.exists(options_path):
        with open(options_path, 'w', encoding='utf-8') as f:
            json.dump(defaults, f, indent=2)
        return defaults
    try:
        with open(options_path, 'r', encoding='utf-8') as f:
            opts = json.load(f)
        for k in defaults:
            if k not in opts or opts[k] == '' or opts[k] is None:
                opts[k] = defaults[k]
        return opts
    except Exception:
        return defaults

def pic_to_ascii_from_pil(pic, wide=None, high=None):
    import shutil
    from colorama import Style
    opts = load_options()
    chars = opts['chars']
    gamma = float(opts['gamma'])
    contrast = float(opts['contrast'])
    # Dynamically determine width and height as 90% of terminal size if not provided
    if wide is None or high is None:
        try:
            size = shutil.get_terminal_size()
            term_w = int(size.columns * 0.9)
            term_h = int(size.lines * 0.9)
            if wide is None:
                wide = max(20, term_w)
            if high is None:
                high = max(10, term_h)
        except Exception:
            if wide is None:
                wide = 160
            if high is None:
                high = 24
    # Maintain aspect ratio
    ratio = pic.height / pic.width
    tall = int(ratio * wide * 0.55)
    if tall > high:
        tall = high
        wide = int(tall / (ratio * 0.55))
    gray = pic.convert('L').resize((wide, tall))
    color = pic.convert('RGB').resize((wide, tall))
    px = list(gray.getdata())
    px_color = list(color.getdata())
    out = ''
    for i, (p, rgb) in enumerate(zip(px, px_color)):
        r, g, b = rgb
        r = int(255 * pow((r / 255), gamma) * contrast)
        g = int(255 * pow((g / 255), gamma) * contrast)
        b = int(255 * pow((b / 255), gamma) * contrast)
        r = min(max(r, 0), 255)
        g = min(max(g, 0), 255)
        b = min(max(b, 0), 255)
        out += f'\033[38;2;{r};{g};{b}m{chars[p * (len(chars) - 1) // 255]}'
        if (i + 1) % wide == 0:
            out += Style.RESET_ALL + '\n'
    out += Style.RESET_ALL
    return out

def pic_to_ascii(img, wide=None, high=None):
    from PIL import Image
    pic = Image.open(img)
    return pic_to_ascii_from_pil(pic, wide, high)

# Multiprocessing helper for frame conversion

def convert_frame_to_ascii(args):
    frame_path, wide = args
    from PIL import Image
    pic = Image.open(frame_path)
    return pic_to_ascii_from_pil(pic, wide)

# plays sound, can pause/stop, whatever
def play_sound(audio, pause_flag, stop_flag):
    pygame.mixer.init()
    pygame.mixer.music.load(audio)
    pygame.mixer.music.play()
    paused_at = 0
    was_paused = False
    while not stop_flag.is_set():
        if pause_flag.is_set():
            if not was_paused:
                paused_at = pygame.mixer.music.get_pos() / 1000.0
                pygame.mixer.music.pause()
                was_paused = True
        else:
            if was_paused:
                pygame.mixer.music.play(start=paused_at)
                was_paused = False
        if not pygame.mixer.music.get_busy() and not pause_flag.is_set():
            break
        pygame.time.wait(100)
    pygame.mixer.music.stop()
    pygame.mixer.quit()

# gets one char from user, non-blocking, magic
def getch():
    if platform.system() == 'Windows':
        import msvcrt
        if msvcrt.kbhit():
            return msvcrt.getch().decode('utf-8', errors='ignore')
        return None
    else:
        import sys, select, tty, termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            dr, _, _ = select.select([sys.stdin], [], [], 0)
            if dr:
                return sys.stdin.read(1)
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

# clears terminal, because why not
def clear_terminal():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

# plays ascii frames + sound, handles pause/quit
def play_ascii_video_stream(folder, audio, speed=24, wide=160, buffer_size=24):
    pygame.mixer.init()
    delay = 1.0 / speed
    frames = sorted([f for f in os.listdir(folder) if f.startswith('frame_') and f.endswith('.txt')])
    total = len(frames)
    stop_flag = threading.Event()
    pause_flag = threading.Event()
    pause_flag.clear()

    def keyboard_listener():
        while not stop_flag.is_set():
            key = getch()
            if key == ' ':
                if pause_flag.is_set():
                    pause_flag.clear()
                else:
                    pause_flag.set()
            if key in ('q', 'Q'):
                stop_flag.set()
            time.sleep(0.05)

    key_thread = threading.Thread(target=keyboard_listener, daemon=True)
    key_thread.start()

    def play_audio_from(pos):
        pygame.mixer.music.load(audio)
        pygame.mixer.music.play(start=pos)

    i = 0
    print('\x1b[2J', end='')  # clear screen, trust me
    start = time.time()
    play_audio_from(0)
    while i < total and not stop_flag.is_set():
        if pause_flag.is_set():
            pygame.mixer.music.pause()
            paused_at = i * delay
            while pause_flag.is_set() and not stop_flag.is_set():
                time.sleep(0.1)
            if stop_flag.is_set():
                break
            play_audio_from(paused_at)
            start = time.time() - paused_at
        tgt = start + i * delay
        now = time.time()
        sleep_for = tgt - now
        if sleep_for > 0:
            time.sleep(sleep_for)
        print('\x1b[H', end='')  # move cursor home
        # Batch terminal output: print whole frame at once
        print(pic_from_ascii_txt(os.path.join(folder, frames[i])), end='')
        i += 1
    stop_flag.set()
    pygame.mixer.music.stop()
    key_thread.join()
    pygame.mixer.quit()

# streams video/audio in parallel, starts playback after buffer fills
def get_stuff_from_video_stream(vid, out, speed=24, buffer_size=24):
    if not os.path.exists(out):
        os.makedirs(out)
    audio = os.path.join(out, 'audio.ogg')
    print('Doing video things...')
    clip = VideoFileClip(vid)
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        clip.audio.write_audiofile(audio, codec='libvorbis')
    frame_queue = queue.Queue(maxsize=buffer_size*2)
    total_frames = int(clip.fps * clip.duration)
    video_duration = clip.duration  # <-- add this
    def extract_frames():
        for i, frame in enumerate(clip.iter_frames(fps=speed, dtype='uint8')):
            frame_path = os.path.join(out, f'frame_{i+1:05d}.png')
            Image.fromarray(frame).save(frame_path)
            try:
                frame_queue.put_nowait(frame_path)
            except queue.Full:
                pass  # Don't block extraction, just skip putting in queue
        frame_queue.put(None)  # Sentinel for end
    threading.Thread(target=extract_frames, daemon=True).start()
    return out, audio, frame_queue, total_frames, video_duration

# plays ascii video + audio from stream, handles pause/quit
def play_ascii_video_stream_streaming(folder, audio, frame_queue, total_frames, speed=24, wide=160, buffer_size=24, video_duration=None):
    import queue as pyqueue
    pygame.mixer.init()
    delay = 1.0 / speed
    stop_flag = threading.Event()
    pause_flag = threading.Event()
    pause_flag.clear()
    rewind_forward = pyqueue.Queue()

    def keyboard_listener():
        import platform
        is_windows = platform.system() == 'Windows'
        while not stop_flag.is_set():
            key = getch()
            if not key:
                time.sleep(0.05)
                continue
            if key == ' ':
                if pause_flag.is_set():
                    pause_flag.clear()
                else:
                    pause_flag.set()
            elif key in ('q', 'Q'):
                stop_flag.set()
            elif key in ('a', 'A'):
                rewind_forward.put(-5 * speed)  # rewind 5s
            elif key in ('d', 'D'):
                rewind_forward.put(5 * speed)   # forward 5s
            elif is_windows:
                # Windows arrow keys: first getch() returns '\xe0', next is code
                if key in ('\xe0', '\x00'):
                    next_key = getch()
                    if next_key == 'M':  # right arrow
                        rewind_forward.put(speed)
                    elif next_key == 'K':  # left arrow
                        rewind_forward.put(-speed)
            else:
                # Unix: arrow keys are '\x1b', '[', 'C'/'D'
                if key == '\x1b':
                    next1 = getch()
                    if next1 == '[':
                        next2 = getch()
                        if next2 == 'C':  # right arrow
                            rewind_forward.put(speed)
                        elif next2 == 'D':  # left arrow
                            rewind_forward.put(-speed)
            time.sleep(0.05)

    key_thread = threading.Thread(target=keyboard_listener, daemon=True)
    key_thread.start()

    def play_audio_from(pos):
        pygame.mixer.music.load(audio)
        pygame.mixer.music.play(start=pos)

    def format_time(t):
        t = int(t)
        return f"{t//3600:02}:{(t%3600)//60:02}:{t%60:02}"

    print('\x1b[2J', end='')  # clear screen
    start = time.time()
    play_audio_from(0)
    i = 0
    frames_buffer = []
    # Pre-buffer
    while len(frames_buffer) < buffer_size:
        frame_path = frame_queue.get()
        if frame_path is None:
            break
        frames_buffer.append(frame_path)
    # Use actual video duration if provided
    total_time = video_duration if video_duration is not None else (total_frames / speed if total_frames > 0 else 0)
    while not stop_flag.is_set() and frames_buffer:
        # Handle rewind/forward requests
        jump = 0
        while not rewind_forward.empty():
            jump += rewind_forward.get()
        if jump != 0:
            # --- Begin robust seek logic: buffer only target frame, not intermediates ---
            target_i = max(0, min(i + jump, total_frames - 1))
            pygame.mixer.music.pause()
            frames_buffer.clear()
            # Wait for the target frame to be extracted (but do not display intermediates)
            frame_path = os.path.join(folder, f'frame_{target_i+1:05d}.png')
            wait_count = 0
            while not os.path.exists(frame_path):
                print('\x1b[H', end='')
                print('Buffering...'.center(wide), end='\n')
                time.sleep(0.05)
                wait_count += 1
                if wait_count > 400:
                    break
            if os.path.exists(frame_path):
                frames_buffer.append(frame_path)
            # Fill buffer with next frames if available, always from disk
            for idx in range(target_i+1, min(target_i+1+buffer_size, total_frames)):
                next_path = os.path.join(folder, f'frame_{idx+1:05d}.png')
                if os.path.exists(next_path):
                    frames_buffer.append(next_path)
                else:
                    break
            i = target_i
            # Set start time so seek bar is correct
            start = time.time() - i * delay
            # Resume audio at the new position only when frame is ready
            if frames_buffer:
                play_audio_from(i * delay)
            time.sleep(0.1)
            # --- End robust seek logic ---
        if pause_flag.is_set():
            pygame.mixer.music.pause()
            paused_at = i * delay
            while pause_flag.is_set() and not stop_flag.is_set():
                time.sleep(0.1)
            if stop_flag.is_set():
                break
            play_audio_from(paused_at)
            start = time.time() - paused_at
        tgt = start + i * delay
        now = time.time()
        sleep_for = tgt - now
        if sleep_for > 0:
            time.sleep(sleep_for)
        print('\x1b[H', end='')
        if frames_buffer:
            print(pic_to_ascii(frames_buffer[0], wide), end='')
        else:
            print('Buffering...'.center(wide), end='\n')
        # --- Seek bar with play/pause and time ---
        play_emoji = '⏸️' if not pause_flag.is_set() else '▶️'
        time_str = f"{format_time(i / speed)} / {format_time(total_time)}"
        fixed_len = len(play_emoji) + 2 + 2 + len(time_str)
        bar_width = max(1, wide - fixed_len)
        bar_pos = int((i / (total_frames - 1)) * bar_width) if total_frames > 1 else 0
        bar = '█' * bar_pos + '-' * (bar_width - bar_pos)
        print(f"{play_emoji} [{bar}] {time_str}")
        # --- End seek bar ---
        i += 1
        if frames_buffer:
            frames_buffer.pop(0)
        # Always refill buffer from disk after skip
        next_idx = i + len(frames_buffer)
        if next_idx < total_frames:
            next_path = os.path.join(folder, f'frame_{next_idx+1:05d}.png')
            if os.path.exists(next_path):
                frames_buffer.append(next_path)
    stop_flag.set()
    pygame.mixer.music.stop()
    key_thread.join()
    pygame.mixer.quit()

def pic_from_ascii_txt(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as f:
        return f.read()

# main thing, asks stuff, runs stuff
def main():
    extract_and_set_ffmpeg_bin()  # pulls ffmpeg from zip, sets env, whatever
    from colorama import Fore, Style
    box_width = 64
    box_color = Fore.CYAN + Style.BRIGHT
    text_color = Fore.YELLOW + Style.BRIGHT
    reset = Style.RESET_ALL
    def box_line(text, color=text_color):
        # Remove ANSI codes for length calculation
        import re
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        visible = ansi_escape.sub('', text)
        pad = box_width - 2 - len(visible)
        return f"{box_color}║{reset}{color}{text}{' ' * pad}{reset}{box_color}║{reset}"
    lines = [
        "",
        f"{box_color}╔{'═'* (box_width-2)}╗{reset}",
        box_line("  Turns videos into ugly terminal art. With sound.  "),
        box_line("  Made by a lazy coder. " + Fore.MAGENTA + "@github/SajagIN" + text_color + "  "),
        box_line(f"  {Fore.GREEN}Space{reset}{text_color} = pause  {Fore.GREEN}Q{reset}{text_color} = quit  {Fore.GREEN}A/D{reset}{text_color} = rewind/forward 5s  "),
        f"{box_color}╚{'═'* (box_width-2)}╝{reset}",
        ""
    ]
    print("\n".join(lines))
    opts = load_options('options.json')
    vid_input = input(Fore.CYAN + Style.BRIGHT + 'Video file?' + reset + f' (default: {Fore.YELLOW}BadApple.mp4{reset}): ').strip()
    vid = find_resource_path(vid_input) if vid_input else find_resource_path('BadApple.mp4')
    temp = opts['temp']
    width = int(opts['wide'])
    fps = int(opts['fps'])
    try:
        frames, audio, frame_queue, total_frames, video_duration = get_stuff_from_video_stream(vid, temp, speed=fps, buffer_size=fps)
        print(Fore.GREEN + Style.BRIGHT + 'Streaming ASCII video...' + reset)
        play_ascii_video_stream_streaming(frames, audio, frame_queue, total_frames, speed=fps, wide=width, buffer_size=fps, video_duration=video_duration)
    except Exception as e:
        print(Fore.RED + f'Nope, broke: {e}' + reset)
        sys.exit(1)

if __name__ == '__main__':
    while True:
        main()  # run it, or not, idc