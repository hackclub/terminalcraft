import sys
import os
import time
import threading
import msvcrt
import random
import math
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)  
except ImportError as e:
    print("This program requires the colorama module.")
    print("Please install colorama using: pip install colorama")
    print(f"Error: {e}")
    sys.exit(1)
try:
    from audio import get_ultra_realistic_drum_sample
    AUDIO_AVAILABLE = True
    AUDIO_TYPE = "High Quality Audio"
    def play_drum_hit(drum_type, velocity=0.8, duration=1.0):
        """Play drum hit using high quality synthesis"""
        sample = get_ultra_realistic_drum_sample(drum_type, duration, velocity)
        sample.play()
except ImportError:
    from audio_fallback import audio_engine
    AUDIO_AVAILABLE = False
    AUDIO_TYPE = "Fallback Audio"
    def play_drum_hit(drum_type, velocity=0.8, duration=1.0):
        """Play drum hit using fallback audio"""
        audio_engine.play_drum_hit(drum_type, duration)
DRUMS = {
    'a': 'kick',      
    's': 'snare',     
    'd': 'hihat_closed',  
    'f': 'hihat_open',    
    'g': 'tom1',      
    'h': 'tom2',      
    'j': 'tom3',      
    'k': 'crash',     
    'l': 'ride',      
}
DRUM_SOUNDS = {
    'kick': {
        'base_freq': 60,
        'attack_freq': 80,
        'decay_freq': 45,
        'duration': 250,
        'has_thump': True
    },
    'snare': {
        'base_freq': 200,
        'attack_freq': 300,
        'decay_freq': 150,
        'duration': 180,
        'has_rattle': True
    },
    'hihat_closed': {
        'base_freq': 8000,
        'attack_freq': 12000,
        'decay_freq': 6000,
        'duration': 80,
        'has_shimmer': True
    },
    'hihat_open': {
        'base_freq': 6000,
        'attack_freq': 9000,
        'decay_freq': 4000,
        'duration': 300,
        'has_shimmer': True
    },
    'tom1': {
        'base_freq': 300,
        'attack_freq': 350,
        'decay_freq': 250,
        'duration': 220,
        'has_thump': False
    },
    'tom2': {
        'base_freq': 200,
        'attack_freq': 240,
        'decay_freq': 160,
        'duration': 280,
        'has_thump': False
    },
    'tom3': {
        'base_freq': 150,
        'attack_freq': 180,
        'decay_freq': 120,
        'duration': 350,
        'has_thump': False
    },
    'crash': {
        'base_freq': 4000,
        'attack_freq': 6000,
        'decay_freq': 3000,
        'duration': 800,
        'has_shimmer': True
    },
    'ride': {
        'base_freq': 3000,
        'attack_freq': 4000,
        'decay_freq': 2500,
        'duration': 400,
        'has_shimmer': True
    }
}
DRUM_NAMES = {
    'a': 'Kick',
    's': 'Snare',
    'd': 'Hi-hat (closed)',
    'f': 'Hi-hat (open)',
    'g': 'Tom 1',
    'h': 'Tom 2',
    'j': 'Tom 3',
    'k': 'Crash',
    'l': 'Ride',
}
active_drums = {}
last_drum = ""
redraw_needed = True
currently_playing = False  
def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')
def draw_drums():
    """Draw a visual representation of a drum kit."""
    print("\n" + Style.BRIGHT + Fore.CYAN + "=" * 70)
    print(Style.BRIGHT + Fore.WHITE + Back.BLUE + " CLI DRUMS - Press keys to play drums (press ESC to exit) ".center(70))
    print(Style.BRIGHT + Fore.CYAN + "=" * 70)
    cymbal_color = Fore.YELLOW
    tom_color = Fore.RED
    hihat_color = Fore.CYAN
    snare_color = Fore.WHITE
    kick_color = Fore.MAGENTA
    crash_active = 'k' in active_drums and time.time() - active_drums['k'] < 0.3
    ride_active = 'l' in active_drums and time.time() - active_drums['l'] < 0.3
    tom1_active = 'g' in active_drums and time.time() - active_drums['g'] < 0.3
    tom2_active = 'h' in active_drums and time.time() - active_drums['h'] < 0.3
    tom3_active = 'j' in active_drums and time.time() - active_drums['j'] < 0.3
    hihat_active = ('d' in active_drums and time.time() - active_drums['d'] < 0.2) or \
                  ('f' in active_drums and time.time() - active_drums['f'] < 0.2)
    snare_active = 's' in active_drums and time.time() - active_drums['s'] < 0.2
    kick_active = 'a' in active_drums and time.time() - active_drums['a'] < 0.2
    crash_style = Style.BRIGHT + (Back.WHITE if crash_active else "")
    ride_style = Style.BRIGHT + (Back.WHITE if ride_active else "")
    tom1_style = Style.BRIGHT + (Back.WHITE if tom1_active else "")
    tom2_style = Style.BRIGHT + (Back.WHITE if tom2_active else "")
    tom3_style = Style.BRIGHT + (Back.WHITE if tom3_active else "")
    hihat_style = Style.BRIGHT + (Back.WHITE if hihat_active else "")
    snare_style = Style.BRIGHT + (Back.WHITE if snare_active else "")
    kick_style = Style.BRIGHT + (Back.WHITE if kick_active else "")
    print(f"""
    {crash_style}{cymbal_color}     ╭───────╮{Style.RESET_ALL} K                      {ride_style}{cymbal_color}╭───────╮{Style.RESET_ALL} L
    {crash_style}{cymbal_color}    ╱         ╲{Style.RESET_ALL}                      {ride_style}{cymbal_color}╱         ╲{Style.RESET_ALL}
    {crash_style}{cymbal_color}   ╱           ╲{Style.RESET_ALL}                    {ride_style}{cymbal_color}╱           ╲{Style.RESET_ALL}
    {crash_style}{cymbal_color}  ╱             ╲{Style.RESET_ALL}                  {ride_style}{cymbal_color}╱             ╲{Style.RESET_ALL}
    {crash_style}{cymbal_color} ╱               ╲{Style.RESET_ALL}                {ride_style}{cymbal_color}╱               ╲{Style.RESET_ALL}
          │                                 │
          │                                 │
          │       {tom1_style}{tom_color}╭───────╮{Style.RESET_ALL} G       {tom2_style}{tom_color}╭───────╮{Style.RESET_ALL} H
          │       {tom1_style}{tom_color}│       │{Style.RESET_ALL}         {tom2_style}{tom_color}│       │{Style.RESET_ALL}
          │       {tom1_style}{tom_color}│       │{Style.RESET_ALL}         {tom2_style}{tom_color}│       │{Style.RESET_ALL}
          │       {tom1_style}{tom_color}╰───────╯{Style.RESET_ALL}         {tom2_style}{tom_color}╰───────╯{Style.RESET_ALL}
          │            │                     │
          │            │                     │
          │            │     {tom3_style}{tom_color}╭───────╮{Style.RESET_ALL} J
          │            │     {tom3_style}{tom_color}│       │{Style.RESET_ALL}
          │            │     {tom3_style}{tom_color}│       │{Style.RESET_ALL}
          │            │     {tom3_style}{tom_color}╰───────╯{Style.RESET_ALL}
          │            │         │
    {hihat_style}{hihat_color}╭───────╮{Style.RESET_ALL} D/F  │         │       {snare_style}{snare_color}╭───────╮{Style.RESET_ALL} S
    {hihat_style}{hihat_color}│       │{Style.RESET_ALL}      │         │       {snare_style}{snare_color}│       │{Style.RESET_ALL}
    {hihat_style}{hihat_color}│       │{Style.RESET_ALL}      │         │       {snare_style}{snare_color}│       │{Style.RESET_ALL}
    {hihat_style}{hihat_color}╰───────╯{Style.RESET_ALL}      │         │       {snare_style}{snare_color}╰───────╯{Style.RESET_ALL}
          │            │         │            │
          │            │         │            │
          └────────────┴─────────┴────────────┘
                            │
                      {kick_style}{kick_color}╭───────╮{Style.RESET_ALL} A
                      {kick_style}{kick_color}│       │{Style.RESET_ALL}
                      {kick_style}{kick_color}│       │{Style.RESET_ALL}
                      {kick_style}{kick_color}╰───────╯{Style.RESET_ALL}
    """)
    print(Style.BRIGHT + Fore.CYAN + "-" * 70)
    print(Style.BRIGHT + Fore.YELLOW + "Last played drum: " + 
          Style.BRIGHT + Fore.WHITE + last_drum)
