import sys
import os
import time
import threading
import msvcrt
import math
import random
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)  
except ImportError as e:
    print("This program requires the colorama module.")
    print("Please install colorama using: pip install colorama")
    print(f"Error: {e}")
    sys.exit(1)
try:
    from audio import get_ultra_realistic_piano_sample
    AUDIO_AVAILABLE = True
    AUDIO_TYPE = "High Quality Audio"
    def play_piano_note(frequency, duration=1.0, velocity=0.8):
        """Play piano note using high quality synthesis"""
        sample = get_ultra_realistic_piano_sample(frequency, duration, velocity)
        sample.play()
except ImportError:
    from audio_fallback import audio_engine
    AUDIO_AVAILABLE = False
    AUDIO_TYPE = "Fallback Audio"
    def play_piano_note(frequency, duration=1.0, velocity=0.8):
        """Play piano note using fallback audio"""
        audio_engine.play_piano_note(frequency, duration)
PIANO_KEYS = {
    'a': 261.63,  
    'w': 277.18,  
    's': 293.66,  
    'e': 311.13,  
    'd': 329.63,  
    'f': 349.23,  
    't': 369.99,  
    'g': 392.00,  
    'y': 415.30,  
    'h': 440.00,  
    'u': 466.16,  
    'j': 493.88,  
    'k': 523.25,  
}
NOTE_NAMES = {
    'a': 'C4',
    'w': 'C#4',
    's': 'D4',
    'e': 'D#4',
    'd': 'E4',
    'f': 'F4',
    't': 'F#4',
    'g': 'G4',
    'y': 'G#4',
    'h': 'A4',
    'u': 'A#4',
    'j': 'B4',
    'k': 'C5',
}
NOTE_DURATION = 300
pressed_keys = set()
last_note = ""
currently_playing = False  
def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')
def draw_keyboard():
    """Draw a visual representation of the piano keyboard."""
    print("\n" + Style.BRIGHT + Fore.CYAN + "=" * 60)
    print(Style.BRIGHT + Fore.WHITE + Back.BLUE + " CLI PIANO - Press keys to play notes (press ESC to exit) ".center(60))
    print(Style.BRIGHT + Fore.CYAN + "=" * 60)
    black_keys = "  W E   T Y U   "
    black_key_positions = []
    print(Style.BRIGHT + Fore.WHITE + " " * 5, end="")
    for i, k in enumerate(black_keys):
        if k != " ":
            if k.lower() in pressed_keys:
                print(Back.RED + f" {k} " + Style.RESET_ALL, end="")
            else:
                print(Back.BLACK + f" {k} " + Style.RESET_ALL, end="")
            black_key_positions.append(i)
        else:
            print("   ", end="")
    print()
    print(Style.BRIGHT + Fore.WHITE + " " * 5, end="")
    for i in range(len(black_keys)):
        if i in black_key_positions:
            if black_keys[i].lower() in pressed_keys:
                print(Back.RED + "███" + Style.RESET_ALL, end="")
            else:
                print(Back.BLACK + "███" + Style.RESET_ALL, end="")
        else:
            print("   ", end="")
    print()
    white_keys = "A S D F G H J K"
    print(Style.BRIGHT + Fore.BLACK, end="")
    for k in white_keys:
        if k.lower() in pressed_keys:
            print(Back.RED + f" {k} " + Style.RESET_ALL, end=" ")
        else:
            print(Back.WHITE + f" {k} " + Style.RESET_ALL, end=" ")
    print()
    print(Style.BRIGHT + Fore.BLACK, end="")
    for k in white_keys:
        if k.lower() in pressed_keys:
            print(Back.RED + "███" + Style.RESET_ALL, end="  ")
        else:
            print(Back.WHITE + "███" + Style.RESET_ALL, end="  ")
    print()
    for _ in range(3):  
        print(Style.BRIGHT + Fore.BLACK, end="")
        for k in white_keys:
            if k.lower() in pressed_keys:
                print(Back.RED + "███" + Style.RESET_ALL, end="  ")
            else:
                print(Back.WHITE + "███" + Style.RESET_ALL, end="  ")
        print()
    print("\n" + Style.BRIGHT + Fore.CYAN + "-" * 60)
    print(Style.BRIGHT + Fore.YELLOW + "Last played note: " + 
          Style.BRIGHT + Fore.WHITE + last_note)
def play_note(frequency, key):
    """Play a note with the given frequency."""
    global last_note, currently_playing
    if currently_playing:
        return
    pressed_keys.add(key)
    last_note = f"{NOTE_NAMES[key]} ({key})"
    currently_playing = True
    velocity = 0.7 + random.uniform(0, 0.3)  
    play_piano_note(frequency, duration=2.0, velocity=velocity)
    def reset_playing():
        global currently_playing
        time.sleep(0.4)  
        currently_playing = False
        if key in pressed_keys:
            pressed_keys.remove(key)
    threading.Thread(target=reset_playing, daemon=True).start()
def show_splash_screen():
    """Show a splash screen with the piano logo."""
    clear_screen()
    print(Style.BRIGHT + Fore.YELLOW + """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║  ██████╗ ██╗ █████╗ ███╗   ██╗ ██████╗               ║
    ║  ██╔══██╗██║██╔══██╗████╗  ██║██╔═══██╗              ║
    ║  ██████╔╝██║███████║██╔██╗ ██║██║   ██║              ║
    ║  ██╔═══╝ ██║██╔══██║██║╚██╗██║██║   ██║              ║
    ║  ██║     ██║██║  ██║██║ ╚████║╚██████╔╝              ║
    ║  ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝               ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    time.sleep(1)
def main():
    global pressed_keys, last_note
    show_splash_screen()
    clear_screen()
    draw_keyboard()
    print(Style.BRIGHT + Fore.GREEN + "\nStart playing! Press ESC to exit." + Style.RESET_ALL)
    last_redraw = 0
    while True:
        current_time = time.time()
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
            if ord(key) == 27:
                print(Style.BRIGHT + Fore.GREEN + "\nThanks for playing!")
                break
            if key in PIANO_KEYS:
                threading.Thread(target=play_note, args=(PIANO_KEYS[key], key), daemon=True).start()
                if current_time - last_redraw > 0.1:
                    clear_screen()
                    draw_keyboard()
                    last_redraw = current_time
        time.sleep(0.05)
        time.sleep(0.01)
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Style.BRIGHT + Fore.GREEN + "\nThanks for playing!") 