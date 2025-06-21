import cv2
import time
import os
import sys
import argparse
import numpy as np
from typing import Tuple, List, Optional
from threading import Thread
from queue import Queue
ASCII_CHARS_STANDARD = '@%#*+=-:. '
ASCII_CHARS_DETAILED = '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,"^`\'.'
ASCII_CHARS_INVERTED = ' .:=-+*#%@'
def resize_frame(frame, new_width: int = 100, new_height: Optional[int] = None) -> cv2.Mat:
    """
    Resize the frame while maintaining aspect ratio unless new_height is specified
    """
    height, width = frame.shape[:2]
    if new_height is None:
        aspect_ratio = height / width
        new_height = int(aspect_ratio * new_width)
        new_height = int(new_height * 0.5)  
    return cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
def convert_to_grayscale(frame) -> cv2.Mat:
    """
    Convert frame to grayscale
    """
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
def map_pixels_to_ascii(frame, char_set: str = 'standard', colored: bool = False) -> List[str]:
    """
    Map each pixel to an ASCII character based on intensity
    """
    if char_set == 'detailed':
        chars = ASCII_CHARS_DETAILED
    elif char_set == 'inverted':
        chars = ASCII_CHARS_INVERTED
    else:  
        chars = ASCII_CHARS_STANDARD
    pixels = frame.flatten()
    ascii_chars = [chars[min(len(chars)-1, int(pixel * len(chars) / 256))] for pixel in pixels]
    return ascii_chars
def convert_frame_to_ascii(frame, width: int = 100, height: Optional[int] = None, 
char_set: str = 'standard', colored: bool = False) -> str:
    """
    Convert a frame to ASCII art with optional color support
    """
    resized_frame = resize_frame(frame, width, height)
    if colored:
        color_frame = resized_frame.copy()
        grayscale_frame = convert_to_grayscale(resized_frame)
        ascii_chars = map_pixels_to_ascii(grayscale_frame, char_set)
        rows = []
        height, width = grayscale_frame.shape[:2]
        for y in range(height):
            row = []
            for x in range(width):
                b, g, r = color_frame[y, x]
                char_idx = y * width + x
                if char_idx < len(ascii_chars):
                    colored_char = f"\033[38;2;{r};{g};{b}m{ascii_chars[char_idx]}\033[0m"
                    row.append(colored_char)
            rows.append(''.join(row))
    else:
        grayscale_frame = convert_to_grayscale(resized_frame)
        ascii_chars = map_pixels_to_ascii(grayscale_frame, char_set)
        rows = []
        for i in range(0, len(ascii_chars), width):
            row = ascii_chars[i:i+width]
            rows.append(''.join(row))
    return '\n'.join(rows)
def clear_console():
    """
    Clear the console screen based on the operating system
    """
    os.system('cls' if os.name == 'nt' else 'clear')
