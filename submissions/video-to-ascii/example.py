#!/usr/bin/env python3
"""
Example script to demonstrate the video_to_ascii.py program
This script shows how to use the video_to_ascii module programmatically
instead of through the command line interface. It demonstrates the
enhanced features like color support, different character sets,
and playback options.
"""
import os
import sys
import time
import argparse
from video_to_ascii import play_video_as_ascii, detect_terminal_size
def show_demo_menu():
    """
    Display a menu of demo options
    """
    print("\n===== ASCII Video Player Demo =====\n")
    print("1. Basic playback (auto-sized)")
    print("2. Color mode")
    print("3. Detailed character set")
    print("4. Inverted character set")
    print("5. Loop mode")
    print("6. Reverse playback")
    print("7. Preloaded mode (smoother playback)")
    print("8. Full featured demo (color + detailed + preloaded)")
    print("9. Custom settings")
    print("0. Exit")
    choice = input("\nSelect a demo option (0-9): ")
    return choice
def get_video_path():
    """
    Get video path from command line or find one in the current directory
    """
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        video_files = [f for f in os.listdir('.') if f.endswith(('.mp4', '.avi', '.mkv', '.mov'))]
        if not video_files:
            print("Error: No video files found in the current directory")
            print("Please provide a video path as a command line argument:")
            print("python example.py path/to/your/video.mp4")
            return None
        video_path = video_files[0]
        print(f"Using video file: {video_path}")
    if not os.path.isfile(video_path):
        print(f"Error: Video file '{video_path}' does not exist")
        return None
    return video_path
def custom_settings(video_path):
    """
    Allow user to input custom settings
    """
    term_width, term_height = detect_terminal_size()
    try:
        width = int(input(f"Width (default: {term_width}): ") or term_width)
        height = int(input(f"Height (default: {term_height}): ") or term_height)
        fps = int(input("FPS cap (default: 30): ") or 30)
        print("\nCharacter set options:")
        print("1. Standard")
        print("2. Detailed")
        print("3. Inverted")
        char_choice = input("Select character set (default: 1): ") or "1"
        char_set = {"1": "standard", "2": "detailed", "3": "inverted"}.get(char_choice, "standard")
        color = input("Enable color? (y/n, default: n): ").lower() == 'y'
        preload = input("Preload frames? (y/n, default: n): ").lower() == 'y'
        loop = input("Loop playback? (y/n, default: n): ").lower() == 'y'
        reverse = input("Play in reverse? (y/n, default: n): ").lower() == 'y'
        print("\nStarting playback with custom settings...")
        time.sleep(1)
        play_video_as_ascii(
            video_path, width, height, fps, char_set, color, preload, loop, reverse
        )
    except ValueError:
        print("Invalid input. Using default values.")
def main():
    video_path = get_video_path()
    if not video_path:
        return
    while True:
        choice = show_demo_menu()
        term_width, term_height = detect_terminal_size()
        if choice == "0":
            print("Exiting demo.")
            break
        elif choice == "1":
            play_video_as_ascii(video_path, term_width, term_height, fps_cap=30)
        elif choice == "2":
            play_video_as_ascii(video_path, term_width, term_height, fps_cap=30, colored=True)
        elif choice == "3":
            play_video_as_ascii(video_path, term_width, term_height, fps_cap=30, char_set="detailed")
        elif choice == "4":
            play_video_as_ascii(video_path, term_width, term_height, fps_cap=30, char_set="inverted")
        elif choice == "5":
            play_video_as_ascii(video_path, term_width, term_height, fps_cap=30, loop=True)
        elif choice == "6":
            play_video_as_ascii(video_path, term_width, term_height, fps_cap=30, preload=True, reverse=True)
        elif choice == "7":
            play_video_as_ascii(video_path, term_width, term_height, fps_cap=30, preload=True)
        elif choice == "8":
            play_video_as_ascii(
                video_path, term_width, term_height, fps_cap=30, 
                char_set="detailed", colored=True, preload=True
            )
        elif choice == "9":
            custom_settings(video_path)
        else:
            print("Invalid choice. Please try again.")
        input("\nPress Enter to return to menu...")
        os.system('cls' if os.name == 'nt' else 'clear')
if __name__ == "__main__":
    main()