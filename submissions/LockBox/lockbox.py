#!/usr/bin/env python3
import os
import json
import secrets
import string
import sys
from datetime import datetime
from getpass import getpass
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

# ASCII Art Header
def show_header():
    print(r"""
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃  ██╗      ██████╗  ██████╗██╗  ██╗██████╗  ██████╗ ██╗  ██╗  ┃
    ┃  ██║     ██╔═══██╗██╔════╝██║ ██╔╝██╔══██╗██╔═══██╗╚██╗██╔╝  ┃
    ┃  ██║     ██║   ██║██║     █████╔╝ ██████╔╝██║   ██║ ╚███╔╝   ┃
    ┃  ██║     ██║   ██║██║     ██╔═██╗ ██╔══██╗██║   ██║ ██╔██╗   ┃
    ┃  ███████╗╚██████╔╝╚██████╗██║  ██╗██████╔╝╚██████╔╝██╔╝ ██╗  ┃
    ┃  ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝  ┃
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
    """)
    print(" " * 20 + "🔒 Secure CLI Password Manager")
    print("-" * 60)

# Box-drawing characters
BOX_TOP = "╭───────────────────────────────╮"
BOX_MID = "├───────────────────────────────┤"
BOX_BOT = "╰───────────────────────────────╯"

# Config
STORAGE_PATH = os.path.expanduser("~/.lockbox/passwords.json")

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_box(title, content):
    """Draw a bordered box with title"""
    print(BOX_TOP)
    print(f"│ {title:^29} │")
    print(BOX_MID)
    for line in content.split('\n'):
        print(f"│ {line:<29} │")
    print(BOX_BOT)

def show_menu():
    """Display main menu"""
    clear_screen()
    show_header()
    draw_box("MAIN MENU", """
1. Generate & Store Password
2. Store Existing Password
3. Get Password
4. List All
5. Search Passwords
6. Export
7. Exit""")

def get_choice():
    """Get user menu choice"""
    while True:
        try:
            choice = int(input("\nSelect option (1-7): "))
            if 1 <= choice <= 7:
                return choice
            print("Please enter 1-7")
        except ValueError:
            print("Invalid input")

def generate_password(length=16):
    """Generate a strong random password"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(length))

def load_passwords():
    """Load passwords from file"""
    if not os.path.exists(STORAGE_PATH):
        return {}
    with open(STORAGE_PATH, 'r') as f:
        return json.load(f)

def save_passwords(passwords):
    """Save passwords to file"""
    os.makedirs(os.path.dirname(STORAGE_PATH), exist_ok=True)
    with open(STORAGE_PATH, 'w') as f:
        json.dump(passwords, f)
    os.chmod(STORAGE_PATH, 0o600)

def encrypt_data(data: bytes, key: bytes, iv: bytes) -> bytes:
    """AES-256-CBC encryption"""
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(padded_data) + encryptor.finalize()

def export_passwords(passwords):
    """Export passwords with optional encryption"""
    # Get the appropriate downloads directory for the OS
    if os.name == 'nt':  # Windows
        downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
    else:  # Linux/Mac
        username = os.getenv('SUDO_USER') or os.getenv('USER')
        downloads_dir = os.path.join('/home', username, 'Downloads')
    
    os.makedirs(downloads_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    choice = input("Encrypt the export file? (y/n): ").strip().lower()
    
    if choice == 'y':
        filename = f"passwords_export_{timestamp}.aes"
        filepath = os.path.join(downloads_dir, filename)
        
        key = secrets.token_bytes(32)
        iv = secrets.token_bytes(16)
        encrypted = encrypt_data(json.dumps(passwords).encode(), key, iv)
        
        with open(filepath, "wb") as f:
            f.write(encrypted)
        
        draw_box("EXPORT SUCCESS", f"""File: {filename}
Key (hex): {key.hex()}
IV (hex): {iv.hex()}

IMPORTANT: Save the key and IV separately!
They are required to decrypt the file.""")
    
    else:
        filename = f"passwords_export_{timestamp}.txt"
        filepath = os.path.join(downloads_dir, filename)
        
        with open(filepath, "w") as f:
            for service, password in passwords.items():
                f.write(f"{service}: {password}\n")
        
        draw_box("EXPORT SUCCESS", f"Saved to:\n{filename}")

    # Add a pause to prevent window from closing
    if os.name == 'nt':
        input("\nPress Enter to return to menu...")

def search_passwords():
    """Quick search through stored services"""
    query = input("Enter search term: ").lower()
    passwords = load_passwords()
    
    # Find matches (case-insensitive contains)
    matches = [service for service in passwords if query in service.lower()]
    
    if not matches:
        draw_box("SEARCH RESULTS", "No matching services found")
    else:
        result = "\n".join(matches)
        draw_box("SEARCH RESULTS", f"Found {len(matches)} matches:\n{result}")

def main():
    while True:
        show_menu()
        choice = get_choice()
        
        if choice == 1:  # Generate & Store
            service = input("Enter service name: ")
            password = generate_password()
            passwords = load_passwords()
            passwords[service] = password
            save_passwords(passwords)
            draw_box("SUCCESS", f"Added:\n{service}: {password}")
            input("\nPress Enter to continue...")
            
        elif choice == 2:  # Store Existing
            service = input("Enter service name: ")
            password = getpass("Enter password to store: ")
            confirm = getpass("Confirm password: ")
            
            if password != confirm:
                draw_box("ERROR", "Passwords don't match!")
            else:
                passwords = load_passwords()
                passwords[service] = password
                save_passwords(passwords)
                draw_box("SUCCESS", f"Stored password for {service}")
            input("\nPress Enter to continue...")
            
        elif choice == 3:  # Get
            service = input("Enter service name: ")
            passwords = load_passwords()
            if service in passwords:
                draw_box("PASSWORD", f"{service}:\n{passwords[service]}")
            else:
                draw_box("ERROR", "Service not found!")
            input("\nPress Enter to continue...")
            
        elif choice == 4:  # List
            passwords = load_passwords()
            content = "\n".join(f"{s:20} {'*'*len(p)}" for s,p in passwords.items())
            draw_box("STORED PASSWORDS", content or "No passwords stored")
            input("\nPress Enter to continue...")
            
        elif choice == 5:  # Search
            search_passwords()
            input("\nPress Enter to continue...")
            
        elif choice == 6:  # Export
            export_passwords(load_passwords())
            if os.name != 'nt':  # Already handled pause for Windows in export_passwords
                input("\nPress Enter to continue...")
            
        elif choice == 7:  # Exit
            sys.exit(0)

if __name__ == "__main__":
    main()
