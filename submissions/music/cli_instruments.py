import os
import sys
import importlib.util
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)  
except ImportError:
    print("This program requires the colorama module.")
    print("Please install colorama using: pip install colorama")
    sys.exit(1)
def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')
def check_module_exists(module_name):
    """Check if a Python module exists in the current directory."""
    return os.path.isfile(f"{module_name}.py")
def load_and_run_module(module_name):
    """Dynamically load and run a Python module."""
    spec = importlib.util.spec_from_file_location(module_name, f"{module_name}.py")
    if spec is None:
        print(f"Error: Could not load the {module_name} module.")
        return
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        print(f"Error: Could not load the {module_name} module (no loader).")
        return
    spec.loader.exec_module(module)
    if hasattr(module, 'main'):
        module.main()
    else:
        print(f"Error: The {module_name} module does not have a main() function.")
def display_menu():
    """Display the main menu of available instruments."""
    clear_screen()
    print(Style.BRIGHT + Fore.YELLOW + """
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                                                                          ║
    ║   ██████╗██╗     ██╗    ██╗███╗   ██╗███████╗████████╗██████╗ ██╗   ██╗ ║
    ║  ██╔════╝██║     ██║    ██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██║   ██║ ║
    ║  ██║     ██║     ██║    ██║██╔██╗ ██║███████╗   ██║   ██████╔╝██║   ██║ ║
    ║  ██║     ██║     ██║    ██║██║╚██╗██║╚════██║   ██║   ██╔══██╗██║   ██║ ║
    ║  ╚██████╗███████╗╚██████╔╝██║ ╚████║███████║   ██║   ██║  ██║╚██████╔╝ ║
    ║   ╚═════╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝  ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """ + Style.RESET_ALL)
    print(Style.BRIGHT + Fore.CYAN + "=" * 70)
    print(Style.BRIGHT + Fore.WHITE + Back.BLUE + " VIRTUAL INSTRUMENTS IN YOUR TERMINAL ".center(70) + Style.RESET_ALL)
    print(Style.BRIGHT + Fore.CYAN + "=" * 70)
    print("\n" + Style.BRIGHT + Fore.GREEN + " Select an instrument to play:" + Style.RESET_ALL + "\n")
    instruments = [
        ("1", "Piano", "piano", "Play a virtual piano keyboard with realistic notes"),
        ("2", "Guitar", "guitar", "Play guitar strings with authentic string sounds"),
        ("3", "Drums", "drums", "Play a virtual drum kit with realistic percussion"),
        ("q", "Quit", None, "Exit the program")
    ]
    for key, name, module, description in instruments:
        if module is None or check_module_exists(module):
            if key == 'q':
                print(Style.BRIGHT + Fore.RED + f"  [{key}] " + 
                      Style.BRIGHT + Fore.WHITE + f"{name} - {description}")
            else:
                print(Style.BRIGHT + Fore.BLUE + f"  [{key}] " + 
                      Style.BRIGHT + Fore.YELLOW + f"{name}" + 
                      Style.RESET_ALL + f" - {description}")
        else:
            print(Style.BRIGHT + Fore.BLUE + f"  [{key}] " + 
                  Style.BRIGHT + Fore.YELLOW + f"{name}" + 
                  Style.BRIGHT + Fore.RED + " - [NOT AVAILABLE]")
    print("\n" + Style.BRIGHT + Fore.CYAN + "-" * 70 + Style.RESET_ALL)
def main():
    """Main function to run the CLI instruments program."""
    try:
        import audio
        print(Style.BRIGHT + Fore.GREEN + "🎵 High Quality Audio Loaded!" + Style.RESET_ALL)
        print(Style.BRIGHT + Fore.CYAN + "   → Piano: Realistic string harmonics" + Style.RESET_ALL)
        print(Style.BRIGHT + Fore.CYAN + "   → Guitar: String physics modeling" + Style.RESET_ALL) 
        print(Style.BRIGHT + Fore.CYAN + "   → Drums: Real drum sounds" + Style.RESET_ALL)
    except ImportError:
        try:
            from audio_fallback import ADVANCED_AUDIO
            if ADVANCED_AUDIO:
                print(Style.BRIGHT + Fore.GREEN + "✓ Basic audio loaded!" + Style.RESET_ALL)
            else:
                print(Style.BRIGHT + Fore.YELLOW + "⚠ Using simple beeps. Install numpy and pygame for better sound." + Style.RESET_ALL)
        except:
            print(Style.BRIGHT + Fore.RED + "⚠ Audio system unavailable." + Style.RESET_ALL)
    print()
    while True:
        display_menu()
        choice = input(Style.BRIGHT + Fore.GREEN + "\nEnter your choice: " + Style.RESET_ALL).lower()
        if choice == '1':
            if check_module_exists("piano"):
                load_and_run_module("piano")
            else:
                print(Style.BRIGHT + Fore.RED + "Piano module not found. Please make sure piano.py exists.")
                input(Style.BRIGHT + Fore.YELLOW + "Press Enter to continue..." + Style.RESET_ALL)
        elif choice == '2':
            if check_module_exists("guitar"):
                load_and_run_module("guitar")
            else:
                print(Style.BRIGHT + Fore.RED + "Guitar module not found. Please make sure guitar.py exists.")
                input(Style.BRIGHT + Fore.YELLOW + "Press Enter to continue..." + Style.RESET_ALL)
        elif choice == '3':
            if check_module_exists("drums"):
                load_and_run_module("drums")
            else:
                print(Style.BRIGHT + Fore.RED + "Drums module not found. Please make sure drums.py exists.")
                input(Style.BRIGHT + Fore.YELLOW + "Press Enter to continue..." + Style.RESET_ALL)
        elif choice == 'q':
            print(Style.BRIGHT + Fore.GREEN + "\nThanks for playing CLI Instruments!" + Style.RESET_ALL)
            break
        else:
            print(Style.BRIGHT + Fore.RED + "\nInvalid choice. Please try again.")
            input(Style.BRIGHT + Fore.YELLOW + "Press Enter to continue..." + Style.RESET_ALL)
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Style.BRIGHT + Fore.GREEN + "\nThanks for playing CLI Instruments!" + Style.RESET_ALL) 