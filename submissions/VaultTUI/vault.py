import argparse
import getpass
import config
from config import VAULT_FILE, VAULT_DIR
import os

PASS_FILE = VAULT_DIR / ".vault_pass"

from utils import (
    generate_key,
    encrypt,
    decrypt,
    load_vault,
    save_vault,
    backup_vault,
    restore_vault,
    set_master_password,
    validate_master_password,
    get_entry,
    filter_entries,
)

def edit_entry_command(args):
    password = prompt_password()
    key = generate_key(password)
    vault = load_vault(key)

    if args.name not in vault:
        print(f"❌ Entry '{args.name}' not found.")
        return

    print(f"📝 Editing entry '{args.name}':")
    current = vault[args.name]

    new_username = input(f"New username [{current['username']}]: ") or current['username']
    new_password = getpass.getpass("New password (leave blank to keep current): ") or current['password']

    vault[args.name] = {
        "username": new_username,
        "password": new_password
    }

    save_vault(vault, key)
    print(f"✅ Entry '{args.name}' updated successfully.")

def search_entries(args):
    password = prompt_password()
    key = generate_key(password)
    vault = load_vault(key)

    results = filter_entries(args.query, vault)

    if not results:
        print(f"❌ No entries found for '{args.query}'.")
        return

    print(f"🔍 Results for '{args.query}':")
    for name in results:
        print(f"- {name}")

def prompt_password():
    return getpass.getpass("Enter master password: ")

def add_entry(args):
    password = prompt_password()
    key = generate_key(password)
    vault = load_vault(key)

    if args.name in vault:
        print(f"❗ Entry '{args.name}' already exists.")
        return

    vault[args.name] = {
        "username": args.username,
        "password": args.password,
    }
    save_vault(vault, key)
    print(f"✅ Entry '{args.name}' added.")

def view_entry(args):
    password = prompt_password()
    key = generate_key(password)

    entry = get_entry(args.name, key)
    if not entry:
        print(f"❌ Entry '{args.name}' not found.")
        return

    print(f"🔐 {args.name}:")
    print(f"   Username: {entry['username']}")
    print(f"   Password: {entry['password']}")

def delete_entry(args):
    password = prompt_password()
    key = generate_key(password)
    vault = load_vault(key)

    if args.name not in vault:
        print(f"❌ Entry '{args.name}' not found.")
        return

    del vault[args.name]
    save_vault(vault, key)
    print(f"🗑️ Entry '{args.name}' deleted.")

def list_entries(args):
    password = prompt_password()
    key = generate_key(password)
    vault = load_vault(key)

    print("📁 Saved entries:")
    for name in vault:
        print(f"- {name}")

def handle_backup(args):
    backup_vault()
    print("🗃️ Backup created.")

def handle_restore(args):
    restore_vault()
    print("📦 Vault restored from backup.")

def handle_set_password(args):
    if not PASS_FILE.exists():
        print("🔐 No existing password found. Setting up a new master password.")
        new_pw = getpass.getpass("Set master password: ")
        confirm_pw = getpass.getpass("Confirm master password: ")
        if new_pw != confirm_pw:
            print("❌ Passwords do not match.")
            return
        from utils import set_master_password_initial
        set_master_password_initial(new_pw)
        return

    old_pw = getpass.getpass("Enter current master password: ")
    if not validate_master_password(old_pw):
        print("❌ Incorrect current master password. Aborting.")
        return

    new_pw = getpass.getpass("Enter new master password: ")
    confirm_pw = getpass.getpass("Confirm new master password: ")
    if new_pw != confirm_pw:
        print("❌ Passwords do not match.")
        return

    set_master_password(old_pw, new_pw)

def handle_add_entry(args):
    password = input("Enter master password: ")
    if not validate_master_password(password):
        print("❌ Incorrect master password.")
        return

    key = generate_key(password)
    vault = load_vault(key)

    if args.name in vault:
        print(f"⚠️ Entry '{args.name}' already exists. Use a different name or delete it first.")
        return

    vault[args.name] = {
        "username": args.username,
        "password": args.password,
    }

    save_vault(vault, key)
    print(f"✅ Entry '{args.name}' added successfully.")

# 🔐 Only run CLI if executed directly
def main():
    parser = argparse.ArgumentParser(description="🔐 VaultTUI - Encrypted CLI Password Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add
    add_parser = subparsers.add_parser("add", help="Add a new entry")
    add_parser.add_argument("name", help="Entry name (e.g., github)")
    add_parser.add_argument("username", help="Username or email")
    add_parser.add_argument("password", help="Password")
    add_parser.set_defaults(func=add_entry)

    # View
    view_parser = subparsers.add_parser("view", help="View an entry")
    view_parser.add_argument("name", help="Entry name")
    view_parser.set_defaults(func=view_entry)

    # Get (alias)
    get_parser = subparsers.add_parser("get", help="Get an entry (alias for view)")
    get_parser.add_argument("name", help="Entry name")
    get_parser.set_defaults(func=view_entry)

    # Delete
    delete_parser = subparsers.add_parser("delete", help="Delete an entry")
    delete_parser.add_argument("name", help="Entry name")
    delete_parser.set_defaults(func=delete_entry)

    # List
    list_parser = subparsers.add_parser("list", help="List all entries")
    list_parser.set_defaults(func=list_entries)

    # Search
    search_parser = subparsers.add_parser("search", help="Search entries")
    search_parser.add_argument("query", help="Search query")
    search_parser.set_defaults(func=search_entries)

    # Backup
    backup_parser = subparsers.add_parser("backup", help="Backup the vault")
    backup_parser.set_defaults(func=handle_backup)

    # Restore
    restore_parser = subparsers.add_parser("restore", help="Restore from backup")
    restore_parser.set_defaults(func=handle_restore)

    # Set/change password
    setpass_parser = subparsers.add_parser("set-password", help="Set or change master password")
    setpass_parser.add_argument("new_password", help="New master password")
    setpass_parser.set_defaults(func=handle_set_password)

    # Edit
    edit_parser = subparsers.add_parser("edit", help="Edit an existing entry")
    edit_parser.add_argument("name", help="Entry name to edit")
    edit_parser.set_defaults(func=edit_entry_command)

    # Add entry (alternate)
    parser_add = subparsers.add_parser("add-entry", help="Add a new entry")
    parser_add.add_argument("name", help="Entry name (e.g., github)")
    parser_add.add_argument("username", help="Username for the entry")
    parser_add.add_argument("password", help="Password for the entry")
    parser_add.set_defaults(func=handle_add_entry)

    # Run
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
