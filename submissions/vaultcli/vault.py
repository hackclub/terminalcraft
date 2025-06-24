import os
import json
import base64
import getpass
from cryptography.fernet import Fernet
from rich.console import Console
from rich.prompt import Prompt

DATA_FILE = "vault_data.enc"
console = Console()

def generate_key(master_password):
    return base64.urlsafe_b64encode(master_password.encode("utf-8").ljust(32)[:32])

def load_notes(cipher):
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "rb") as f:
        data = cipher.decrypt(f.read())
        return json.loads(data.decode("utf-8"))

def save_notes(cipher, notes):
    data = json.dumps(notes).encode("utf-8")
    with open(DATA_FILE, "wb") as f:
        f.write(cipher.encrypt(data))

def add_note(cipher, notes):
    title = Prompt.ask("Enter title")
    content = Prompt.ask("Enter content")
    notes.append({"title": title, "content": content})
    save_notes(cipher, notes)
    console.print("[green]Note saved and encrypted![/green]")

def list_notes(notes):
    console.print("\n[bold underline]Stored Notes:[/bold underline]")
    for i, note in enumerate(notes):
        console.print(f"{i+1}. [bold]{note['title']}[/bold]")

def main():
    console.print("[bold cyan]Vault CLI - Encrypted Notes[/bold cyan]")
    pw = getpass.getpass("Enter your master password: ")
    key = generate_key(pw)
    cipher = Fernet(key)
    try:
        notes = load_notes(cipher)
    except:
        notes = []

    while True:
        console.print("\n[1] Add Note\n[2] List Notes\n[3] Exit")
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3"])
        if choice == "1":
            add_note(cipher, notes)
        elif choice == "2":
            list_notes(notes)
        else:
            break

if __name__ == "__main__":
    main()