def play_drum(drum_type, key):
    """Play a drum sound - prevent overlapping hits."""
    global active_drums, last_drum, redraw_needed, currently_playing
    if currently_playing:
        return
    active_drums[key] = time.time()
    last_drum = f"{DRUM_NAMES[key]} ({key.upper()})"
    redraw_needed = True
    currently_playing = True
    velocity = 0.6 + random.uniform(0, 0.4)  
    durations = {
        'kick': 1.2,
        'snare': 0.8,
        'hihat_closed': 0.3,
        'hihat_open': 1.5,
        'tom1': 1.0,
        'tom2': 1.1,
        'tom3': 1.3,
        'crash': 3.0,
        'ride': 2.0
    }
    duration = durations.get(drum_type, 1.0)
    play_drum_hit(drum_type, velocity=velocity, duration=duration)
    def reset_playing():
        global currently_playing
        time.sleep(0.3)  
        currently_playing = False
    threading.Thread(target=reset_playing, daemon=True).start()
def show_splash_screen():
    """Show a splash screen with the drums logo."""
    clear_screen()
    print(Style.BRIGHT + Fore.YELLOW + """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║   ██████╗ ██████╗ ██╗   ██╗███╗   ███╗███████╗       ║
    ║   ██╔══██╗██╔══██╗██║   ██║████╗ ████║██╔════╝       ║
    ║   ██║  ██║██████╔╝██║   ██║██╔████╔██║███████╗       ║
    ║   ██║  ██║██╔══██╗██║   ██║██║╚██╔╝██║╚════██║       ║
    ║   ██████╔╝██║  ██║╚██████╔╝██║ ╚═╝ ██║███████║       ║
    ║   ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝       ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    time.sleep(1)
def main():
    global redraw_needed, last_drum
    show_splash_screen()
    clear_screen()
    draw_drums()
    print(Style.BRIGHT + Fore.GREEN + "\nStart playing! Press ESC to exit." + Style.RESET_ALL)
    last_redraw_time = 0
    while True:
        current_time = time.time()        
        if redraw_needed and current_time - last_redraw_time > 0.15:  
            clear_screen()
            draw_drums()
            redraw_needed = False
            last_redraw_time = current_time
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
            if ord(key) == 27:
                print(Style.BRIGHT + Fore.GREEN + "\nThanks for playing!")
                break
            if key in DRUMS:
                threading.Thread(target=play_drum, args=(DRUMS[key], key), daemon=True).start()
        time.sleep(0.05)  
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Style.BRIGHT + Fore.GREEN + "\nThanks for playing!")