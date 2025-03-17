"""
Entry script to run the Veritaminal game.

This standalone script allows you to run the game without installing it as a package.
"""

import os
import sys
import argparse
from colorama import init, Fore, Style, Back

# Initialize colorama for welcome message
init(autoreset=True, convert=True, strip=False, wrap=True)

# Add the project root directory to Python path to allow importing game modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main function from the game package
from game.main import main

def parse_args():
    """Parse command-line arguments for the game launcher."""
    parser = argparse.ArgumentParser(
        description='Veritaminal: A Document Verification Game with Memory and Narrative',
        epilog='Example: python run_game.py --debug'
    )
    
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--load', type=str, help='Load a saved game from a specific file path')
    
    return parser.parse_args()

def print_welcome():
    """Print a welcome message with instructions."""
    print("\n" + Fore.BLUE + "="*80 + Style.RESET_ALL)
    print(Fore.YELLOW + Back.BLUE + " VERITAMINAL: Enhanced Edition ".center(80, '=') + Style.RESET_ALL)
    print(Fore.BLUE + "="*80 + Style.RESET_ALL)
    print("\n" + Fore.WHITE + "Welcome to the enhanced version of Veritaminal!" + Style.RESET_ALL)
    print(Fore.WHITE + "This version includes:" + Style.RESET_ALL)
    print(Fore.CYAN + "- Border setting selection with tailored document rules" + Style.RESET_ALL)
    print(Fore.CYAN + "- AI judgment system that evaluates documents based on context" + Style.RESET_ALL)
    print(Fore.CYAN + "- Memory system that stores your decisions and creates a continuous story" + Style.RESET_ALL)
    print(Fore.CYAN + "- Save/load functionality to continue your career across sessions" + Style.RESET_ALL)
    print("\n" + Fore.GREEN + "Starting game...\n" + Style.RESET_ALL)

if __name__ == "__main__":
    # Display welcome message
    print_welcome()
    
    # Set up command line arguments to forward to the main game
    args = parse_args()
    
    # Convert args to list format for sys.argv
    sys_args = []
    if args.debug:
        sys_args.append('--debug')
    if args.load:
        sys_args.append('--load')
        sys_args.append(args.load)
    
    # Update sys.argv to pass arguments to main()
    sys.argv[1:] = sys_args
    
    # Run the game
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nGame interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        print("See veritaminal.log for details.")
        sys.exit(1)
