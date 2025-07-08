#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
try:
    import colorama
except ImportError:
    print("Notice: The 'colorama' package is not installed.")
    print("For the best visual experience with colors, please install it:")
    print("pip install colorama")
    print("Continuing without colors...\n")
try:
    from src.game import Game
except ImportError:
    print("Error: Could not import game modules.")
    print("Make sure you're running the game from the correct directory.")
    sys.exit(1)
def main():
    """Main entry point for the game."""
    print("Starting One Piece: Escape from Impel Down...\n")
    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        print("\nGame terminated by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()
        print("\nGame terminated unexpectedly.")
    print("\nThank you for playing!")
if __name__ == "__main__":
    main() 