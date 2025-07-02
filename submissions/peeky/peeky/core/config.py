"""
Configuration management for Peeky.

This module provides functions for managing configuration and secrets.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

CONFIG_DIR = Path.home() / '.peeky'
CONFIG_FILE = CONFIG_DIR / 'config.json'

def ensure_config_dir() -> None:
    """
    Ensure the configuration directory exists.
    """
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_config() -> Dict[str, Any]:
    """
    Load the configuration from the config file.
    
    Returns:
        Dict with configuration values
    """
    ensure_config_dir()
    
    if not CONFIG_FILE.exists():
        return {}
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_config(config: Dict[str, Any]) -> None:
    """
    Save the configuration to the config file.
    
    Args:
        config: Dict with configuration values
    """
    ensure_config_dir()
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_api_key(service: str) -> Optional[str]:
    """
    Get an API key for a specific service.
    
    Args:
        service: Service name (e.g., 'whois')
        
    Returns:
        API key string or None if not set
    """
    env_var = f"PEEKY_{service.upper()}_API_KEY"
    if env_var in os.environ:
        return os.environ[env_var]
    
    config = load_config()
    return config.get('api_keys', {}).get(service)

def set_api_key(service: str, api_key: str) -> None:
    """
    Set an API key for a specific service.
    
    Args:
        service: Service name (e.g., 'whois')
        api_key: The API key to store
    """
    config = load_config()
    
    if 'api_keys' not in config:
        config['api_keys'] = {}
    
    config['api_keys'][service] = api_key
    save_config(config) 