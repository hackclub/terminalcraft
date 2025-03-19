import subprocess

import minecraft_launcher_lib
import sys
from colorama import Fore
import warnings
warnings.filterwarnings('ignore')

# Print the ASCII art and Welcome Message
print("|  \/  (_)                          / _| |  ")
print("| \  / |_ _ __ ___  _ __   ___ _ __| |_| |__")
print("| |\/| | | '_ \ / _ \/ __| '__/ _` |  _| __|")
print("| |  | | | | | |  __/ (__| | | (_| | | | |_ ")
print("\_|  |_/_|_| |_|\___|\___|_|  \__,_|_|  \__|")
print("Welcome to the Minecraft Launcher!")
print("This is a simple launcher for Minecraft Java Edition.")
print(Fore.RED + "As logging in to Microsoft accounts is currently not supported, you will be running a Demo version of Minecraft" + Fore.RESET)
print(Fore.RED + "Check https://github.com/ArmadilloMike/minecraft-launcher to see if there are any updates" + Fore.RESET)
print("Specify Minecraft Directory:")
minecraft_directory_choice = input("Enter the path to your Minecraft directory (Leave Blank for default): ")
if minecraft_directory_choice.strip() == "":
    minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
if minecraft_directory_choice.strip() != "":
    minecraft_directory = minecraft_directory_choice

print("Please choose an option:")
print("1. Launch Vanilla Minecraft"+Fore.RED+" (Demo Version)" + Fore.RESET)
print("2. Launch Minecraft with a Mod pack")
print("3. Exit")
choice = input("Enter your choice (1-3): "+Fore.RED+" Soon to be supported" + Fore.RESET)
if choice == '1':
    print("Installing and running Minecraft Demo Version...")
    options = minecraft_launcher_lib.utils.generate_test_options()
    options['demo'] = True
    print(options)
    minecraft_launcher_lib.install.install_minecraft_version("1.16.5", minecraft_directory)
    minecraft_command = minecraft_launcher_lib.command.get_minecraft_command("1.16.5", minecraft_directory, options)
    subprocess.call(minecraft_command)
if choice == '2':
    print("Will be supported soon!")
if choice == '3':
    print("Exiting...")
    sys.exit()