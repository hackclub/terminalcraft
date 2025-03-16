"""
Settings module for Veritaminal

Handles border settings, game configurations, and contextual information
for different game scenarios.
"""

import random
import logging
from .ui import TerminalUI  # Import TerminalUI for consistent styling

logger = logging.getLogger(__name__)

# Predefined border settings for the game
BORDER_SETTINGS = [
    {
        "id": "eastokan_westoria",
        "name": "Eastokan-Westoria Border",
        "situation": "Tense relations due to recent trade disputes. Increased scrutiny on business travelers.",
        "description": "The border between the industrial nation of Eastokan and the agricultural country of Westoria. Recent trade disputes have heightened tensions.",
        "document_requirements": [
            "Permit must start with 'P' followed by 4 digits",
            "Travelers must have both first and last names",
            "Business travelers require a trade visa stamp"
        ],
        "common_issues": [
            "Forged business credentials",
            "Expired permits",
            "Identity mismatches in documentation"
        ]
    },
    {
        "id": "northland_southoria",
        "name": "Northland-Southoria Border",
        "situation": "Post-conflict reconciliation with humanitarian crisis. Focus on refugee documentation.",
        "description": "Following the peace treaty ending the 5-year conflict, this border handles many refugees and humanitarian workers.",
        "document_requirements": [
            "Permit must start with 'P' followed by 4 digits",
            "Humanitarian workers need special H-class authorization",
            "Refugee documents must include origin verification"
        ],
        "common_issues": [
            "Missing refugee documentation",
            "Impersonation of humanitarian workers",
            "Forged origin documentation"
        ]
    },
    {
        "id": "oceania_continent",
        "name": "Oceania-Continent Ferry Checkpoint",
        "situation": "Tourism boom with increasing smuggling concerns. Focus on contraband detection.",
        "description": "This busy checkpoint manages traffic between the island nation of Oceania and the mainland Continent. Tourism is booming, but smuggling is on the rise.",
        "document_requirements": [
            "Permit must start with 'P' followed by 4 digits",
            "Tourist visas require verification stamps",
            "Commercial transport requires cargo manifests"
        ],
        "common_issues": [
            "Overstayed tourist visas",
            "Undeclared commercial activity",
            "Falsified transport documentation"
        ]
    }
]

class SettingsManager:
    """
    Manages game settings and border configurations.
    """
    def __init__(self):
        """
        Initialize the settings manager.
        """
        self.current_setting = None
        self.available_settings = BORDER_SETTINGS
        self.custom_rules = []
        self.ui = TerminalUI()  # Create UI instance for styling
        
    def get_available_settings(self):
        """
        Get all available border settings.
        
        Returns:
            list: List of available border settings.
        """
        return self.available_settings
    
    def select_setting(self, setting_id):
        """
        Select a border setting by ID.
        
        Args:
            setting_id (str): The ID of the setting to select.
            
        Returns:
            dict: The selected setting.
        """
        for setting in self.available_settings:
            if setting["id"] == setting_id:
                self.current_setting = setting
                return setting
                
        # If ID not found, default to the first setting
        logger.warning(f"Setting ID '{setting_id}' not found. Using default.")
        self.current_setting = self.available_settings[0]
        return self.current_setting
    
    def get_current_setting(self):
        """
        Get the current border setting.
        
        Returns:
            dict: The current setting.
        """
        if not self.current_setting:
            # If no setting is selected, use the first one
            self.current_setting = self.available_settings[0]
            
        return self.current_setting
    
    def add_custom_rule(self, rule_description):
        """
        Add a custom rule to the current setting.
        
        Args:
            rule_description (str): Description of the rule.
            
        Returns:
            bool: True if the rule was added successfully.
        """
        if rule_description not in self.custom_rules:
            self.custom_rules.append(rule_description)
            return True
        return False
    
    def get_all_rules(self):
        """
        Get all rules for the current setting.
        
        Returns:
            list: Combined list of default and custom rules.
        """
        if not self.current_setting:
            self.current_setting = self.available_settings[0]
            
        return self.current_setting["document_requirements"] + self.custom_rules
    
    def get_setting_context(self):
        """
        Get a formatted context string for the current setting.
        
        Returns:
            str: A formatted context string.
        """
        if not self.current_setting:
            self.current_setting = self.available_settings[0]
            
        context = []
        context.append(f"BORDER: {self.current_setting['name']}")
        context.append(f"SITUATION: {self.current_setting['situation']}")
        
        context.append("\nDOCUMENT REQUIREMENTS:")
        for req in self.current_setting["document_requirements"]:
            context.append(f"- {req}")
        
        if self.custom_rules:
            context.append("\nADDITIONAL RULES:")
            for rule in self.custom_rules:
                context.append(f"- {rule}")
                
        return "\n".join(context)
        
    def display_current_setting(self):
        """
        Display information about the current setting with consistent styling.
        """
        if not self.current_setting:
            self.current_setting = self.available_settings[0]
            
        self.ui.clear_screen()
        self.ui.draw_border(f"BORDER: {self.current_setting['name']}")
        
        print(self.ui.colored_text(f"SITUATION:", 'header'))
        print(self.ui.colored_text(f"{self.current_setting['situation']}\n", 'value'))
        
        print(self.ui.colored_text("DOCUMENT REQUIREMENTS:", 'header'))
        for req in self.current_setting["document_requirements"]:
            print(self.ui.colored_text(f"- {req}", 'value'))
        
        print(self.ui.colored_text("\nCOMMON ISSUES:", 'header'))
        for issue in self.current_setting["common_issues"]:
            print(self.ui.colored_text(f"- {issue}", 'value'))
            
        if self.custom_rules:
            print(self.ui.colored_text("\nADDITIONAL RULES:", 'header'))
            for rule in self.custom_rules:
                print(self.ui.colored_text(f"- {rule}", 'value'))