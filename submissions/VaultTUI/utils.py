import base64
import json
import os
import hashlib
import shutil
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import csv
from config import VAULT_FILE, VAULT_DIR, BACKUP_DIR

def export_vault_to_csv(vault: dict, filename: str = "vault_export.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "url", "username", "password"])
        writer.writeheader()
        for name, entry in vault.items():
            writer.writerow({
                "name": name,
                "url": entry.get("url", ""),
                "username": entry.get("username", ""),
                "password": entry.get("password", "")
            })

# === Key Derivation ===

def generate_key(password: str, salt: bytes = b"vault_salt") -> bytes:
    """Derives a key from the master password using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend(),
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

# === Vault Encryption/Decryption ===

def encrypt(data: dict, key: bytes) -> bytes:
    """Encrypts the vault dictionary using Fernet."""
    f = Fernet(key)
    json_data = json.dumps(data).encode()
    return f.encrypt(json_data)

def decrypt(token: bytes, key: bytes) -> dict:
    """Decrypts the vault using the given key."""
    f = Fernet(key)
    decrypted = f.decrypt(token)
    return json.loads(decrypted.decode())

# === Vault Management ===

def load_vault(key: bytes) -> dict:
    """Loads and decrypts the vault."""
    if not VAULT_FILE.exists():
        return {}
    with open(VAULT_FILE, "rb") as f:
        return decrypt(f.read(), key)

def save_vault(vault_data: dict, key: bytes):
    """Encrypts and saves the vault."""
    encrypted = encrypt(vault_data, key)
    with open(VAULT_FILE, "wb") as f:
        f.write(encrypted)

def backup_vault():
    """Creates a timestamped backup of the vault."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy(VAULT_FILE, BACKUP_DIR / f"vault_backup_{timestamp}.enc")

def restore_vault():
    """Restores the latest backup."""
    backups = sorted(BACKUP_DIR.glob("vault_backup_*.enc"))
    if not backups:
        print("❌ No backups found.")
        return
    latest_backup = backups[-1]
    shutil.copy(latest_backup, VAULT_FILE)

# === Master Password Management ===

PASS_FILE = VAULT_DIR / ".vault_pass"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()
def set_master_password_initial(new_password: str):
    """Set a master password for the first time."""
    key = generate_key(new_password)
    save_vault({}, key)  # Save empty vault

    with open(PASS_FILE, "w") as f:
        f.write(hash_password(new_password))

    print("🔐 Master password set successfully.")

def set_master_password(old_password: str, new_password: str):
    """Change an existing master password."""
    if not validate_master_password(old_password):
        print("❌ Incorrect current master password. Aborting.")
        return

    old_key = generate_key(old_password)
    vault_data = load_vault(old_key)

    new_key = generate_key(new_password)
    save_vault(vault_data, new_key)

    with open(PASS_FILE, "w") as f:
        f.write(hash_password(new_password))

    print("🔐 Master password changed successfully.")

def validate_master_password(password: str) -> bool:
    """Validates entered password against stored hash."""
    if not PASS_FILE.exists():
        print("⚠️ No password is set. Use 'set-password' first.")
        return False
    with open(PASS_FILE, "r") as f:
        stored_hash = f.read().strip()
    return hash_password(password) == stored_hash

def get_entry(name: str, key: bytes) -> dict | None:
    """Returns a specific entry from the vault by name."""
    vault = load_vault(key)
    return vault.get(name)

def filter_entries(query: str, vault: dict) -> dict:
    """Returns entries whose names contain the query substring."""
    result = {}
    for name, entry in vault.items():
        if query.lower() in name.lower():
            result[name] = entry
    return result

def delete_entry_manual(name, vault):
    if name not in vault:
        print(f"❌ Entry '{name}' not found.")
        return False

    del vault[name]
    print(f"🗑️ Entry '{name}' deleted.")
    return True

def search_entries_manual(query, vault):
    return {
        name: entry
        for name, entry in vault.items()
        if query.lower() in name.lower()
    }
