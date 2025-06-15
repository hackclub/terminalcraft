import configparser
from pathlib import Path
import typer

APP_NAME = "sumsnap"
CONFIG_DIR_PATH = Path(typer.get_app_dir(APP_NAME))
CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"

def init_config() -> int:
    """Initialize the config file and directory."""
    try:
        CONFIG_DIR_PATH.mkdir(exist_ok=True)
    except OSError:
        return 1  # DIR_ERROR
    try:
        CONFIG_FILE_PATH.touch(exist_ok=True)
    except OSError:
        return 2  # FILE_ERROR
    return 0  # SUCCESS

def set_config(key: str, value: str) -> int:
    """Set a config value in the config file."""
    config = configparser.ConfigParser()
    if CONFIG_FILE_PATH.exists():
        config.read(CONFIG_FILE_PATH)
    if "General" not in config:
        config["General"] = {}
    config["General"][key] = value
    try:
        with CONFIG_FILE_PATH.open("w") as f:
            config.write(f)
    except OSError:
        return 3  # WRITE_ERROR
    return 0  # SUCCESS

def get_config(key: str) -> str | None:
    """Get a config value from the config file."""
    config = configparser.ConfigParser()
    if CONFIG_FILE_PATH.exists():
        config.read(CONFIG_FILE_PATH)
        return config.get("General", key, fallback=None)
    return None