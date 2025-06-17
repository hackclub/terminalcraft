# config.py
from pathlib import Path

VAULT_DIR = Path.home() / ".vaulttui"
VAULT_FILE = VAULT_DIR / "vault.enc"
BACKUP_DIR = VAULT_DIR / "backups"

VAULT_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
