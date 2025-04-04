import os
from pathlib import Path

def get_default_storage_path() -> Path:
    """Get the default storage path for bookmarks."""
    if os.name == 'nt':
        base_dir = Path(os.environ.get('APPDATA', '~/.terminal-bookmarks'))
    else:
        base_dir = Path(os.environ.get('XDG_DATA_HOME', '~/.local/share/terminal-bookmarks'))
    base_dir = base_dir.expanduser()
    storage_path = base_dir / 'bookmarks.json'
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    
    return storage_path 