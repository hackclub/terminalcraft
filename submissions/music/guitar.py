import sys
import os
import time
import threading
import msvcrt
try:
    import winsound
    from colorama import init, Fore, Back, Style
    init(autoreset=True)  
except ImportError:
    print("This program requires the winsound and colorama modules.")
    print("Please install colorama using: pip install colorama")
    sys.exit(1)
CHORDS = {
    'a': [82.41, 110.00, 146.83, 196.00, 246.94, 329.63],  
    's': [82.41, 123.47, 164.81, 196.00, 246.94, 329.63],  
    'd': [110.00, 110.00, 146.83, 220.00, 277.18, 329.63], 
    'f': [110.00, 110.00, 164.81, 220.00, 277.18, 329.63], 
    'g': [146.83, 110.00, 146.83, 220.00, 293.66, 370.00], 
    'h': [146.83, 110.00, 146.83, 220.00, 293.66, 349.23], 
    'j': [131.87, 123.47, 164.81, 196.00, 261.63, 329.63], 
    'k': [131.87, 123.47, 164.81, 196.00, 233.08, 329.63], 
    'l': [82.41, 110.00, 123.47, 196.00, 246.94, 293.66],  
}
CHORD_NAMES = {
    'a': 'E minor',
    's': 'E major',
    'd': 'A minor',
    'f': 'A major',
    'g': 'D major',
    'h': 'D minor',
    'j': 'C major',
    'k': 'C minor',
    'l': 'E7',
}
STRUM_DURATION = 80  
CHORD_DURATION = 800
current_chord = None
strumming = False
last_chord = ""
def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')
def draw_guitar():
    """Draw a visual representation of a guitar."""
    print("\n" + Style.BRIGHT + Fore.CYAN + "=" * 70)
    print(Style.BRIGHT + Fore.WHITE + Back.BLUE + " CLI GUITAR - Press keys to play chords (press ESC to exit) ".center(70))
    print(Style.BRIGHT + Fore.CYAN + "=" * 70)
    neck_color = Fore.YELLOW
    fretboard_color = Fore.RED if strumming else Fore.YELLOW
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
                 {Style.BRIGHT}{Fore.WHITE}║  {Style.BRIGHT}{Fore.GREEN}Available Chords:                   {Style.BRIGHT}{Fore.WHITE}║
                 {Style.BRIGHT}{Fore.WHITE}║  {Style.BRIGHT}{Fore.YELLOW}A = Em   S = E    D = Am   F = A        {Style.BRIGHT}{Fore.WHITE}║
                 {Style.BRIGHT}{Fore.WHITE}║  {Style.BRIGHT}{Fore.YELLOW}G = D    H = Dm   J = C    K = Cm       {Style.BRIGHT}{Fore.WHITE}║
                 {Style.BRIGHT}{Fore.WHITE}║  {Style.BRIGHT}{Fore.YELLOW}L = E7                                   {Style.BRIGHT}{Fore.WHITE}║
                 {Style.BRIGHT}{Fore.WHITE}╚═══════════════════════════════════════╝
    """)
    print(Style.BRIGHT + Fore.CYAN + "-" * 70)
    print(Style.BRIGHT + Fore.YELLOW + "Last played chord: " + 
          Style.BRIGHT + Fore.WHITE + last_chord)
def play_single_string(freq):
    """Play a single guitar string."""
    try:
        freq_int = max(37, min(32767, int(freq)))
        winsound.Beep(freq_int, STRUM_DURATION)
    except Exception as e:
        try:
            winsound.Beep(500, 50)
        except:
            pass
def play_chord(frequencies, key):
    """Play a chord by playing each note in sequence."""
    global strumming, last_chord
    last_chord = f"{CHORD_NAMES[key]} ({key.upper()})"
    strumming = True
    clear_screen()
    draw_guitar()
    for freq in frequencies:
        threading.Thread(target=play_single_string, args=(freq,)).start()
        time.sleep(0.06)
    time.sleep(0.3)
    strumming = False
    clear_screen()
    draw_guitar()
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
    time.sleep(1)
def main():
    global current_chord, last_chord
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
            if key in CHORDS:
                current_chord = key
                threading.Thread(target=play_chord, args=(CHORDS[key], key)).start()
        time.sleep(0.01)
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Style.BRIGHT + Fore.GREEN + "\nThanks for playing!") 