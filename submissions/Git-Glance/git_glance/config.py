from typing import TypedDict, List
from pathlib import Path
from platformdirs import user_config_dir
from datetime import datetime
import json

APP_NAME = "git-glance"
# CONFIG_FILE = "./config.json"

class RepoConfig(TypedDict):
    path: str
    alias: str
    added: str

class Config(TypedDict):
    version: int
    repos: List[RepoConfig]

def get_config_path() -> Path:
    config_dir = Path(user_config_dir(APP_NAME))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"

def load_config() -> Config:
    config_path = get_config_path()
    if not config_path.exists():
        default_config = {
            "version": 1,
            "repos": [],
        }
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        return default_config
    with open(config_path, 'r') as f:
        return json.load(f)
    
def save_config(config: Config):
    config_path = get_config_path()
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

def add_repo(path: str, alias: str) -> None:
    config = load_config()
    repos = config["repos"]
    path = str(Path(path).expanduser().resolve())

    for repo in repos:
        if repo["path"] == path or repo["alias"] == alias:
            raise ValueError(f"Repo with path '{path}' or alias '{alias}' already exists.")
    
    repos.append({
        "path": path,
        "alias": alias,
        "added": datetime.now().isoformat()
    })

    save_config(config)

def remove_repo(path: str | None = None, alias: str | None = None):
    config = load_config()
    repos = config["repos"]
    new_repos = [
        repo for repo in repos
        if not (
            (path and repo["path"] == str(Path(path).expanduser().resolve())) or
            (alias and repo["alias"] == alias)
        )
    ]

    if len(new_repos) == len(repos):
        raise ValueError("No matching repo found to remove.")
    
    config["repos"] = new_repos
    save_config(config)
