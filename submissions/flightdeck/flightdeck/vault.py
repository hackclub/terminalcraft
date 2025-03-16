import colorama
from colorama import Fore, Back, Style
import getpass
import socket
import os
import pyAesCrypt
import platform
from pathlib import Path
import pickle
import subprocess

BUFFER_SIZE = 64 * 1024

hostname = socket.gethostname()
username = getpass.getuser()

vault_entry = True
unlocked = False
first_entry = True

def vault_location(os):
    if os == "Windows":
        path = f"C:/Users/{username}/Documents/FlightDeckVault"
    elif os == "Linux":
        path = f"/home/{username}/Documents/FlightDeckVault"
    elif os == "Darwin":
        path = f"/Users/{username}/Documents/FlightDeckVault"
    return path

# Enccryption/Decryption
def encrypt_file(file_path, password):
    encrypted_path = file_path + ".fdei"
    pyAesCrypt.encryptFile(file_path, encrypted_path, password, BUFFER_SIZE)
    os.remove(file_path)

def encrypt_folder(folder_path, password):
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            encrypt_file(file_path, password)
    print(f"Folder '{folder_path}' encrypted successfully.")

class DecryptionError(Exception):
    pass

def decrypt_file(encrypted_file_path, password):
    original_file_path = encrypted_file_path[:-5] 
    try:
        pyAesCrypt.decryptFile(encrypted_file_path, original_file_path, password, BUFFER_SIZE)
        os.remove(encrypted_file_path)
        print(f"Decrypted: {original_file_path}")
    except Exception:
        raise DecryptionError(f"Failed to decrypt {encrypted_file_path}: Wrong password or corrupted file.")

def decrypt_folder(folder_path, password):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".fdei"): 
                encrypted_file_path = os.path.join(root, file)
                decrypt_file(encrypted_file_path, password) 
    print(f"Decryption process completed for '{folder_path}'.")


# New guy setup
def welcome():
    global unlocked
    print("✈ Welcome to the FlightDeck Vault!")
    print("Since this is your first time, we'll need to set up your vault.")
    os = platform.system()
    if os == "Windows":
        path = Path(f"C:/Users/{username}/Documents/FlightDeckVault")
        path.mkdir(parents=True, exist_ok=True)
    elif os == "Linux":
        path = Path(f"/home/{username}/Documents/FlightDeckVault")
        path.mkdir(parents=True, exist_ok=True)
    elif os == "Darwin":
        path = Path(f"/Users/{username}/Documents/FlightDeckVault")
        path.mkdir(parents=True, exist_ok=True)

    print(f"Vault created at {path}!")
    print("In case you ever forget this, you can use the 'path' command to see where your vault is located.")

    unlocked = True

def main_loop():
    global first_entry, unlocked, vault_entry

    try:
        with open("data.pkl", "rb") as f:
            first_entry = pickle.load(f)
    except:
        first_entry = True

    colorama.init(autoreset=True)


    if not first_entry:
        print("✈ Welcome to the FlightDeck Vault!")
        print("Please start by unencrypting your vault.")

        verifying_password = True
        first_attempt = True
        new_vault = False
        while verifying_password:
            password = getpass.getpass("Enter your password: ")

            if not first_attempt and password == "HELP IT MOVED":
                print("Let's get a new vault")
                new_vault = True
                break

            path = vault_location(platform.system())
            try:
                decrypt_folder(path, password)
                unlocked = True
                verifying_password = False
                print("Vault unlocked!")
            except DecryptionError:
                print("Failed to decrypt. Please enter a valid password or ensure that your vault has not been moved/deleted. If it has moved/deleted, enter the \"HELP IT MOVED\" in the next prompt to create a new one")
            
            first_attempt = False

        if new_vault:
            welcome()
    elif first_entry:
        welcome()
        first_entry = False
        with open("data.pkl", "wb") as f:
            pickle.dump(first_entry, f)

    print("Commands: help, exit, add, tree, path")

    help = f"""
    Welcome to the FlightDeck Secure Vault!
    Current vault status: {'🔒' if not unlocked else '🔑'}

    Commands:
    help       - show this help message
    exit       - exit the vault
    add [file] - add a new note to your vault
    tree       - show the tree structure of your vault
    path       - show the current path to your vault
    rm         - remove a note from your vault
    sys [cmd]  - run a system command
    """

    while vault_entry:
        command = input(f"{Fore.BLUE}{'🔒' if not unlocked else '🔑'} FlightDeck Vault{Fore.RESET} {Fore.GREEN}{username} at {hostname} {Fore.BLUE}✈{Fore.RESET}  ")
        if command == "exit":
            vault_entry = False
            print("🔒 Lock your vault before you go!")
            verifying_password = True
            while verifying_password:
                password = getpass.getpass("Enter a password: ")
                confirm_password = getpass.getpass("Enter it again to confirm: ")
                if password == confirm_password:
                    verifying_password = False
                else:
                    print("Passwords do not match. Try again.")

            path = vault_location(platform.system())
            encrypt_folder(path, password)
            print("Vault locked. Do not forget your password else you will lose access to your vault!")
            print("See you soon!")
        
        elif command == "help":
            print(help)
        
        elif command.startswith("add"):
            try:
                print(f"Adding a new note with the title '{command.split(' ', 1)[1]}.md'...")
                with open(f"{vault_location(platform.system())}/{command.split(' ', 1)[1]}.md", "w") as f:
                    f.write("")
                    print("File created!")
            except:
                print("Error creating file. Did you provide a filename?")
                
            try:
                if platform.system() == "Windows":
                    subprocess.run(f"notepad {vault_location(platform.system())}/{command.split(' ', 1)[1]}.md")
                else:
                    os.system(f"nano {vault_location(platform.system())}/{command.split(' ', 1)[1]}.md")
            except:
                print("Error opening file. You will need to open it manually.")
                print("P.S: If you are on macOS/Linux, please make sure GNU Nano is installed for this to work.")
        
        elif command.startswith("sys"):
            print(f"Running system command: {command.split(' ', 1)[1]}")
            subprocess.run(command.split(' ', 1)[1], shell=True)

        elif command.startswith("rm"):
            print(f"Removing note '{command.split(' ', 1)[1]}.md'...")
            try:
                os.remove(f"{vault_location(platform.system())}/{command.split(' ', 1)[1]}.md")
                print("File removed!")
            except FileNotFoundError:
                print("File not found. Please enter a real file.")

        elif command == "path":
            print("To add your own file, the path of your vault is:")
            print(vault_location(platform.system()))

        elif command == "tree":
            print("Showing tree structure of your vault...")
            if platform.system() == "Windows":
                os.system(f"tree /F /A {vault_location(platform.system())}")
            else:
                os.system(f"tree {vault_location(platform.system())}")

        else:
            print("Invalid command. Type 'help' to see available commands.")

if __name__ == "__main__":
    main_loop()