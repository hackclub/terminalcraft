"""
Configuration management for Meet-Zone
"""

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict, Any


@dataclass
class AppConfig:
    """Application configuration settings"""
    
    # Default settings
    default_duration: int = 30
    default_top_results: int = 3
    default_show_week: bool = False
    default_prioritize: str = "participants"  # or "duration"
    
    # UI settings
    theme: str = "dark"  # or "light"
    auto_save: bool = True
    remember_window_size: bool = True
    
    # Advanced settings
    min_meeting_gap: int = 15  # minutes between meetings
    max_meeting_duration: int = 480  # 8 hours
    working_days_only: bool = True
    
    # File paths
    last_roster_file: Optional[str] = None
    export_directory: Optional[str] = None


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.json"
        self.config = AppConfig()
        self.load_config()
    
    def _get_config_dir(self) -> Path:
        """Get the configuration directory"""
        if os.name == 'nt':  # Windows
            config_dir = Path(os.environ.get('APPDATA', '')) / "MeetZone"
        else:  # macOS/Linux
            config_dir = Path.home() / ".config" / "meetzone"
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def load_config(self) -> None:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                
                # Update config with loaded data
                for key, value in data.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
                        
            except Exception as e:
                print(f"Warning: Could not load config: {e}")
    
    def save_config(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(asdict(self.config), f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value"""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            if self.config.auto_save:
                self.save_config()
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self.config = AppConfig()
        self.save_config()


# Global config manager instance
config_manager = ConfigManager()