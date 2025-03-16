"""
Gameplay module for Veritaminal

Handles the core gameplay mechanics including document generation,
verification rules, and scoring.
"""

import random
import logging
from .api import (generate_text, generate_document_error, generate_consistent_backstory, 
                 generate_document_for_setting, ai_judge_document)
from .memory import MemoryManager
from .settings import SettingsManager

logger = logging.getLogger(__name__)

class Rule:
    """
    Represents a verification rule for documents.
    """
    def __init__(self, name, description, check_function):
        """
        Initialize a rule.
        
        Args:
            name (str): Name of the rule.
            description (str): Description of the rule.
            check_function (callable): Function that checks if a document follows this rule.
        """
        self.name = name
        self.description = description
        self.check_function = check_function

    def check(self, document):
        """
        Check if a document follows this rule.
        
        Args:
            document (dict): The document to check.
            
        Returns:
            bool: True if the document follows this rule, False otherwise.
        """
        return self.check_function(document)


class GameplayManager:
    """
    Manages the gameplay mechanics.
    """
    def __init__(self):
        """
        Initialize the gameplay manager.
        """
        self.score = 0
        self.current_document = None
        self.rules = []
        self.memory_manager = MemoryManager()
        self.settings_manager = SettingsManager()
        self._initialize_rules()
        self.ai_judgment = None  # Will store the AI's judgment of the current document
        self.game_completed = False  # Track if player has completed a full game

    def _initialize_rules(self):
        """
        Initialize the basic verification rules.
        """
        # Rule 1: Permit must start with 'P'
        self.rules.append(
            Rule(
                "Permit Format",
                "All permits must start with the letter 'P'.",
                lambda doc: doc["permit"].startswith("P")
            )
        )
        
        # Rule 2: Permit must be followed by 4 digits
        self.rules.append(
            Rule(
                "Permit Number",
                "Permit numbers must have 4 digits after the 'P'.",
                lambda doc: len(doc["permit"]) == 5 and doc["permit"][1:].isdigit()
            )
        )
        
        # Rule 3: Name must have a first and last name
        self.rules.append(
            Rule(
                "Name Format",
                "Traveler names must include both first and last names.",
                lambda doc: len(doc["name"].split()) >= 2
            )
        )

    def add_rule(self, rule):
        """
        Add a new rule.
        
        Args:
            rule (Rule): The rule to add.
        """
        self.rules.append(rule)
        self.memory_manager.add_rule_change(rule.description)
        
    def initialize_game(self, setting_id=None):
        """
        Initialize a new game with the selected setting.
        
        Args:
            setting_id (str, optional): ID of the border setting to use.
                                       If None, the player will be prompted to choose.
        
        Returns:
            dict: The selected setting.
        """
        # Reset game state
        self.score = 0
        self.current_document = None
        self.game_completed = False
        
        # Reset memory but keep used names to prevent repetition across games
        used_names = self.memory_manager.memory["used_names"]
        self.memory_manager.reset_memory()
        self.memory_manager.memory["used_names"] = used_names
        
        # Select a setting
        if setting_id:
            setting = self.settings_manager.select_setting(setting_id)
        else:
            # Default to the first setting if none specified
            setting = self.settings_manager.get_current_setting()
        
        # Initialize memory with the selected setting
        self.memory_manager.set_border_setting(setting)
        self.memory_manager.add_narrative_event(
            f"You begin your shift at the {setting['name']}.", 
            "start"
        )
        
        return setting
        
    def generate_document(self):
        """
        Generate a new document based on the current setting.
        
        Returns:
            dict: The generated document.
        """
        # Get the current setting
        setting = self.settings_manager.get_current_setting()
        
        # Get used names context to avoid repetition
        used_names_context = self.memory_manager.get_used_names_context()
        
        # Generate a document for this setting with name history awareness
        name, permit, backstory, additional_fields = generate_document_for_setting(
            setting, 
            used_names_context=used_names_context
        )
        
        # Create the document
        document = {
            "name": name,
            "permit": permit,
            "backstory": backstory,
            **additional_fields  # Include any additional fields
        }
        
        # Use AI to judge the document
        setting_context = self.settings_manager.get_setting_context()
        memory_context = self.memory_manager.get_memory_context()
        
        self.ai_judgment = ai_judge_document(document, setting_context, memory_context)
        
        # Store the AI's judgment decision in the document
        document["is_valid"] = self.ai_judgment["decision"] == "approve"
        
        self.current_document = document
        return document
    
    def check_document_validity(self, document):
        """
        Check if a document is valid according to all rules.
        For backward compatibility - now just returns the AI judgment.
        
        Args:
            document (dict): The document to check.
            
        Returns:
            bool: True if the document is valid, False otherwise.
        """
        if self.ai_judgment:
            return self.ai_judgment["decision"] == "approve"
        
        # Fallback to rule-based checking if no AI judgment is available
        for rule in self.rules:
            if not rule.check(document):
                return False
        return True
    
    def make_decision(self, decision):
        """
        Make a decision on the current document.
        
        Args:
            decision (str): "approve" or "deny".
            
        Returns:
            tuple: (is_correct, points_earned)
        """
        if not self.current_document:
            logger.error("No current document to make a decision on.")
            return False, 0
        
        # Get the AI's recommended decision
        ai_decision = self.ai_judgment["decision"] if self.ai_judgment else "approve"
        
        # Decision is correct if it matches the AI's decision
        is_correct = decision == ai_decision
        
        # Calculate points - weight by AI confidence
        confidence = self.ai_judgment.get("confidence", 0.5) if self.ai_judgment else 0.5
        points = 1 * confidence if is_correct else 0
        self.score += points
        
        # Update game state based on decision
        self.update_game_state(decision, is_correct)
        
        # Store the decision in memory
        self.memory_manager.add_traveler(
            self.current_document, 
            decision, 
            is_correct, 
            self.ai_judgment if self.ai_judgment else {"decision": ai_decision, "reasoning": "No AI judgment available"}
        )
        
        return is_correct, points
    
    def update_game_state(self, decision, is_correct):
        """
        Update the game state based on the player's decision.
        
        Args:
            decision (str): The player's decision.
            is_correct (bool): Whether the decision was correct.
        """
        state_updates = {}
        
        # Update corruption/trust based on decision
        if decision == "approve" and not is_correct:
            # Incorrectly approving increases corruption
            state_updates["corruption"] = self.memory_manager.memory["game_state"].get("corruption", 0) + 1
        elif decision == "deny" and not is_correct:
            # Incorrectly denying decreases trust
            state_updates["trust"] = self.memory_manager.memory["game_state"].get("trust", 0) - 1
            
        # Apply the updates
        if state_updates:
            self.memory_manager.update_game_state(state_updates)
    
    def advance_day(self):
        """
        Advance to the next day in the game.
        
        Returns:
            str: The day announcement.
        """
        self.memory_manager.advance_day()
        day = self.memory_manager.memory["game_state"]["day"]
        
        # Check if player has completed day 10
        if day > 10:
            self.game_completed = True
        
        # Day-specific events
        if day == 3:
            message = "Day 3: New regulations have been implemented. All permits must now have valid seals."
            self.memory_manager.add_rule_change("All permits must have valid seals.")
        elif day == 7:
            message = "Day 7: Border tensions are rising. Security has been tightened."
            # Could add special rule or event here
        else:
            message = f"Day {day}: Another day at the {self.settings_manager.get_current_setting()['name']} begins."
            
        self.memory_manager.add_narrative_event(message, "day_change")
        return message
    
    def get_all_rules(self):
        """
        Get all current rules.
        
        Returns:
            list: List of all rules.
        """
        return self.rules
    
    def get_score(self):
        """
        Get the current score.
        
        Returns:
            int: The current score.
        """
        return self.score
    
    def get_ai_reasoning(self):
        """
        Get the AI's reasoning for the current judgment.
        
        Returns:
            str: The AI's reasoning.
        """
        if self.ai_judgment and "reasoning" in self.ai_judgment:
            return self.ai_judgment["reasoning"]
        return "No reasoning available."
    
    def save_game(self):
        """
        Save the current game state.
        
        Returns:
            bool: True if save was successful.
        """
        return self.memory_manager.save_game()
    
    def load_game(self, filepath):
        """
        Load a saved game.
        
        Args:
            filepath (str): Path to the save file.
            
        Returns:
            bool: True if load was successful.
        """
        success = self.memory_manager.load_game(filepath)
        if success:
            # Update score and other gameplay state from the loaded memory
            self.score = 0  # Reset score, could be calculated from decisions if needed
            
            # Select the saved setting
            if self.memory_manager.memory["border_setting"]:
                setting_id = self.memory_manager.memory["border_setting"].get("id")
                if setting_id:
                    self.settings_manager.select_setting(setting_id)
            
            # Set game_completed flag if past day 10
            if self.memory_manager.memory["game_state"]["day"] > 10:
                self.game_completed = True
        
        return success
