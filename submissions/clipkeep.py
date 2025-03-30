#!/usr/bin/env python3
"""
ClipKeep - P2P Clipboard Synchronization Tool

This tool synchronizes your clipboard across devices on the same local network using UDP multicast.
Optional encryption is available using the cryptography package.
"""

import argparse
import json
import os
import time
import logging
import threading
import socket
import pyperclip

# Optional encryption support
try:
    from cryptography.fernet import Fernet, InvalidToken
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False

# Constants for configuration and networking
CONFIG_FILE = os.path.expanduser("~/.clipkeep_config.json")
MULTICAST_GROUP = "224.0.0.251"  # Multicast address for local networks
MULTICAST_PORT = 5005
BUFFER_SIZE = 4096

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ClipKeep")


def load_config():
    """Load configuration from file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error("Error loading config: %s", e)
    return {}


def save_config(cfg):
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=4)
    except Exception as e:
        logger.error("Error saving config: %s", e)


def encrypt_text(text, key):
    """Encrypt text using Fernet."""
    if not ENCRYPTION_AVAILABLE:
        return text
    try:
        f = Fernet(key.encode())
        return f.encrypt(text.encode()).decode()
    except Exception as e:
        logger.error("Encryption failed: %s", e)
        return text


def decrypt_text(text, key):
    """Decrypt text using Fernet."""
    if not ENCRYPTION_AVAILABLE:
        return text
    try:
        f = Fernet(key.encode())
        return f.decrypt(text.encode()).decode()
    except InvalidToken:
        logger.error("Invalid encryption key or corrupted text.")
        return text
    except Exception as e:
        logger.error("Decryption failed: %s", e)
        return text


class ClipKeep:
    """Local clipboard manager with peer-to-peer synchronization."""

    def __init__(self, debug=False):
        self.config = load_config()
        self.encryption_key = self.config.get("encryption_key") if ENCRYPTION_AVAILABLE else None
        self.last_clipboard = None
        self.sync_thread = None
        self.stop_sync = threading.Event()
        self.peer_listener_thread = None
        if debug:
            logger.setLevel(logging.DEBUG)
        logger.debug("ClipKeep initialized.")

    def set_encryption_key(self, key=None):
        """
        Generate and save a new encryption key.
        Optionally, you can specify a key (as a string) to be used.
        """
        if not ENCRYPTION_AVAILABLE:
            logger.error("Encryption not available. Install the 'cryptography' package.")
            return
        if key is None:
            key = Fernet.generate_key().decode()
        self.config["encryption_key"] = key
        save_config(self.config)
        print("Encryption key set.")

    def add_clip(self, text):
        """Add text to clipboard and broadcast to peers."""
        if self.encryption_key:
            text_to_send = encrypt_text(text, self.encryption_key)
        else:
            text_to_send = text
        pyperclip.copy(text)
        logger.info("Local clipboard updated: %s", text)
        self.broadcast_clipboard(text_to_send)

    def paste_latest(self):
        """Print the current clipboard content."""
        text = pyperclip.paste()
        if self.encryption_key:
            text = decrypt_text(text, self.encryption_key)
        print("Current clipboard text:", text)

    def auto_sync(self, polling_interval=1.0):
        """Monitor local clipboard for changes and broadcast updates."""
        logger.info("Auto-sync started.")
        self.last_clipboard = pyperclip.paste()
        while not self.stop_sync.is_set():
            current_clip = pyperclip.paste()
            if current_clip != self.last_clipboard:
                self.last_clipboard = current_clip
                self.add_clip(current_clip)
            time.sleep(polling_interval)
        logger.info("Auto-sync stopped.")

    def start_auto_sync(self, polling_interval=1.0):
        """Start the auto-sync thread."""
        self.stop_sync.clear()
        self.sync_thread = threading.Thread(target=self.auto_sync, args=(polling_interval,), daemon=True)
        self.sync_thread.start()
        print("Auto-sync started. Press Ctrl+C to stop.")

    def stop_auto_sync(self):
        """Stop the auto-sync thread."""
        self.stop_sync.set()
        if self.sync_thread:
            self.sync_thread.join()
        print("Auto-sync stopped.")

    def broadcast_clipboard(self, text):
        """Broadcast clipboard update to peers via UDP multicast."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            message = json.dumps({"clipboard": text})
            sock.sendto(message.encode(), (MULTICAST_GROUP, MULTICAST_PORT))
            sock.close()
            logger.info("Broadcasted clipboard update.")
        except Exception as e:
            logger.error("Error broadcasting clipboard: %s", e)

    def listen_for_peers(self):
        """Listen for clipboard updates from peers."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("", MULTICAST_PORT))
        except Exception as e:
            logger.error("Error binding socket: %s", e)
            return

        group = socket.inet_aton(MULTICAST_GROUP)
        try:
            # Use local IP for joining the multicast group (fixes issues on macOS)
            local_ip = socket.gethostbyname(socket.gethostname())
            mreq = group + socket.inet_aton(local_ip)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        except Exception as e:
            logger.error("Error joining multicast group: %s", e)
            return

        while True:
            try:
                data, _ = sock.recvfrom(BUFFER_SIZE)
                message = json.loads(data.decode())
                text = message.get("clipboard", "")
                if self.encryption_key:
                    text = decrypt_text(text, self.encryption_key)
                pyperclip.copy(text)
                logger.info("Received clipboard update: %s", text)
            except Exception as e:
                logger.error("Error receiving peer message: %s", e)

    def start_daemon(self):
        """Run auto-sync and peer listener concurrently."""
        self.start_auto_sync()
        self.peer_listener_thread = threading.Thread(target=self.listen_for_peers, daemon=True)
        self.peer_listener_thread.start()
        print("Daemon mode started. Press Ctrl+C to stop.")


def main():
    """Command-line interface for ClipKeep."""
    parser = argparse.ArgumentParser(description="ClipKeep - P2P Clipboard Sync")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("daemon", help="Start clipboard sync in daemon mode")
    parser_add = subparsers.add_parser("add", help="Add a clipboard entry and broadcast it")
    parser_add.add_argument("text", help="Text to add to clipboard")
    subparsers.add_parser("paste", help="Show the current clipboard content")
    
    # Allow setting encryption key with an optional argument.
    parser_setkey = subparsers.add_parser("setkey", help="Generate and set a new encryption key or specify one")
    parser_setkey.add_argument("key", nargs="?", help="Optional: specify an encryption key")

    args = parser.parse_args()
    clipkeep = ClipKeep(debug=args.debug)

    if args.command == "daemon":
        clipkeep.start_daemon()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            clipkeep.stop_auto_sync()
            print("Daemon stopped.")
    elif args.command == "add":
        clipkeep.add_clip(args.text)
    elif args.command == "paste":
        clipkeep.paste_latest()
    elif args.command == "setkey":
        clipkeep.set_encryption_key(args.key)

if __name__ == "__main__":
    main()
