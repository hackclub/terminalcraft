"""
Save system for The Signal Cartographer
Handles saving and loading game progress and state
"""

import json
import os
import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path


class SaveSystem:
    """
    Manages saving and loading of game state and player progress
    """
    
    def __init__(self, save_dir: str = "saves"):
        """Initialize save system with specified save directory"""
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        # Default save file name
        self.auto_save_file = "autosave.json"
        self.last_save_time = None
        
        # Track what needs to be saved
        self.game_state = None
    
    def set_game_state(self, game_state):
        """Set reference to the main game state for auto-save"""
        self.game_state = game_state
    
    def create_save_data(self, game_state) -> Dict[str, Any]:
        """Create a dictionary containing all saveable game data"""
        save_data = {
            "version": "1.0.1",
            "timestamp": datetime.datetime.now().isoformat(),
            
            # Core game state
            "game_state": {
                "current_sector": game_state.get_current_sector(),
                "frequency_range": game_state.get_frequency_range(),
            },
            
            # Player progress
            "progress": {
                "sectors_discovered": self._get_discovered_sectors(game_state),
                "signals_found": self._get_found_signals(game_state),
                "signals_analyzed": self._get_analyzed_signals(game_state),
                "total_scan_count": getattr(game_state, 'total_scan_count', 0),
                "total_analysis_count": getattr(game_state, 'total_analysis_count', 0),
            },
            
            # Focused signal (if any)
            "focused_signal": self._serialize_signal(game_state.get_focused_signal()),
            
            # Session statistics
            "statistics": {
                "play_time_minutes": getattr(game_state, 'play_time_minutes', 0),
                "session_start": getattr(game_state, 'session_start', datetime.datetime.now().isoformat()),
                "last_command": getattr(game_state, 'last_command', ""),
            },
            
            # Settings
            "settings": {
                "auto_save_enabled": True,
                "last_save_location": str(self.save_dir),
            }
        }
        
        return save_data
    
    def save_game(self, game_state, filename: str = None) -> bool:
        """
        Save the current game state to a file
        Returns True if successful, False otherwise
        """
        try:
            # Use provided filename or default auto-save
            if filename is None:
                filename = self.auto_save_file
            
            # Ensure .json extension
            if not filename.endswith('.json'):
                filename += '.json'
            
            save_path = self.save_dir / filename
            save_data = self.create_save_data(game_state)
            
            # Write to file with pretty formatting
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            self.last_save_time = datetime.datetime.now()
            return True
            
        except Exception as e:
            print(f"Save error: {e}")
            return False
    
    def load_game(self, filename: str = None) -> Optional[Dict[str, Any]]:
        """
        Load game state from a file
        Returns save data dictionary if successful, None otherwise
        """
        try:
            # Use provided filename or default auto-save
            if filename is None:
                filename = self.auto_save_file
            
            # Ensure .json extension
            if not filename.endswith('.json'):
                filename += '.json'
            
            save_path = self.save_dir / filename
            
            if not save_path.exists():
                return None
            
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            return save_data
            
        except Exception as e:
            print(f"Load error: {e}")
            return None
    
    def apply_save_data(self, save_data: Dict[str, Any], game_state) -> bool:
        """
        Apply loaded save data to the game state
        Returns True if successful, False otherwise
        """
        try:
            # Apply core game state
            if "game_state" in save_data:
                gs = save_data["game_state"]
                if "current_sector" in gs:
                    game_state.set_current_sector(gs["current_sector"])
                if "frequency_range" in gs:
                    game_state.set_frequency_range(tuple(gs["frequency_range"]))
            
            # Apply focused signal
            if "focused_signal" in save_data and save_data["focused_signal"]:
                signal = self._deserialize_signal(save_data["focused_signal"])
                if signal:
                    game_state.set_focused_signal(signal)
            
            # Apply progress data
            if "progress" in save_data:
                progress = save_data["progress"]
                game_state.total_scan_count = progress.get("total_scan_count", 0)
                game_state.total_analysis_count = progress.get("total_analysis_count", 0)
                
                # Store discovered sectors and found signals for future reference
                game_state.discovered_sectors = progress.get("sectors_discovered", [])
                game_state.found_signals = progress.get("signals_found", {})
                game_state.analyzed_signals = progress.get("signals_analyzed", [])
            
            # Apply statistics
            if "statistics" in save_data:
                stats = save_data["statistics"]
                game_state.play_time_minutes = stats.get("play_time_minutes", 0)
                game_state.session_start = stats.get("session_start", datetime.datetime.now().isoformat())
                game_state.last_command = stats.get("last_command", "")
            
            return True
            
        except Exception as e:
            print(f"Error applying save data: {e}")
            return False
    
    def get_save_files(self) -> List[Dict[str, str]]:
        """
        Get list of available save files with metadata
        Returns list of dictionaries with file info
        """
        save_files = []
        
        try:
            for file_path in self.save_dir.glob("*.json"):
                try:
                    # Get file modification time
                    mod_time = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    # Try to read save data for more info
                    save_info = {
                        "filename": file_path.name,
                        "path": str(file_path),
                        "modified": mod_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "size_kb": round(file_path.stat().st_size / 1024, 1)
                    }
                    
                    # Try to get additional info from save file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        if "timestamp" in data:
                            save_info["save_time"] = data["timestamp"]
                        if "game_state" in data and "current_sector" in data["game_state"]:
                            save_info["sector"] = data["game_state"]["current_sector"]
                        if "progress" in data:
                            save_info["signals_found"] = len(data["progress"].get("signals_found", {}))
                    
                    except:
                        # If we can't read the file, just use basic info
                        pass
                    
                    save_files.append(save_info)
                    
                except Exception:
                    # Skip files we can't read
                    continue
        
        except Exception as e:
            print(f"Error listing save files: {e}")
        
        # Sort by modification time (newest first)
        save_files.sort(key=lambda x: x["modified"], reverse=True)
        return save_files
    
    def delete_save(self, filename: str) -> bool:
        """Delete a save file"""
        try:
            if not filename.endswith('.json'):
                filename += '.json'
            
            save_path = self.save_dir / filename
            if save_path.exists():
                save_path.unlink()
                return True
            return False
            
        except Exception as e:
            print(f"Error deleting save file: {e}")
            return False
    
    def auto_save(self) -> bool:
        """Perform an automatic save if game state is available"""
        if self.game_state:
            return self.save_game(self.game_state, self.auto_save_file)
        return False
    
    def get_last_save_info(self) -> Dict[str, str]:
        """Get information about the last save"""
        if self.last_save_time:
            return {
                "time": self.last_save_time.strftime("%H:%M:%S"),
                "date": self.last_save_time.strftime("%Y-%m-%d"),
                "file": self.auto_save_file
            }
        return {}
    
    # Helper methods for data serialization
    def _serialize_signal(self, signal) -> Optional[Dict[str, Any]]:
        """Convert a Signal object to a dictionary"""
        if signal is None:
            return None
        
        return {
            "id": signal.id,
            "frequency": signal.frequency,
            "strength": signal.strength,
            "modulation": signal.modulation,
            "sector": getattr(signal, 'sector', ''),
            "stability": getattr(signal, 'stability', 1.0),
            "signature": getattr(signal, 'signature', ''),
            "decoded": getattr(signal, 'decoded', False),
        }
    
    def _deserialize_signal(self, data: Dict[str, Any]):
        """Convert a dictionary back to a Signal object"""
        if not data:
            return None
        
        try:
            from ..signal_system import Signal
            return Signal(
                id=data.get("id", ""),
                frequency=data.get("frequency", 0.0),
                strength=data.get("strength", 0.0),
                modulation=data.get("modulation", ""),
                sector=data.get("sector", ""),
                stability=data.get("stability", 1.0),
                signature=data.get("signature", ""),
                decoded=data.get("decoded", False),
            )
        except Exception as e:
            print(f"Error deserializing signal: {e}")
            return None
    
    def _get_discovered_sectors(self, game_state) -> List[str]:
        """Get list of sectors that have been discovered/scanned"""
        # For now, return the current sector - can be expanded later
        discovered = getattr(game_state, 'discovered_sectors', [])
        current = game_state.get_current_sector()
        if current not in discovered:
            discovered.append(current)
        return discovered
    
    def _get_found_signals(self, game_state) -> Dict[str, List[Dict]]:
        """Get dictionary of signals found per sector"""
        # This will be expanded as the signal tracking system develops
        return getattr(game_state, 'found_signals', {})
    
    def _get_analyzed_signals(self, game_state) -> List[str]:
        """Get list of signal IDs that have been analyzed"""
        return getattr(game_state, 'analyzed_signals', []) 