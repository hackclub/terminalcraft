import sys
import os
import time
import threading
import msvcrt
import random
try:
    import winsound
    from colorama import init, Fore, Back, Style
    init(autoreset=True)  
except ImportError:
    print("This program requires the winsound and colorama modules.")
    print("Please install colorama using: pip install colorama")
    sys.exit(1)
DRUMS = {
    'a': [(60, 150), (40, 100)],                   
    's': [(1200, 20), (800, 40), (400, 60)],       
    'd': [(2000, 10), (1800, 5)],                  
    'f': [(1800, 80), (1600, 60), (1400, 40)],     
    'g': [(500, 70), (450, 50), (400, 30)],        
    'h': [(400, 70), (350, 50), (300, 30)],        
    'j': [(300, 70), (250, 50), (200, 30)],        
    'k': [(1500, 100), (1200, 80), (900, 60), (600, 40)],  
    'l': [(1000, 70), (800, 60), (600, 50)],       
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
def play_drum_sound(freq, duration):
    """Play a single drum sound component."""
    try:
        freq_int = max(37, min(32767, int(freq)))
        winsound.Beep(freq_int, duration)
    except Exception as e:
        pass
def play_drum(sound_components, key):
    """Play a drum sound with the given frequency and duration."""
    global active_drums, last_drum, redraw_needed
    active_drums[key] = time.time()
    last_drum = f"{DRUM_NAMES[key]} ({key.upper()})"
    redraw_needed = True
    for freq, duration in sound_components:
        freq_variation = random.uniform(0.98, 1.02)
        threading.Thread(target=play_drum_sound, 
                        args=(freq * freq_variation, duration)).start()
        time.sleep(0.01)
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
        if redraw_needed and current_time - last_redraw_time > 0.1:
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
                threading.Thread(target=play_drum, args=(DRUMS[key], key)).start()
        time.sleep(0.01)
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Style.BRIGHT + Fore.GREEN + "\nThanks for playing!") 