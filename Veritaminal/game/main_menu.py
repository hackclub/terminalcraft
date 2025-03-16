"""
Main menu module for Veritaminal

Handles the main menu system, game session management, and career progression.
"""

import os
import logging
import glob
from .gameplay import GameplayManager
from .settings import SettingsManager
from .ui import TerminalUI
from colorama import Fore, Back, Style

logger = logging.getLogger(__name__)

class MainMenuManager:
    """
    Manages the main menu and game sessions.
    """
    def __init__(self):
        """
        Initialize the main menu manager.
        """
        self.ui = TerminalUI()
        self.gameplay_manager = GameplayManager()
        self.settings_manager = SettingsManager()
        self.career_stats = {
            "games_completed": 0,
            "total_score": 0,
            "borders_served": set(),
            "highest_day_reached": 0
        }
        
    def display_main_menu(self):
        """
        Display the main menu options.
        
        Returns:
            str: The selected option.
        """
        self.ui.clear_screen()
        # Using UI's styled borders instead of plain text
        self.ui.draw_border("VERITAMINAL: Document Verification Game")
        
        # Display career stats if any games have been played
        if self.career_stats["games_completed"] > 0:
            print(self.ui.colored_text("CAREER STATISTICS".center(self.ui.width), 'title'))
            print(self.ui.colored_text(f"Games Completed: {self.career_stats['games_completed']}", 'value'))
            print(self.ui.colored_text(f"Total Career Score: {self.career_stats['total_score']}", 'value'))
            print(self.ui.colored_text(f"Borders Served: {len(self.career_stats['borders_served'])}", 'value'))
            print(self.ui.colored_text(f"Highest Day Reached: {self.career_stats['highest_day_reached']}", 'value'))
            print("\n" + self.ui.colored_text("=" * self.ui.width, 'border') + "\n")
        
        print(self.ui.colored_text("MAIN MENU".center(self.ui.width), 'title'))
        options = [
            "1. Start New Career",
            "2. Continue Previous Career",
            "3. View Border Settings",
            "4. View Game Rules",
            "5. Quit Game"
        ]
        
        for option in options:
            print(self.ui.colored_text(option.center(self.ui.width), 'value'))
            
        print("\n" + self.ui.colored_text("=" * self.ui.width, 'border'))
        
        choice = ""
        valid_choices = ["1", "2", "3", "4", "5"]
        while choice not in valid_choices:
            choice = input("\n" + self.ui.colored_text("Enter your selection (1-5): ", 'hint'))
            
        return choice
    
    def start_new_career(self):
        """
        Start a new game career with border selection.
        
        Returns:
            bool: True if a game was started, False otherwise.
        """
        # Display available border settings
        self.ui.clear_screen()
        self.ui.draw_border("SELECT YOUR BORDER ASSIGNMENT")
        
        settings = self.settings_manager.get_available_settings()
        for i, setting in enumerate(settings, 1):
            print(self.ui.colored_text(f"{i}. {setting['name']}", 'header'))
            print(self.ui.colored_text(f"   {setting['description']}\n", 'value'))
        
        # Let player choose a border or go back to main menu
        print(self.ui.colored_text("0. Return to Main Menu", 'command'))
        
        choice = -1
        while choice < 0 or choice > len(settings):
            try:
                choice = int(input("\n" + self.ui.colored_text(f"Enter your choice (0-{len(settings)}): ", 'hint')))
            except ValueError:
                print(self.ui.colored_text("Please enter a valid number.", 'error'))
                
        if choice == 0:
            return False  # Return to main menu
            
        # Initialize new game with selected border
        selected_setting = self.gameplay_manager.initialize_game(settings[choice-1]["id"])
        
        self.ui.clear_screen()
        print(self.ui.colored_text(f"\nYou selected: {selected_setting['name']}", 'header'))
        print(self.ui.colored_text(f"\n{selected_setting['description']}\n", 'value'))
        print(self.ui.colored_text("Current rules:", 'header'))
        for rule in self.gameplay_manager.settings_manager.get_all_rules():
            print(self.ui.colored_text(f"- {rule}", 'value'))
        
        input("\n" + self.ui.colored_text("Press Enter to begin your shift...", 'hint'))
        return True
    
    def continue_previous_career(self):
        """
        Load and continue a previous game career.
        
        Returns:
            bool: True if a game was loaded, False otherwise.
        """
        self.ui.clear_screen()
        self.ui.draw_border("LOAD PREVIOUS CAREER")
        
        # Get list of save files
        save_files = self._get_save_files()
        
        if not save_files:
            print(self.ui.colored_text("No saved games found.", 'error'))
            input("\n" + self.ui.colored_text("Press Enter to return to main menu...", 'hint'))
            return False
        
        print(self.ui.colored_text("Available saved games:", 'header'))
        for i, (save_path, save_name) in enumerate(save_files, 1):
            print(self.ui.colored_text(f"{i}. {save_name}", 'value'))
        
        print("\n" + self.ui.colored_text("0. Return to Main Menu", 'command'))
        
        choice = -1
        while choice < 0 or choice > len(save_files):
            try:
                choice = int(input("\n" + self.ui.colored_text(f"Enter your choice (0-{len(save_files)}): ", 'hint')))
            except ValueError:
                print(self.ui.colored_text("Please enter a valid number.", 'error'))
                
        if choice == 0:
            return False  # Return to main menu
            
        # Load the selected save
        save_path, _ = save_files[choice-1]
        success = self.gameplay_manager.load_game(save_path)
        
        if success:
            print(self.ui.colored_text(f"\nGame loaded successfully!", 'success'))
            
            # Display border info
            setting = self.gameplay_manager.settings_manager.get_current_setting()
            day = self.gameplay_manager.memory_manager.memory["game_state"]["day"]
            
            print(self.ui.colored_text(f"\nCurrent Assignment: {setting['name']}", 'header'))
            print(self.ui.colored_text(f"Current Day: {day}", 'value'))
            
            input("\n" + self.ui.colored_text("Press Enter to continue your shift...", 'hint'))
            return True
        else:
            print(self.ui.colored_text("\nFailed to load game.", 'error'))
            input("\n" + self.ui.colored_text("Press Enter to return to main menu...", 'hint'))
            return False
    
    def view_border_settings(self):
        """
        Display information about all border settings.
        
        Returns:
            bool: Always False to return to main menu.
        """
        self.ui.clear_screen()
        self.ui.draw_border("BORDER SETTINGS")
        
        settings = self.settings_manager.get_available_settings()
        
        for setting in settings:
            print(self.ui.colored_text(f"= {setting['name']} =".center(self.ui.width), 'title'))
            print(self.ui.colored_text(f"\n{setting['description']}", 'value'))
            print(self.ui.colored_text(f"\nSituation: {setting['situation']}", 'value'))
            
            print(self.ui.colored_text("\nDocument Requirements:", 'header'))
            for req in setting['document_requirements']:
                print(self.ui.colored_text(f"- {req}", 'value'))
                
            print(self.ui.colored_text("\nCommon Issues:", 'header'))
            for issue in setting['common_issues']:
                print(self.ui.colored_text(f"- {issue}", 'value'))
                
            print("\n" + self.ui.colored_text("=" * self.ui.width, 'border') + "\n")
        
        input(self.ui.colored_text("Press Enter to return to main menu...", 'hint'))
        return False
    
    def view_game_rules(self):
        """
        Display the core game rules.
        
        Returns:
            bool: Always False to return to main menu.
        """
        self.ui.clear_screen()
        self.ui.draw_border("GAME RULES")
        
        rules = [
            "As a border control agent, your job is to verify travel documents.",
            "Each traveler presents their document with a name, permit number, and backstory.",
            "Your task is to either APPROVE or DENY each traveler based on document validity.",
            "Valid permits must start with 'P' followed by exactly 4 digits.",
            "Traveler names must have both first and last names.",
            "Backstories should be consistent with the name.",
            "Additional requirements may be added based on your border assignment.",
            "Each day you will process multiple travelers.",
            "Making correct decisions improves your score.",
            "Careers last for 10 days, after which your performance is evaluated."
        ]
        
        for rule in rules:
            print(self.ui.colored_text(f"• {rule}", 'value'))
        
        print("\n" + self.ui.colored_text("=" * self.ui.width, 'border'))
        print(self.ui.colored_text("\nCommands during gameplay:".center(self.ui.width), 'header'))
        commands = [
            ("approve", "Approve the current traveler"),
            ("deny", "Deny the current traveler"),
            ("hint", "Request a hint from Veritas"),
            ("rules", "Display current verification rules"),
            ("save", "Save your current game progress"),
            ("help", "Show help information"),
            ("quit", "Return to main menu")
        ]
        
        for cmd, desc in commands:
            print(f"{self.ui.colored_text(cmd.ljust(10), 'command')} - {self.ui.colored_text(desc, 'value')}")
            
        print("\n" + self.ui.colored_text("=" * self.ui.width, 'border'))
        input("\n" + self.ui.colored_text("Press Enter to return to main menu...", 'hint'))
        return False
    
    def update_career_stats(self, gameplay_manager):
        """
        Update career stats based on completed game.
        
        Args:
            gameplay_manager (GameplayManager): The gameplay manager with current game stats.
        """
        # Update career stats
        self.career_stats["games_completed"] += 1
        self.career_stats["total_score"] += gameplay_manager.score
        
        # Add border to borders served
        setting = gameplay_manager.settings_manager.get_current_setting()
        self.career_stats["borders_served"].add(setting["name"])
        
        # Update highest day reached
        day = gameplay_manager.memory_manager.memory["game_state"]["day"]
        self.career_stats["highest_day_reached"] = max(
            self.career_stats["highest_day_reached"],
            day
        )
    
    def _get_save_files(self):
        """
        Get list of available save files.
        
        Returns:
            list: List of (path, name) tuples for save files.
        """
        # Get the saves directory path
        saves_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            self.gameplay_manager.memory_manager.save_dir
        )
        
        # Get all JSON files in the saves directory
        save_pattern = os.path.join(saves_dir, "*.json")
        save_files = glob.glob(save_pattern)
        
        # Convert to (path, name) tuples
        return [(path, os.path.basename(path)) for path in save_files]