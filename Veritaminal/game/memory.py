"""
Memory module for Veritaminal

Handles the storage of game history, narrative state, and player decisions.
Maintains continuity across game sessions and implements the AI memory system.
"""

import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Manages the game's memory and narrative continuity.
    """
    def __init__(self, save_dir="saves"):
        """
        Initialize the memory manager.
        
        Args:
            save_dir (str): Directory to store save files.
        """
        self.save_dir = save_dir
        self.memory = {
            "border_setting": None,       # Selected border/country setting
            "game_state": {
                "day": 1,
                "corruption": 0,
                "trust": 0
            },
            "traveler_history": [],       # List of previous travelers
            "decisions": [],              # List of player decisions
            "narrative_events": [],       # Key narrative events
            "rule_changes": [],           # History of rule changes
            "used_names": set()           # Track used names to prevent repetition
        }
        self._ensure_save_directory()
        
    def _ensure_save_directory(self):
        """
        Ensure the save directory exists.
        """
        save_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.save_dir)
        if not os.path.exists(save_path):
            try:
                os.makedirs(save_path)
                logger.info(f"Created save directory at {save_path}")
            except Exception as e:
                logger.error(f"Failed to create save directory: {e}")
                
    def set_border_setting(self, setting):
        """
        Set the border/country setting for the game.
        
        Args:
            setting (dict): Contains setting info like country names, political situation, etc.
        """
        self.memory["border_setting"] = setting
        
    def add_traveler(self, traveler_data, decision, is_correct, ai_judgment):
        """
        Add a traveler to the history with the player's decision.
        
        Args:
            traveler_data (dict): The traveler document data.
            decision (str): The player's decision (approve/deny).
            is_correct (bool): Whether the decision was correct.
            ai_judgment (dict): AI's evaluation of the document.
        """
        # Add name to used names set
        self.memory["used_names"].add(traveler_data["name"])
        
        # Add timestamp for when this traveler was processed
        timestamp = datetime.now().isoformat()
        
        # Add to traveler history
        self.memory["traveler_history"].append({
            "traveler": traveler_data,
            "timestamp": timestamp,
            "day": self.memory["game_state"]["day"]
        })
        
        # Add to decisions history
        self.memory["decisions"].append({
            "traveler_name": traveler_data["name"],
            "decision": decision,
            "correct": is_correct,
            "ai_judgment": ai_judgment,
            "timestamp": timestamp,
            "day": self.memory["game_state"]["day"]
        })
        
        # Limit the history size to prevent excessive token usage
        if len(self.memory["traveler_history"]) > 10:
            self.memory["traveler_history"] = self.memory["traveler_history"][-10:]
        if len(self.memory["decisions"]) > 10:
            self.memory["decisions"] = self.memory["decisions"][-10:]
    
    def add_narrative_event(self, event_text, event_type):
        """
        Add a narrative event to the history.
        
        Args:
            event_text (str): Description of the event.
            event_type (str): Type of event (e.g., "milestone", "rule_change", "special").
        """
        self.memory["narrative_events"].append({
            "text": event_text,
            "type": event_type,
            "day": self.memory["game_state"]["day"],
            "timestamp": datetime.now().isoformat()
        })
        
        # Limit narrative events to prevent token bloat
        if len(self.memory["narrative_events"]) > 15:
            self.memory["narrative_events"] = self.memory["narrative_events"][-15:]
    
    def add_rule_change(self, rule_description):
        """
        Add a rule change to the history.
        
        Args:
            rule_description (str): Description of the rule change.
        """
        self.memory["rule_changes"].append({
            "description": rule_description,
            "day": self.memory["game_state"]["day"],
            "timestamp": datetime.now().isoformat()
        })
    
    def update_game_state(self, state_updates):
        """
        Update the game state.
        
        Args:
            state_updates (dict): Updates to apply to the game state.
        """
        self.memory["game_state"].update(state_updates)
    
    def advance_day(self):
        """
        Advance to the next day.
        """
        self.memory["game_state"]["day"] += 1
    
    def get_memory_context(self):
        """
        Get a formatted context string representing the current memory state
        for use in AI prompts.
        
        Returns:
            str: A formatted context string.
        """
        context = []
        
        # Add border setting
        if self.memory["border_setting"]:
            context.append(f"BORDER SETTING: {self.memory['border_setting']['name']}")
            context.append(f"POLITICAL SITUATION: {self.memory['border_setting']['situation']}")
            
        # Add current game state
        context.append(f"CURRENT DAY: {self.memory['game_state']['day']}")
        context.append(f"CORRUPTION LEVEL: {self.memory['game_state']['corruption']}")
        context.append(f"TRUST LEVEL: {self.memory['game_state']['trust']}")
        
        # Add recent rules (if any)
        if self.memory["rule_changes"]:
            context.append("\nCURRENT RULES:")
            for rule in self.memory["rule_changes"][-3:]:  # Last 3 rules only
                context.append(f"- {rule['description']}")
        
        # Add recent narrative events
        if self.memory["narrative_events"]:
            context.append("\nRECENT EVENTS:")
            for event in self.memory["narrative_events"][-3:]:  # Last 3 events only
                context.append(f"- Day {event['day']}: {event['text']}")
        
        # Add recent decisions
        if self.memory["decisions"]:
            context.append("\nRECENT DECISIONS:")
            for decision in self.memory["decisions"][-5:]:  # Last 5 decisions only
                correct_str = "correctly" if decision["correct"] else "incorrectly"
                context.append(f"- {decision['traveler_name']} was {decision['decision']}ed {correct_str}")
        
        return "\n".join(context)
    
    def get_used_names_context(self):
        """
        Get a list of previously used traveler names to avoid repetition.
        
        Returns:
            str: A formatted string with previously used names.
        """
        if not self.memory["used_names"]:
            return "No previous travelers processed."
        
        names_list = list(self.memory["used_names"])
        # Limit to most recent 20 names to avoid token bloat
        if len(names_list) > 20:
            names_list = names_list[-20:]
        
        return "Previously encountered travelers: " + ", ".join(names_list) + ". Please generate a new unique name not on this list."
    
    def save_game(self, filename=None):
        """
        Save the current game state to a file.
        
        Args:
            filename (str, optional): Filename to save to. If None, a timestamped name is used.
        
        Returns:
            bool: True if save was successful, False otherwise.
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"veritaminal_save_{timestamp}.json"
            
        save_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                self.save_dir, filename)
        
        try:
            # Convert used_names set to list for JSON serialization
            memory_copy = self.memory.copy()
            memory_copy["used_names"] = list(self.memory["used_names"])
            
            with open(save_path, 'w') as f:
                json.dump(memory_copy, f, indent=2)
            logger.info(f"Game saved to {save_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save game: {e}")
            return False
    
    def load_game(self, filepath):
        """
        Load a saved game from a file.
        
        Args:
            filepath (str): Path to the save file.
        
        Returns:
            bool: True if load was successful, False otherwise.
        """
        try:
            with open(filepath, 'r') as f:
                loaded_memory = json.load(f)
                
            # Convert used_names list back to set
            if "used_names" in loaded_memory:
                loaded_memory["used_names"] = set(loaded_memory["used_names"])
            else:
                # Handle older save files that don't have used_names
                loaded_memory["used_names"] = set()
                # Try to reconstruct used_names from traveler history
                for traveler_record in loaded_memory.get("traveler_history", []):
                    if "traveler" in traveler_record and "name" in traveler_record["traveler"]:
                        loaded_memory["used_names"].add(traveler_record["traveler"]["name"])
            
            self.memory = loaded_memory
            logger.info(f"Game loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to load game: {e}")
            return False
    
    def reset_memory(self):
        """
        Reset the game memory to default values.
        """
        self.memory = {
            "border_setting": None,
            "game_state": {
                "day": 1,
                "corruption": 0,
                "trust": 0
            },
            "traveler_history": [],
            "decisions": [],
            "narrative_events": [],
            "rule_changes": [],
            "used_names": set()
        }