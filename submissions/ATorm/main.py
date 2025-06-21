#!/usr/bin/env python3
import sys
from colors import Colors, show_cursor
from renderer import AtomRenderer
from menu import AtomMenu

def main():
    """Main application entry point"""
    try:
        # Initialize components
        renderer = AtomRenderer()
        menu = AtomMenu()
        
        # Check for command line args
        if len(sys.argv) > 1:
            try:
                atomic_number = int(sys.argv[1])
                if 1 <= atomic_number <= 118:
                    menu.run_direct_mode(renderer, atomic_number)
                else:
                    print(f"{Colors.ERROR}Atomic number must be between 1 and 118.{Colors.RESET}")
                    sys.exit(1)
            except ValueError:
                print(f"{Colors.ERROR}Invalid atomic number: {sys.argv[1]}{Colors.RESET}")
                sys.exit(1)
        else:
            # Run interactive mode
            menu.run_interactive_mode(renderer)
    
    except KeyboardInterrupt:
        show_cursor()
        print(f"\n\n{Colors.HIGHLIGHT}Program interrupted. Goodbye!{Colors.RESET}")
    except Exception as e:
        show_cursor()
        print(f"\n{Colors.ERROR}An error occurred: {e}{Colors.RESET}")
        sys.exit(1)
    finally:
        show_cursor()

if __name__ == "__main__":
    main()
