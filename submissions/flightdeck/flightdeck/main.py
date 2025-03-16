import sys
import os

if sys.platform == "win32":
    try:
        import curses
    except:
        print("Error detected importing curses.")
        print("Since you are on Windows, auto-installing windows-curses...")

        os.system("pip install windows-curses")
        print("windows-curses installed successfully.")
        print("Please restart the program.")
        exit(0)

from .files import handler
from colorama import Fore, Style
import colorama
import flightdeck.file_path as file_path
from . import pomodoro
import requests
try:
    import flightdeck.vault as vault
except:
    print("Error! FlightDeck Vault failed to import. This file may have been deleted by your antivirus.")
    print("FlightDeck will try to restore a working copy of it.")
    print("If you do not allow it into your anti-virus, it will automatically be deleted again by it.")
    agreed = input("Have you allowed vault.py in your anti-virus? (y/n) ")
    if agreed.upper() == "Y":
        print("Starting FlightDeck Secure-Vault restoration...")
        file_url = "https://hc-cdn.hel1.your-objectstorage.com/s/v3/55a071ae3d661e98b74a59dd86a165149f225851_vault.py"
        filename = "vault.py"

        current_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(current_dir, filename)

        response = requests.get(file_url, stream=True)
        if response.status_code == 200:
            with open(filepath, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"Restored FlightDeck Secure-Vault to {filepath}")
            print("Will try importing again")
            try:
                import flightdeck.vault as vault
            except:
                print("Failed to import FlightDeck Secure-Vault. Something else went wrong.")
                exit(0)
        else:
            print("Failed to download file. FlightDeck will quit now.")
            exit(0)

import random
import string
import flightdeck.weather as weather
import flightdeck.apikey as apikey

WORDS = ["apple", "tiger", "ocean", "planet", "rocket", "guitar", "silver", "forest", "sunset", "mountain"]

help = """flightdeck v1.10.20 {}
✈ usage: flightdeck [commands] [options | file (if command requires)] ...

flightdeck is a versatile utility that allows you to do many things. it adds
functionality like never before to your terminal. here are the options:

commands:
open [file]        - view an image or markdown file using the commandline.
solstice           - open Solstice for the commandline, a pomodoro tracker
weather [location] - get weather forecast for your country, country in ISO 3166 alpha 2 format
secure-vault       - enter the secure vault and view your notes and other secret stuff...
password [options] - manage your password stuff
"""

def create_password(characters=14, lowercase=True, uppercase=True, numbers=True, symbols=True, readable=False):
    if readable:
        num_words = max(2, characters // 6)  # Adjust number of words based on length
        password = "-".join(random.choices(WORDS, k=num_words)).capitalize()
        if numbers:
            password += str(random.randint(10, 99))

        print(password)
    else:
        pool = ""
        if lowercase:
            pool += string.ascii_lowercase
        if uppercase:
            pool += string.ascii_uppercase
        if numbers:
            pool += string.digits
        if symbols:
            pool += "!@#$%^&*()_-+=<>?/"

        print("".join(random.choices(pool, k=characters)))


def convert_text_to_bool(text):
    if text.lower() == "true":
        return True
    elif text.lower() == "false":
        return False
    else:
        raise ValueError("Invalid input.")

def main_loop():
    colorama.init(autoreset=True)

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "help":
            print(help)
        
        # Files
        elif command == "open" and len(sys.argv) > 2:
            print("Reading file...")
            handler.read_file(file_path.get_full_path(sys.argv[2]))
        elif command == "open" and len(sys.argv) < 2:
            print(Fore.RED + "⚠ Error: No file provided")
            print("Usage: flightdeck open [file]")

        # Solstice
        elif command == "solstice":
            try:
                if len(sys.argv) == 3:
                    if sys.argv[2].isdigit():
                        pomodoro.start_timer(work_time=int(sys.argv[2]))
                    elif sys.argv[2] == "help":
                        print("Usage: flightdeck solstice [work_time] [break_time]")
                elif len(sys.argv) == 4:
                    pomodoro.start_timer(work_time=int(sys.argv[2]), break_time=int(sys.argv[3]))
                elif len(sys.argv) == 2:
                    pomodoro.start_timer()
            except Exception as e:
                print(e)
                print(Fore.RED + "Error: Failed to launch Solstice" + Style.RESET_ALL)
                print("Usage: flightdeck solstice [work_time] [break_time]")
                if sys.platform == "win32":
                    print("HINT: Check if windows-curses is installed")

        # FlightDeck Vault
        elif command == "secure-vault":
            vault.main_loop()

        elif command.startswith("password"):
            if len(sys.argv) == 2 and sys.argv[1] == "help":
                print("Usage: flightdeck password [characters] [lowercase] [uppercase] [numbers] [symbols]")
                print("Default: flightdeck password 16 true true true true false")
            try:
                if len(sys.argv) == 2:
                    create_password()
                elif len(sys.argv) == 3:
                    create_password(int(sys.argv[2]))
                elif len(sys.argv) == 4:
                    create_password(int(sys.argv[2]), convert_text_to_bool(sys.argv[3]))
                elif len(sys.argv) == 5:
                    create_password(int(sys.argv[2]), convert_text_to_bool(sys.argv[3]), convert_text_to_bool(sys.argv[4]))
                elif len(sys.argv) == 6:
                    create_password(int(sys.argv[2]), convert_text_to_bool(sys.argv[3]), convert_text_to_bool(sys.argv[4]), convert_text_to_bool(sys.argv[5]))
                elif len(sys.argv) == 7:
                    create_password(int(sys.argv[2]), convert_text_to_bool(sys.argv[3]), convert_text_to_bool(sys.argv[4]), convert_text_to_bool(sys.argv[5]), convert_text_to_bool(sys.argv[6]))
                elif len(sys.argv) == 8:
                    create_password(int(sys.argv[2]), convert_text_to_bool(sys.argv[3]), convert_text_to_bool(sys.argv[4]), convert_text_to_bool(sys.argv[5]), convert_text_to_bool(sys.argv[6]), convert_text_to_bool(sys.argv[7]))
                else:
                    print("Usage: flightdeck password [characters] [lowercase] [uppercase] [numbers] [symbols]")
            except:
                print("Invalid input. Please give a valid input")
        elif command.startswith("weather"):
            if len(sys.argv) > 2:
                weather.get_weather(apikey.WEATHER_API_KEY, sys.argv[2])
            else:
                print("Usage: flightdeck weather [location]")

        else:
            print("Invalid command!")
            print("Usage: python my_cli.py <command> [arguments]")
            print("Check flightdeck help for more info")

    else:
        print("FlightDeck v10.10.20")
        print("Please add a command to test")