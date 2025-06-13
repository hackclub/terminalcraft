"""
Configuration management - because nobody likes hardcoded settings!
Handles all the user preferences and app settings.

Note to self: Maybe add encryption for sensitive stuff later?
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

class Config:
    """Manages all TermiCast settings - your preferences matter!"""
    
    def __init__(self):
        # Set up our file locations - keeping everything tidy
        self.config_dir = Path.home() / ".termicast"
        self.config_file = self.config_dir / "config.json"
        self.log_dir = self.config_dir / "logs"
        self.data_dir = Path("data")
        self.tle_dir = Path("tle")
        
        # Reasonable defaults - I picked New York because... why not?
        self.defaults = {
            "default_location": {
                "name": "New York, NY",
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            "satellites": {
                # Weather satellites that actually work well
                "weather_satellites": [
                    "NOAA-18",    # Old but reliable
                    "NOAA-19",    # Also solid
                    "NOAA-20",    # Newest NOAA bird
                    "METOP-A",    # European satellites
                    "METOP-B",    # are pretty good too
                    "METOP-C"     # Latest METOP
                ]
            },
            "prediction": {
                "forecast_days": 3,           # 3 days seems reasonable
                "min_elevation": 10.0,        # Below 10° is pretty low
                "pressure_trend_hours": 24    # 24h gives good trends
            },
            "sensor": {
                "enabled": False,             # Off by default
                "port": "/dev/ttyUSB0",      # Common Linux serial port
                "baudrate": 9600             # Standard rate
            },
            "display": {
                "colors": True,               # Pretty colors!
                "unicode": True,              # Fancy characters
                "table_style": "grid"        # Looks nice
            },
            # My additions for better UX
            "user_preferences": {
                "show_tips": True,           # Helpful hints
                "compact_mode": False,       # More info vs cleaner display
                "emoji_level": "normal"      # none, minimal, normal, extra
            }
        }
        
        # Make sure our directories exist
        self._ensure_directories()
        # Load up the actual config
        self._config = self._load_config()
    
    def _ensure_directories(self):
        """Make sure all our folders exist - housekeeping stuff"""
        try:
            self.config_dir.mkdir(exist_ok=True)
            self.log_dir.mkdir(exist_ok=True)
            self.data_dir.mkdir(exist_ok=True)
            self.tle_dir.mkdir(exist_ok=True)
        except OSError as e:
            # Fallback if home directory access fails
            print(f"Warning: Couldn't create config directories: {e}")
            print("Using current directory for config storage")
            self.config_dir = Path(".")
            self.config_file = Path("termicast_config.json")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load settings from file, or create defaults if needed"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    
                # Merge user config with defaults (defaults win for new keys)
                merged_config = {}
                for key, default_value in self.defaults.items():
                    if isinstance(default_value, dict) and key in user_config:
                        # Deep merge for nested dictionaries
                        merged_config[key] = {**default_value, **user_config[key]}
                    elif key in user_config:
                        merged_config[key] = user_config[key]
                    else:
                        merged_config[key] = default_value
                        
                return merged_config
                
            except (json.JSONDecodeError, IOError, UnicodeDecodeError) as e:
                print(f"Config file is corrupted or unreadable: {e}")
                print("Using defaults and backing up old config...")
                
                # Backup the broken config
                backup_file = self.config_file.with_suffix('.json.backup')
                try:
                    self.config_file.rename(backup_file)
                    print(f"Old config saved as: {backup_file}")
                except OSError:
                    pass  # Oh well, we tried
                    
                return self.defaults.copy()
        else:
            # First run - save defaults and return them
            self.save_config(self.defaults)
            return self.defaults.copy()
    
    def get(self, key: str, default=None):
        """Get a config value using dot notation (e.g., 'sensor.enabled')"""
        keys = key.split('.')
        current_value = self._config
        
        # Navigate through nested dictionaries
        for k in keys:
            if isinstance(current_value, dict) and k in current_value:
                current_value = current_value[k]
            else:
                # Key not found, return default
                return default
                
        return current_value
    
    def set(self, key: str, value: Any):
        """Set a config value and save it immediately"""
        keys = key.split('.')
        current_dict = self._config
        
        # Navigate to the right nested dictionary
        for k in keys[:-1]:
            if k not in current_dict:
                current_dict[k] = {}
            current_dict = current_dict[k]
            
        # Set the final value
        current_dict[keys[-1]] = value
        
        # Save immediately - no point in keeping changes in memory
        self.save_config(self._config)
    
    def get_all(self) -> Dict[str, Any]:
        """Get the entire config - useful for debugging"""
        return self._config.copy()
    
    def reset_to_defaults(self):
        """Reset everything back to defaults - nuclear option"""
        self._config = self.defaults.copy()
        self.save_config(self._config)
        print("Configuration reset to defaults")
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file - with error handling"""
        try:
            # Make sure the directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write with nice formatting
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        except (IOError, OSError) as e:
            print(f"Couldn't save configuration: {e}")
            print("Your settings might not persist between sessions")
        except Exception as e:
            print(f"Unexpected error saving config: {e}")

# The one and only config instance - global but contained
config = Config() 

def save_config():
    """Standalone function to save the global config instance"""
    config.save_config(config._config) 