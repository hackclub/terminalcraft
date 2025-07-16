import os
import json
import base64
import getpass
import pyperclip
import time
from datetime import datetime
from termcolor import colored
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

VAULT_FILE = 'passwords.json'
SALT_FILE = 'salt.bin'

def print_banner():
    ascii_art = r"""

$$\   $$\ $$$$$$$$\ $$\   $$\ $$$$$$$$\ $$$$$$$$\ $$$$$$$\  $$\      $$\ 
$$$\  $$ |$$  _____|$$ |  $$ |\__$$  __|$$  _____|$$  __$$\ $$$\    $$$ |
$$$$\ $$ |$$ |      \$$\ $$  |   $$ |   $$ |      $$ |  $$ |$$$$\  $$$$ |
$$ $$\$$ |$$$$$\     \$$$$  /    $$ |   $$$$$\    $$$$$$$  |$$\$$\$$ $$ |
$$ \$$$$ |$$  __|    $$  $$<     $$ |   $$  __|   $$  __$$< $$ \$$$  $$ |
$$ |\$$$ |$$ |      $$  /\$$\    $$ |   $$ |      $$ |  $$ |$$ |\$  /$$ |
$$ | \$$ |$$$$$$$$\ $$ /  $$ |   $$ |   $$$$$$$$\ $$ |  $$ |$$ | \_/ $$ |
\__|  \__|\________|\__|  \__|   \__|   \________|\__|  \__|\__|     \__|
                                                                         
Your Personal Password Manager
"""
    print(colored(ascii_art, 'cyan'))

# pause screen
def pause():
    input(colored("\npress enter to return...", 'yellow'))

# create key from master password
def generate_key(master_password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
    )
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode()))

# read vault file
def load_vault():
    if not os.path.exists(VAULT_FILE):
        return {}
    with open(VAULT_FILE, 'r') as file:
        return json.load(file)

# write vault file
def save_vault(vault):
    with open(VAULT_FILE, 'w') as file:
        json.dump(vault, file, indent=4)

# encryption and decryption
def encrypt_password(fernet, password):
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(fernet, encrypted):
    return fernet.decrypt(encrypted.encode()).decode()

# first timee setup
def setup_master_password():
    master = getpass.getpass("set master password: ")
    confirm = getpass.getpass("confirm password: ")
    if master != confirm:
        print("passwords do not match")
        exit(1)
    salt = os.urandom(16)
    with open(SALT_FILE, 'wb') as f:
        f.write(salt)
    return master, salt

# check access
def authenticate(prompt="enter master password: "):
    if not os.path.exists(SALT_FILE):
        return setup_master_password()
    salt = open(SALT_FILE, 'rb').read()
    master = getpass.getpass(prompt)
    return master, salt

# random password gen
def generate_password(length=16):
    import secrets, string
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(chars) for _ in range(length))

# clipboard
def copy_to_clipboard(pwd, auto_clear=True, delay=10):
    pyperclip.copy(pwd)
    print(colored(f"[+] copied. will clear in {delay}s", 'yellow'))
    if auto_clear:
        try:
            time.sleep(delay)
            pyperclip.copy('')
            print(colored("[+] clipboard cleared", 'green'))
        except KeyboardInterrupt:
            pass

# summary
def show_stats(vault):
    print(colored(f"\naccounts: {len(vault)}", 'cyan'))
    items = sorted(list(vault.keys()))
    if items:
        print(colored("list:", 'cyan'), ", ".join(items))
    else:
        print("none")

# main menu loop
def main():
    print_banner()
    master_password, salt = authenticate()
    key = generate_key(master_password, salt)
    fernet = Fernet(key)
    vault = load_vault()

    while True:
        print(colored("\n[ menu ]", 'blue'))
        print("1. add account")
        print("2. view account")
        print("3. search")
        print("4. list all")
        print("5. delete")
        print("6. generate password")
        print("7. stats")
        print("8. exit")

        choice = input("select: ")

        if choice == '1':
            acc = input("account name: ").strip()
            user = input("username: ").strip()
            pwd = getpass.getpass("password (blank = auto gen): ")
            if not pwd:
                pwd = generate_password()
                print(f"generated: {pwd}")
            vault[acc] = {
                'username': user,
                'password': encrypt_password(fernet, pwd),
                'created_at': datetime.now().isoformat()
            }
            save_vault(vault)
            print(colored("saved", 'green'))
            pause()

        elif choice == '2':
            acc = input("account name: ").strip()
            if acc in vault:
                reauth = getpass.getpass("master password: ")
                if generate_key(reauth, salt) != key:
                    print(colored("invalid password", 'red'))
                    pause()
                    continue
                data = vault[acc]
                pwd = decrypt_password(fernet, data['password'])
                print(f"\naccount: {acc}")
                print(f"user: {data['username']}")
                print(f"created: {data.get('created_at', '-')}")
                print("1. show password\n2. copy to clipboard")
                action = input("choose: ")
                if action == "1":
                    print(f"password: {pwd}")
                elif action == "2":
                    copy_to_clipboard(pwd)
            else:
                print(colored("not found", 'red'))
            pause()

        elif choice == '3':
            query = input("search keyword: ").lower()
            found = False
            for acc, data in vault.items():
                if query in acc.lower() or query in data['username'].lower():
                    print(colored(f"{acc} ({data['username']})", 'yellow'))
                    found = True
            if not found:
                print(colored("no match", 'red'))
            pause()

        elif choice == '4':
            if vault:
                for acc in vault:
                    print(f"{acc} ({vault[acc]['username']})")
            else:
                print(colored("vault empty", 'cyan'))
            pause()

        elif choice == '5':
            acc = input("account name to delete: ").strip()
            if acc in vault:
                confirm = input("type DELETE to confirm: ")
                if confirm == "DELETE":
                    del vault[acc]
                    save_vault(vault)
                    print(colored("deleted", 'green'))
            else:
                print(colored("not found", 'red'))
            pause()

        elif choice == '6':
            length = int(input("length: "))
            pwd = generate_password(length)
            print(f"password: {pwd}")
            copy_to_clipboard(pwd)
            pause()

        elif choice == '7':
            show_stats(vault)
            pause()

        elif choice == '8':
            break

        else:
            print(colored("invalid option", 'red'))
            pause()

if __name__ == "__main__":
    main()