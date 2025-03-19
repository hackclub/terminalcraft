#!/usr/bin/env python3
"""
new features:
  - Automatic clipboard monitoring and syncing ("autosync")
  - Real-time updates via SocketIO ("watch")
  - A combined "daemon" mode for auto-sync plus real-time updates
  - Backup and restore of clipboard history
  - Deleting individual entries from the server
  - Viewing/updating configuration
  - Optional encryption support using the cryptography package (Fernet)
  - Additional debug logging

Before running, install required packages:
  pip install requests pyperclip python-socketio cryptography

If you don't want encryption, you may skip installing cryptography.
"""

import argparse
import json
import os
import sys
import time
import logging
import threading
import requests
import pyperclip
import socketio

# Optional encryption support using cryptography (Fernet)
try:
    from cryptography.fernet import Fernet, InvalidToken
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False

# Constants for configuration and default server URL
CONFIG_FILE = os.path.expanduser("~/.clipkeep_config.json")
DEFAULT_SERVER_URL = "http://clipkeep.yzde.es"

# Configure logging for detailed debugging and info messages
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ClipKeep")


def load_config():
    """
    Load configuration from the config file.
    Returns:
        dict: Configuration dictionary.
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                logger.debug("Config loaded: %s", config)
                return config
        except Exception as e:
            logger.error("Error reading config: %s", e)
            return {}
    return {}


def save_config(cfg):
    """
    Save configuration to the config file.
    Args:
        cfg (dict): Configuration dictionary.
    """
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=4)
        logger.debug("Config saved: %s", cfg)
    except Exception as e:
        logger.error("Error saving config: %s", e)


def generate_encryption_key():
    """
    Generate a new encryption key using Fernet.
    Returns:
        str: The encryption key.
    """
    if not ENCRYPTION_AVAILABLE:
        logger.error("Encryption not available. Please install 'cryptography' package.")
        return None
    key = Fernet.generate_key().decode()
    logger.info("Generated encryption key.")
    return key


def encrypt_text(text, key):
    """
    Encrypt text using the provided key.
    Args:
        text (str): The text to encrypt.
        key (str): The encryption key.
    Returns:
        str: Encrypted text.
    """
    if not ENCRYPTION_AVAILABLE:
        return text
    f = Fernet(key.encode())
    try:
        encrypted = f.encrypt(text.encode()).decode()
        return encrypted
    except Exception as e:
        logger.error("Encryption failed: %s", e)
        return text


def decrypt_text(text, key):
    """
    Decrypt text using the provided key.
    Args:
        text (str): The text to decrypt.
        key (str): The encryption key.
    Returns:
        str: Decrypted text.
    """
    if not ENCRYPTION_AVAILABLE:
        return text
    f = Fernet(key.encode())
    try:
        decrypted = f.decrypt(text.encode()).decode()
        return decrypted
    except InvalidToken:
        logger.error("Invalid encryption key or corrupted text.")
        return text
    except Exception as e:
        logger.error("Decryption failed: %s", e)
        return text


class ClipKeepClient:
    """
    ClipKeep client for synchronizing clipboard entries with the server.
    Provides methods for adding, retrieving, deleting entries and more.
    """

    def __init__(self, server_url=DEFAULT_SERVER_URL, debug=False):
        self.config = load_config()
        self.server_url = self.config.get("server_url", server_url)
        self.passkey = self.config.get("passkey")
        self.device = self.config.get("device", os.uname().nodename if hasattr(os, "uname") else "unknown")
        self.encryption_key = self.config.get("encryption_key") if ENCRYPTION_AVAILABLE else None
        self.debug = debug
        if debug:
            logger.setLevel(logging.DEBUG)
        logger.debug("Initialized ClipKeepClient with server_url: %s, device: %s", self.server_url, self.device)
        self.last_clipboard = None
        self.sync_thread = None
        self.stop_sync = threading.Event()
        self.sio = None  # SocketIO client

    def update_config(self, key, value):
        """
        Update a configuration parameter and save to config file.
        Args:
            key (str): Configuration key.
            value: Configuration value.
        """
        self.config[key] = value
        save_config(self.config)
        setattr(self, key, value)
        logger.info("Updated config %s: %s", key, value)

    def show_config(self):
        """
        Display current configuration.
        """
        print(json.dumps(self.config, indent=4))

    def set_key(self, passkey):
        """
        Set the passkey for authentication.
        Args:
            passkey (str): The passkey.
        """
        self.passkey = passkey
        self.update_config("passkey", passkey)
        if "device" not in self.config:
            self.update_config("device", self.device)
        print("Passkey set.")

    def add_clip(self, text, expire_in=None):
        """
        Add a clipboard entry to the server.
        Args:
            text (str): Text to add.
            expire_in (float): Optional expiration time in seconds.
        """
        if self.encryption_key:
            text_to_send = encrypt_text(text, self.encryption_key)
            logger.debug("Text encrypted for sending.")
        else:
            text_to_send = text
        data = {
            "passkey": self.passkey,
            "text": text_to_send,
            "device": self.device,
        }
        if expire_in is not None:
            data["expire_in"] = expire_in
        try:
            r = requests.post(f"{self.server_url}/clipboard", json=data)
            if r.ok:
                print("Clipboard text added.")
            else:
                print("Error adding clipboard:", r.json())
        except Exception as e:
            logger.error("Failed to add clipboard: %s", e)
            print("Error connecting to server.")

    def get_entries(self, limit=10):
        """
        Retrieve clipboard entries from the server.
        Args:
            limit (int): Number of entries to retrieve.
        """
        params = {"passkey": self.passkey, "limit": limit}
        try:
            r = requests.get(f"{self.server_url}/clipboard", params=params)
            if r.ok:
                entries = r.json().get("entries", [])
                for entry in entries:
                    text = entry.get("text", "")
                    if self.encryption_key:
                        text = decrypt_text(text, self.encryption_key)
                    print(f"{entry.get('id')}: {text} (from {entry.get('device','unknown')})")
            else:
                print("Error fetching entries:", r.json())
        except Exception as e:
            logger.error("Failed to get entries: %s", e)
            print("Error connecting to server.")

    def get_entry(self, entry_id):
        """
        Retrieve a specific clipboard entry by ID.
        Args:
            entry_id (int): The ID of the entry.
        """
        params = {"passkey": self.passkey}
        try:
            r = requests.get(f"{self.server_url}/clipboard/entry/{entry_id}", params=params)
            if r.ok:
                entry = r.json().get("entry")
                text = entry.get("text", "")
                if self.encryption_key:
                    text = decrypt_text(text, self.encryption_key)
                print(f"{entry.get('id')}: {text} (from {entry.get('device','unknown')})")
            else:
                print("Error fetching entry:", r.json())
        except Exception as e:
            logger.error("Failed to get entry: %s", e)
            print("Error connecting to server.")

    def clear_entries(self):
        """
        Clear all clipboard entries for this device on the server.
        """
        data = {"passkey": self.passkey, "device": self.device}
        try:
            r = requests.delete(f"{self.server_url}/clipboard", json=data)
            if r.ok:
                print("Clipboard cleared on server.")
            else:
                print("Error clearing clipboard:", r.json())
        except Exception as e:
            logger.error("Failed to clear entries: %s", e)
            print("Error connecting to server.")

    def delete_entry(self, entry_id):
        """
        Delete a specific clipboard entry by ID.
        Args:
            entry_id (int): The ID of the entry to delete.
        """
        data = {"passkey": self.passkey, "entry_id": entry_id}
        try:
            r = requests.delete(f"{self.server_url}/clipboard/entry", json=data)
            if r.ok:
                print(f"Entry {entry_id} deleted.")
            else:
                print("Error deleting entry:", r.json())
        except Exception as e:
            logger.error("Failed to delete entry: %s", e)
            print("Error connecting to server.")

    def paste_latest(self):
        """
        Fetch the latest clipboard entry and copy it to the local clipboard.
        """
        params = {"passkey": self.passkey, "limit": 1}
        try:
            r = requests.get(f"{self.server_url}/clipboard", params=params)
            if r.ok:
                entries = r.json().get("entries", [])
                if entries:
                    latest = entries[-1]
                    text = latest.get("text", "")
                    if self.encryption_key:
                        text = decrypt_text(text, self.encryption_key)
                    pyperclip.copy(text)
                    print("Latest clipboard text copied to local clipboard.")
                else:
                    print("No entries found.")
            else:
                print("Error fetching latest entry:", r.json())
        except Exception as e:
            logger.error("Failed to paste latest: %s", e)
            print("Error connecting to server.")

    def watch_clipboard(self):
        """
        Listen for clipboard updates from the server in real time.
        """
        self.sio = socketio.Client()

        @self.sio.event
        def connect():
            logger.info("Connected to server via SocketIO.")
            self.sio.emit("join", {"passkey": self.passkey, "device": self.device})

        @self.sio.on("clipboard_update")
        def on_update(data):
            text = data.get("text", "")
            if self.encryption_key:
                text = decrypt_text(text, self.encryption_key)
            pyperclip.copy(text)
            print("Clipboard updated from network:", text)

        try:
            self.sio.connect(self.server_url)
            logger.info("SocketIO connection established.")
            # Keep the connection alive until interrupted.
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received. Disconnecting SocketIO.")
            self.sio.disconnect()
        except Exception as e:
            logger.error("SocketIO connection error: %s", e)
            print("Error connecting to server via SocketIO.")

    def auto_sync(self, polling_interval=1.0):
        """
        Automatically monitor local clipboard changes and sync to server.
        This runs in a separate thread.
        Args:
            polling_interval (float): Time in seconds between clipboard checks.
        """
        logger.info("Starting auto-sync with polling interval %s seconds.", polling_interval)
        self.last_clipboard = pyperclip.paste()
        while not self.stop_sync.is_set():
            current_clip = pyperclip.paste()
            if current_clip != self.last_clipboard:
                logger.debug("Clipboard change detected.")
                self.last_clipboard = current_clip
                self.add_clip(current_clip)
            time.sleep(polling_interval)
        logger.info("Auto-sync stopped.")

    def start_auto_sync(self, polling_interval=1.0):
        """
        Start the auto-sync in a separate thread.
        Args:
            polling_interval (float): Time in seconds between checks.
        """
        self.stop_sync.clear()
        self.sync_thread = threading.Thread(target=self.auto_sync, args=(polling_interval,), daemon=True)
        self.sync_thread.start()
        logger.info("Auto-sync thread started.")

    def stop_auto_sync(self):
        """
        Stop the auto-sync thread.
        """
        self.stop_sync.set()
        if self.sync_thread:
            self.sync_thread.join()
        logger.info("Auto-sync thread stopped.")

    def backup_entries(self, backup_file):
        """
        Backup all clipboard entries from the server to a local file.
        Args:
            backup_file (str): Path to the backup file.
        """
        params = {"passkey": self.passkey, "limit": 1000}  # Adjust limit as needed
        try:
            r = requests.get(f"{self.server_url}/clipboard", params=params)
            if r.ok:
                data = r.json()
                with open(backup_file, "w") as f:
                    json.dump(data, f, indent=4)
                print(f"Backup saved to {backup_file}.")
            else:
                print("Error backing up entries:", r.json())
        except Exception as e:
            logger.error("Backup failed: %s", e)
            print("Error connecting to server for backup.")

    def restore_entries(self, backup_file):
        """
        Restore clipboard entries from a backup file to the server.
        Args:
            backup_file (str): Path to the backup file.
        """
        if not os.path.exists(backup_file):
            print("Backup file not found.")
            return
        try:
            with open(backup_file, "r") as f:
                data = json.load(f)
            entries = data.get("entries", [])
            for entry in entries:
                text = entry.get("text", "")
                if self.encryption_key:
                    text = decrypt_text(text, self.encryption_key)
                self.add_clip(text)
                time.sleep(0.2)  # Delay to avoid overwhelming server
            print("Restore complete.")
        except Exception as e:
            logger.error("Restore failed: %s", e)
            print("Error restoring from backup.")

    def ping_server(self):
        """
        Ping the server to check connectivity.
        """
        try:
            r = requests.get(f"{self.server_url}/ping")
            if r.ok:
                print("Server response:", r.json())
            else:
                print("Error pinging server:", r.json())
        except Exception as e:
            logger.error("Ping failed: %s", e)
            print("Error connecting to server.")

    def run_daemon(self, polling_interval=1.0):
        """
        Run both auto-sync and real-time watch concurrently.
        This daemon mode starts auto-sync in a background thread and
        runs the SocketIO client in the main thread.
        """
        logger.info("Starting daemon mode: auto-sync and SocketIO watch.")
        self.start_auto_sync(polling_interval)
        try:
            self.watch_clipboard()
        except KeyboardInterrupt:
            logger.info("Daemon mode interrupted by user.")
        finally:
            self.stop_auto_sync()
            if self.sio and self.sio.connected:
                self.sio.disconnect()
            logger.info("Daemon mode terminated.")


def main():
    """
    Main function to parse arguments and execute commands.
    """
    parser = argparse.ArgumentParser(description="ClipKeep - Clipboard Synchronization Tool")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # setkey command
    parser_setkey = subparsers.add_parser("setkey", help="Set your passkey for syncing")
    parser_setkey.add_argument("passkey", help="Your unique passkey")

    # add command
    parser_add = subparsers.add_parser("add", help="Add a clipboard entry")
    parser_add.add_argument("text", nargs="?", help="Text to add. If not provided, uses clipboard content")
    parser_add.add_argument("--expire", type=float, default=None, help="Expiration time in seconds")

    # list command
    parser_list = subparsers.add_parser("list", help="List recent clipboard entries")
    parser_list.add_argument("--limit", type=int, default=10, help="Number of entries to list")

    # get command
    parser_get = subparsers.add_parser("get", help="Get a specific clipboard entry")
    parser_get.add_argument("id", type=int, help="Entry ID")

    # clear command
    subparsers.add_parser("clear", help="Clear clipboard entries on the server")

    # delete command
    parser_delete = subparsers.add_parser("delete", help="Delete a specific clipboard entry")
    parser_delete.add_argument("id", type=int, help="Entry ID to delete")

    # paste command
    subparsers.add_parser("paste", help="Paste the latest clipboard entry")

    # watch command
    subparsers.add_parser("watch", help="Watch for clipboard updates in real time")

    # autosync command
    parser_autosync = subparsers.add_parser("autosync", help="Automatically sync local clipboard changes")
    parser_autosync.add_argument("--interval", type=float, default=1.0, help="Polling interval in seconds")

    # backup command
    parser_backup = subparsers.add_parser("backup", help="Backup clipboard entries to a file")
    parser_backup.add_argument("file", help="Backup file path")

    # restore command
    parser_restore = subparsers.add_parser("restore", help="Restore clipboard entries from a backup file")
    parser_restore.add_argument("file", help="Backup file path")

    # config command
    parser_config = subparsers.add_parser("config", help="Show or update configuration")
    parser_config.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="Set configuration key to value")

    # ping command
    subparsers.add_parser("ping", help="Ping the server to check connectivity")

    # daemon command
    parser_daemon = subparsers.add_parser("daemon", help="Run in daemon mode (auto-sync and real-time watch)")
    parser_daemon.add_argument("--interval", type=float, default=1.0, help="Polling interval in seconds for auto-sync")

    # genkey command for encryption key generation
    subparsers.add_parser("genkey", help="Generate and set a new encryption key (requires cryptography)")

    # version command
    subparsers.add_parser("version", help="Show version information")

    args = parser.parse_args()
    client = ClipKeepClient(debug=args.debug)

    # Execute commands based on user input
    if args.command == "setkey":
        client.set_key(args.passkey)
    elif args.command == "add":
        text = args.text if args.text is not None else pyperclip.paste()
        client.add_clip(text, args.expire)
    elif args.command == "list":
        client.get_entries(limit=args.limit)
    elif args.command == "get":
        client.get_entry(args.id)
    elif args.command == "clear":
        client.clear_entries()
    elif args.command == "delete":
        client.delete_entry(args.id)
    elif args.command == "paste":
        client.paste_latest()
    elif args.command == "watch":
        client.watch_clipboard()
    elif args.command == "autosync":
        try:
            client.start_auto_sync(args.interval)
            print("Auto-sync started. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            client.stop_auto_sync()
            print("Auto-sync stopped.")
    elif args.command == "backup":
        client.backup_entries(args.file)
    elif args.command == "restore":
        client.restore_entries(args.file)
    elif args.command == "config":
        if args.set:
            key, value = args.set
            client.update_config(key, value)
        else:
            client.show_config()
    elif args.command == "ping":
        client.ping_server()
    elif args.command == "daemon":
        client.run_daemon(args.interval)
    elif args.command == "genkey":
        if ENCRYPTION_AVAILABLE:
            key = generate_encryption_key()
            if key:
                client.update_config("encryption_key", key)
                print("Encryption key generated and saved in config.")
        else:
            print("Encryption feature not available. Please install the 'cryptography' package.")
    elif args.command == "version":
        print("ClipKeep version 2.0.0")
    else:
        parser.print_help()

    # Allow time for logs to flush if necessary before exiting
    time.sleep(0.1)


if __name__ == "__main__":
    main()