def preload_frames(video_path: str, queue: Queue, max_frames: int = 0, width: int = 100, 
height: Optional[int] = None, char_set: str = 'standard', colored: bool = False):
    """
    Preload and process video frames in a separate thread
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        queue.put(None)  
        return
    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames_to_load = total_frames if max_frames <= 0 else min(max_frames, total_frames)
    while frame_count < frames_to_load:
        ret, frame = cap.read()
        if not ret:
            break
        ascii_frame = convert_frame_to_ascii(frame, width, height, char_set, colored)
        queue.put((ascii_frame, frame_count, total_frames))
        frame_count += 1
    queue.put(None)
    cap.release()
def play_video_as_ascii(video_path: str, width: int = 100, height: Optional[int] = None, 
fps_cap: int = 30, char_set: str = 'standard', colored: bool = False, preload: bool = False, 
loop: bool = False, reverse: bool = False):
    """
    Play a video as ASCII art in the terminal
    """
    print(f"Playing video: {video_path}")
    print(f"Playback settings: {width}x{height if height else 'auto'}, {fps_cap} FPS, {char_set} charset")
    print(f"Color mode: {'Enabled' if colored else 'Disabled'}")
    print(f"Preloading: {'Enabled' if preload else 'Disabled'}")
    print(f"Controls: Ctrl+C to exit")
    time.sleep(1.5)  
    if preload:
        frame_queue = Queue(maxsize=1000)  
        preload_thread = Thread(
            target=preload_frames, 
            args=(video_path, frame_queue, 0, width, height, char_set, colored)
        )
        preload_thread.daemon = True
        preload_thread.start()
        first_frame = frame_queue.get()
        if first_frame is None:
            print(f"Error: Could not open video file {video_path}")
            return
        ascii_frame, frame_count, total_frames = first_frame
        cap = cv2.VideoCapture(video_path)
        original_fps = cap.get(cv2.CAP_PROP_FPS) if cap.isOpened() else fps_cap
        cap.release()
        fps = min(original_fps, fps_cap)
        frame_delay = 1 / fps
        all_frames = [first_frame]
        try:
            while True:
                frame_data = frame_queue.get()
                if frame_data is None:  
                    break
                all_frames.append(frame_data)
            while True:
                frames_to_play = all_frames
                if reverse:
                    frames_to_play = frames_to_play[::-1]
                for ascii_frame, frame_count, total_frames in frames_to_play:
                    clear_console()
                    print(ascii_frame)
                    progress = f"Frame: {frame_count+1}/{total_frames} ({(frame_count+1)/total_frames*100:.1f}%)"
                    print(progress)
                    time.sleep(frame_delay)
                if not loop:
                    break
        except KeyboardInterrupt:
            print("\nPlayback stopped by user")
        finally:
            if preload_thread.is_alive():
                preload_thread.join(timeout=1.0)
    else:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video file {video_path}")
            return
        original_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = min(original_fps, fps_cap)
        frame_delay = 1 / fps
        try:
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    if loop:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = cap.read()
                        if not ret:  
                            break
                        frame_count = 0
                    else:
                        break
                ascii_frame = convert_frame_to_ascii(frame, width, height, char_set, colored)
                clear_console()
                print(ascii_frame)
                progress = f"Frame: {frame_count+1}/{total_frames} ({(frame_count+1)/total_frames*100:.1f}%)"
                print(progress)
                time.sleep(frame_delay)
                frame_count += 1
        except KeyboardInterrupt:
            print("\nPlayback stopped by user")
        finally:
            if 'cap' in locals() and cap.isOpened():
                cap.release()
            print("\nPlayback finished")
def detect_terminal_size():
    """
    Detect terminal size and return appropriate width and height
    """
    try:
        terminal_width = os.get_terminal_size().columns
        terminal_height = os.get_terminal_size().lines - 2  
        return terminal_width, terminal_height
    except (AttributeError, OSError):
        return 100, 40
def main():
    parser = argparse.ArgumentParser(description='Convert video to ASCII art and play in terminal')
    parser.add_argument('video_path', type=str, help='Path to the video file')
    parser.add_argument('--width', type=int, default=0, help='Width of ASCII art (default: auto-detect)')
    parser.add_argument('--height', type=int, default=0, help='Height of ASCII art (default: auto-detect)')
    parser.add_argument('--fps', type=int, default=30, help='Maximum FPS cap (default: 30)')
    parser.add_argument('--charset', type=str, choices=['standard', 'detailed', 'inverted'], default='standard',
                        help='ASCII character set to use (default: standard)')
    parser.add_argument('--color', action='store_true', help='Enable color output')
    parser.add_argument('--preload', action='store_true', help='Preload all frames before playing (smoother but uses more memory)')
    parser.add_argument('--loop', action='store_true', help='Loop the video playback')
    parser.add_argument('--reverse', action='store_true', help='Play the video in reverse')
    args = parser.parse_args()
    if not os.path.isfile(args.video_path):
        print(f"Error: Video file '{args.video_path}' does not exist")
        sys.exit(1)
    if args.width <= 0 or args.height <= 0:
        term_width, term_height = detect_terminal_size()
        if args.width <= 0:
            args.width = term_width
        if args.height <= 0:
            args.height = term_height
    play_video_as_ascii(
        args.video_path, 
        args.width, 
        args.height, 
        args.fps, 
        args.charset, 
        args.color, 
        args.preload, 
        args.loop, 
        args.reverse
    )
if __name__ == "__main__":
    main()