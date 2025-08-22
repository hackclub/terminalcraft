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
    from audio_fallback import audio_engine
    AUDIO_AVAILABLE = False
    AUDIO_TYPE = "Fallback Audio (Fast)"
    def play_guitar_note(frequency, fret=0, string_num=1, duration=2.0):
        """Play guitar note using fallback audio for instant response"""
        audio_engine.play_guitar_note(frequency)
except ImportError:
    try:
        from audio import get_ultra_realistic_guitar_sample
        AUDIO_AVAILABLE = True
        AUDIO_TYPE = "High Quality Audio"
        def play_guitar_note(frequency, fret=0, string_num=1, duration=2.0):
            """Play guitar note using high quality synthesis"""
            sample = get_ultra_realistic_guitar_sample(frequency, duration, fret, string_num)
            sample.play()
    except ImportError:
        print("No audio system available")
        def play_guitar_note(frequency, fret=0, string_num=1, duration=2.0):
            pass
GUITAR_NOTES = {
    'a': 82.41,   
    's': 110.00,  
    'd': 146.83,  
    'f': 196.00,  
    'g': 246.94,  
    'h': 329.63,  
    'j': 73.42,   
    'k': 98.00,   
    'l': 123.47,  
}
NOTE_NAMES = {
    'a': 'Low E',
    's': 'A',
    'd': 'D', 
    'f': 'G',
    'g': 'B',
    'h': 'High E',
    'j': 'Low D',
    'k': 'Low G',
    'l': 'Low B',
}
STRUM_DURATION = 80  
CHORD_DURATION = 800
current_chord = None
last_chord = ""
def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')
def draw_guitar():
    """Draw a visual representation of a guitar."""
    print("\n" + Style.BRIGHT + Fore.CYAN + "=" * 70)
    print(Style.BRIGHT + Fore.WHITE + Back.BLUE + " CLI GUITAR - Press keys to play single notes (press ESC to exit) ".center(70))
    print(Style.BRIGHT + Fore.CYAN + "=" * 70)
    neck_color = Fore.YELLOW
    fretboard_color = Fore.YELLOW  
    string_color = Fore.WHITE
    print(f"""
    {Style.BRIGHT}{neck_color}    ⬤════════╗
    {Style.BRIGHT}{neck_color}    ║        ║
    {Style.BRIGHT}{neck_color}    ║        ║{fretboard_color}╔═══════════════════════════════════════════════╗
    {Style.BRIGHT}{neck_color}    ║        {fretboard_color}║ {string_color}═══════════════════════════════════════════════ ║
    {Style.BRIGHT}{neck_color}    ║        {fretboard_color}║ {string_color}═══════════════════════════════════════════════ ║
    {Style.BRIGHT}{neck_color}    ║        {fretboard_color}║ {string_color}═══════════════════════════════════════════════ ║
    {Style.BRIGHT}{neck_color}    ║        {fretboard_color}║ {string_color}═══════════════════════════════════════════════ ║
    {Style.BRIGHT}{neck_color}    ║        {fretboard_color}║ {string_color}═══════════════════════════════════════════════ ║
    {Style.BRIGHT}{neck_color}    ║        {fretboard_color}║ {string_color}═══════════════════════════════════════════════ ║
    {Style.BRIGHT}{neck_color}    ║        {fretboard_color}╚═══════════════════════════════════════════════╝
    {Style.BRIGHT}{neck_color}    ║
    {Style.BRIGHT}{neck_color}    ╚══════════╗
                 ║
                 ║{Style.BRIGHT}{Fore.WHITE}╔═══════════════════════════════════════╗
                 {Style.BRIGHT}{Fore.WHITE}║                                       ║
                 {Style.BRIGHT}{Fore.WHITE}║  {Style.BRIGHT}{Fore.GREEN}Available Guitar Strings:           {Style.BRIGHT}{Fore.WHITE}║
                 {Style.BRIGHT}{Fore.WHITE}║  {Style.BRIGHT}{Fore.YELLOW}A = Low E    S = A     D = D     F = G   {Style.BRIGHT}{Fore.WHITE}║
                 {Style.BRIGHT}{Fore.WHITE}║  {Style.BRIGHT}{Fore.YELLOW}G = B        H = High E          {Style.BRIGHT}{Fore.WHITE}║
                 {Style.BRIGHT}{Fore.WHITE}║  {Style.BRIGHT}{Fore.YELLOW}J = Low D    K = Low G   L = Low B     {Style.BRIGHT}{Fore.WHITE}║
                 {Style.BRIGHT}{Fore.WHITE}╚═══════════════════════════════════════╝
    """)
    print(Style.BRIGHT + Fore.CYAN + "-" * 70)
    print(Style.BRIGHT + Fore.YELLOW + "Last played note: " + 
          Style.BRIGHT + Fore.WHITE + last_chord)
def play_note(frequency, key):
    """Play a single guitar note - immediate playback."""
    play_guitar_note(frequency, duration=1.0)
def show_splash_screen():
    """Show a splash screen with the guitar logo."""
    clear_screen()
    print(Style.BRIGHT + Fore.YELLOW + """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║   ██████╗ ██╗   ██╗██╗████████╗ █████╗ ██████╗       ║
    ║  ██╔════╝ ██║   ██║██║╚══██╔══╝██╔══██╗██╔══██╗      ║
    ║  ██║  ███╗██║   ██║██║   ██║   ███████║██████╔╝      ║
    ║  ██║   ██║██║   ██║██║   ██║   ██╔══██║██╔══██╗      ║
    ║  ╚██████╔╝╚██████╔╝██║   ██║   ██║  ██║██║  ██║      ║
    ║   ╚═════╝  ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝      ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)
def main():
    show_splash_screen()
    clear_screen()
    draw_guitar()
    print(Style.BRIGHT + Fore.GREEN + "\nStart playing! Press ESC to exit." + Style.RESET_ALL)
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
            if ord(key) == 27:
                print(Style.BRIGHT + Fore.GREEN + "\nThanks for playing!")
                break
            if key in GUITAR_NOTES:
                play_note(GUITAR_NOTES[key], key)
        time.sleep(0.001)  
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Style.BRIGHT + Fore.GREEN + "\nThanks for playing!") 