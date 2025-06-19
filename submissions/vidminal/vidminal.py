import os
import sys
import time
from PIL import Image
import threading
import platform
import pygame
from moviepy import VideoFileClip
import contextlib
import io
import py7zr
import queue

# finds stuff, works with PyInstaller too (hopefully)
def find_resource_path(rel):
    try:
        base = sys._MEIPASS
    except AttributeError:
        base = os.path.abspath('.')
    return os.path.join(base, rel)

# pulls ffmpeg from zip, dumps in root, sets env, done
def extract_and_set_ffmpeg_bin():
    zip_path = find_resource_path('ffmpeg_bin.7z')
    sysname = platform.system().lower()
    arch = platform.machine().lower()
    if sysname == 'windows':
        ffmpeg_in_zip = 'windows/ffmpeg.exe'
        out_name = 'ffmpeg.exe'
    elif sysname == 'darwin':
        ffmpeg_in_zip = 'mac/ffmpeg'
        out_name = 'ffmpeg'
    elif sysname == 'linux':
        if 'arm' in arch:
            if '64' in arch:
                ffmpeg_in_zip = 'linux/linux-arm-64/ffmpeg'
            else:
                ffmpeg_in_zip = 'linux/linux-armhf-32/ffmpeg'
        elif '64' in arch:
            ffmpeg_in_zip = 'linux/linux-64/ffmpeg'
        else:
            ffmpeg_in_zip = 'linux/linux-32/ffmpeg'
        out_name = 'ffmpeg'
    else:
        ffmpeg_in_zip = None
        out_name = 'ffmpeg'
    if ffmpeg_in_zip:
        out_path = os.path.abspath(out_name)
        if not os.path.exists(out_path):
            with py7zr.SevenZipFile(zip_path, 'r') as archive:
                archive.extract(targets=[ffmpeg_in_zip], path='.')
            if sysname != 'windows':
                os.chmod(out_path, 0o755)  # make executable, I guess
        os.environ['FFMPEG_BINARY'] = out_path
    else:
        os.environ['FFMPEG_BINARY'] = 'ffmpeg'  # fallback, yolo

# turns video into frames & audio, dumps in folder
def get_stuff_from_video(vid, out, speed=24):
    if not os.path.exists(out):
        os.makedirs(out)
    audio = os.path.join(out, 'audio.ogg')
    print('Doing video things...')
    clip = VideoFileClip(vid)
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        clip.audio.write_audiofile(audio, codec='libvorbis')
    for i, frame in enumerate(clip.iter_frames(fps=speed, dtype='uint8')):
        Image.fromarray(frame).save(os.path.join(out, f'frame_{i+1:05d}.png'))
    print('Done.')
    return out, audio

# image to ascii, not rocket science
def pic_to_ascii(img, wide=80):
    chars = "@%#*+=-:. "
    pic = Image.open(img).convert('L')
    ratio = pic.height / pic.width
    tall = int(ratio * wide * 0.55)
    pic = pic.resize((wide, tall))
    px = pic.getdata()
    out = ''
    for i, p in enumerate(px):
        out += chars[p * len(chars) // 256]
        if (i + 1) % wide == 0:
            out += '\n'
    return out

# yields ascii frames, lazy style
def prepare_ascii_frames_stream(folder, wide=80, buffer_size=24):
    frames = sorted([f for f in os.listdir(folder) if f.startswith('frame_') and f.endswith('.png')])
    for f in frames:
        yield pic_to_ascii(os.path.join(folder, f), wide)

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
def play_ascii_video_stream(folder, audio, speed=24, wide=80, buffer_size=24):
    pygame.mixer.init()
    delay = 1.0 / speed
    frames = sorted([f for f in os.listdir(folder) if f.startswith('frame_') and f.endswith('.png')])
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
        print('\x1b[H', end='')  # move cursor home, don't ask how it works
        print(pic_to_ascii(os.path.join(folder, frames[i]), wide), end='')
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
    def extract_frames():
        for i, frame in enumerate(clip.iter_frames(fps=speed, dtype='uint8')):
            frame_path = os.path.join(out, f'frame_{i+1:05d}.png')
            Image.fromarray(frame).save(frame_path)
            frame_queue.put(frame_path)
        frame_queue.put(None)  # Sentinel for end
    threading.Thread(target=extract_frames, daemon=True).start()
    return out, audio, frame_queue

# plays ascii video + audio from stream, handles pause/quit
def play_ascii_video_stream_streaming(folder, audio, frame_queue, speed=24, wide=80, buffer_size=24):
    pygame.mixer.init()
    delay = 1.0 / speed
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
    while not stop_flag.is_set() and frames_buffer:
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
        print(pic_to_ascii(frames_buffer[0], wide), end='')
        i += 1
        frames_buffer.pop(0)
        next_frame = frame_queue.get()
        if next_frame is None:
            continue
        frames_buffer.append(next_frame)
    stop_flag.set()
    pygame.mixer.music.stop()
    key_thread.join()
    pygame.mixer.quit()

# main thing, asks stuff, runs stuff
def main():
    extract_and_set_ffmpeg_bin()  # pulls ffmpeg from zip, sets env, whatever
    print('Turns videos into ugly terminal art. With sound.')
    print('Made by a lazy coder. @github/SajagIN')
    vid_input = input('Video file? (default: BadApple.mp4): ').strip()
    vid = find_resource_path(vid_input) if vid_input else find_resource_path('BadApple.mp4')
    temp = input('Temp folder? (default: temp): ').strip() or 'temp'
    try:
        width = int(input('How wide? (default: 80): ').strip() or 80)
    except ValueError:
        width = 80
    try:
        fps = int(input('FPS? (default: 24): ').strip() or 24)
    except ValueError:
        fps = 24
    print('Space = pause, Q = quit')
    try:
        frames, audio, frame_queue = get_stuff_from_video_stream(vid, temp, speed=fps, buffer_size=fps)
        print('Streaming ASCII video...')
        play_ascii_video_stream_streaming(frames, audio, frame_queue, speed=fps, wide=width, buffer_size=fps)
    except Exception as e:
        print(f'Nope, broke: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()  # run it, or not, idc