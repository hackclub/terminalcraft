"""
UI module for Veritaminal

Handles the terminal-based user interface, including document display,
user input, and interface styling.
"""

import os
import sys
import logging
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import WordCompleter
from colorama import init, Fore, Back, Style as ColoramaStyle

# Initialize colorama for cross-platform terminal colors
# Using settings that worked well in testing
init(autoreset=True, convert=True, strip=False, wrap=True)

logger = logging.getLogger(__name__)

# Define color styles for prompt_toolkit
pt_style = Style.from_dict({
    'title': '#ansiyellow bold',
    'header': '#ansiblue bold',
    'normal': '#ansiwhite',
    'error': '#ansired bold',
    'success': '#ansigreen',
    'warning': '#ansiyellow',
    'hint': '#ansicyan italic',
    'command': '#ansimagenta',
    'veritas': '#ansigreen bold',
    'border_info': '#ansiyellow italic',
})

# Command completer for auto-completion
command_completer = WordCompleter(['approve', 'deny', 'hint', 'rules', 'help', 'save', 'quit'])


class TerminalUI:
    """
    Manages the terminal-based user interface.
    """
    def __init__(self):
        """
        Initialize the terminal UI.
        """
        self.width = 80  # Default width
        self.adjust_terminal_size()
        
        # Define color styles for terminal output based on test results (Option 3)
        self.colors = {
            'title': Fore.YELLOW + Back.BLUE,  # Yellow on blue for titles
            'header': Fore.BLUE,
            'normal': Fore.WHITE,
            'error': Fore.RED,
            'success': Fore.GREEN,
            'warning': Fore.YELLOW,
            'hint': Fore.CYAN,
            'command': Fore.MAGENTA,
            'veritas': Fore.GREEN,
            'border_info': Fore.YELLOW,
            'border': Fore.BLUE,
            'key': Fore.CYAN,
            'value': Fore.WHITE,
            'reset': ColoramaStyle.RESET_ALL,
        }
        
        # Add special combinations for emphasis using background colors instead of brightness
        self.emphasis = {
            'title': Back.BLACK,       # Yellow on black for titles
            'key': Back.BLACK,         # Cyan on black for keys
            'veritas': Back.BLACK,     # Green on black for Veritas
            'error': Back.BLACK,       # Red on black for errors
            'success': Back.BLACK,     # Green on black for success
        }

    def _check_color_support(self):
        """
        Check if the terminal supports colors.
        
        Returns:
            bool: True if colors are supported, False otherwise.
        """
        # Force color support on Windows
        if os.name == 'nt':
            return True
        
        # Check for NO_COLOR environment variable
        if os.environ.get('NO_COLOR'):
            return False
            
        # Check if output is redirected
        if not sys.stdout.isatty():
            return 'FORCE_COLOR' in os.environ
        
        # Most terminals support colors nowadays
        return True
    
    def adjust_terminal_size(self):
        """
        Adjust UI based on terminal size.
        """
        try:
            # Get terminal size if available
            terminal_size = os.get_terminal_size()
            self.width = min(100, terminal_size.columns)
        except (AttributeError, OSError):
            # Default if terminal size can't be determined
            self.width = 80
    
    def clear_screen(self):
        """
        Clear the terminal screen.
        """
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def colored_text(self, text, style_name):
        """
        Return text with the specified color style.
        
        Args:
            text (str): Text to color.
            style_name (str): Name of the style to apply.
            
        Returns:
            str: Colored text.
        """
        if style_name not in self.colors:
            return text
            
        # Apply background emphasis for specific styles that would normally use BRIGHT
        if style_name in self.emphasis:
            return f"{self.colors[style_name]}{self.emphasis[style_name]}{text}{self.colors['reset']}"
            
        return f"{self.colors[style_name]}{text}{self.colors['reset']}"
    
    def colored_print(self, text, style_name='normal'):
        """
        Print text with the specified color style.
        
        Args:
            text (str): Text to print.
            style_name (str): Name of the style to apply.
        """
        print(self.colored_text(text, style_name))
    
    def draw_border(self, title=None):
        """
        Draw a border with an optional title.
        
        Args:
            title (str, optional): Title to display in the border.
        """
        border = "=" * self.width  # Using '=' instead of '-' for borders
        print(self.colored_text("\n" + border, 'border'))
        
        if title:
            print(self.colored_text(title.center(self.width), 'title'))
            print(self.colored_text(border + "\n", 'border'))
        else:
            print()
    
    def display_welcome(self):
        """
        Display the welcome message.
        """
        self.clear_screen()
        self.draw_border("VERITAMINAL: Document Verification Game")
        
        welcome_text = [
            "Welcome to the border checkpoint.",
            "",
            "As a border control agent, your job is to verify travelers' documents",
            "and decide whether to approve or deny their entry.",
            "",
            "You'll be assisted by Veritas, an AI that may provide hints.",
            "Your decisions will have consequences that carry through your career.",
            "",
            "Type 'help' for a list of commands.",
        ]
        
        for line in welcome_text:
            print(self.colored_text(line.center(self.width), 'normal'))
        
        print("\n" + self.colored_text("=" * self.width, 'border') + "\n")
        
        input(self.colored_text("Press Enter to begin...".center(self.width), 'hint'))
    
    def display_border_selection(self, settings):
        """
        Display the border setting selection screen.
        
        Args:
            settings (list): List of available border settings.
            
        Returns:
            int: The selected border setting index.
        """
        self.clear_screen()
        self.draw_border("SELECT YOUR BORDER ASSIGNMENT")
        
        for i, setting in enumerate(settings, 1):
            print(self.colored_text(f"{i}. {setting['name']}", 'header'))
            print(self.colored_text(f"   {setting['description']}\n", 'normal'))
        
        choice = 0
        while choice < 1 or choice > len(settings):
            try:
                choice = int(input(self.colored_text(f"\nEnter your choice (1-{len(settings)}): ", 'hint')))
            except ValueError:
                self.colored_print("Please enter a valid number.", 'error')
                
        return choice
    
    def display_document(self, document):
        """
        Display a document to the player.
        
        Args:
            document (dict): The document to display.
        """
        self.clear_screen()
        # Using '=' instead of '-' for borders as in Option 3
        print(self.colored_text("\n" + "=" * self.width, 'border'))
        print(self.colored_text("TRAVELER DOCUMENT".center(self.width), 'title'))
        print(self.colored_text("=" * self.width + "\n", 'border'))
        
        # Display document details with formatting
        print(f"{self.colored_text('Name:', 'key')}      {self.colored_text(document['name'], 'value')}")
        print(f"{self.colored_text('Permit:', 'key')}    {self.colored_text(document['permit'], 'value')}")
        print(f"\n{self.colored_text('Backstory:', 'key')} {self.colored_text(document['backstory'], 'value')}")
        
        # Display any additional fields that may be present
        additional_fields = [key for key in document.keys() 
                           if key not in ('name', 'permit', 'backstory', 'is_valid')]
        if additional_fields:
            print(self.colored_text("\nAdditional Information:", 'header'))
            for field in additional_fields:
                if isinstance(document[field], dict):
                    print(self.colored_text(f"{field.capitalize()}: ", 'key'))
                    for subkey, value in document[field].items():
                        print(f"  - {self.colored_text(subkey.capitalize() + ':', 'key')} {self.colored_text(value, 'value')}")
                else:
                    print(f"{self.colored_text(field.capitalize() + ':', 'key')} {self.colored_text(document[field], 'value')}")
        
        print(self.colored_text("\n" + "-" * self.width, 'border'))
    
    def display_veritas_hint(self, hint):
        """
        Display a hint from Veritas.
        
        Args:
            hint (str): The hint to display.
        """
        # Using '=' instead of '-' for borders
        print(self.colored_text("\n" + "=" * self.width, 'border'))
        print(self.colored_text("VERITAS SAYS:".center(self.width), 'veritas'))
        print(self.colored_text(f"\n\"{hint}\"\n", 'hint'))
        print(self.colored_text("=" * self.width, 'border'))
    
    def display_rules(self, rules):
        """
        Display the current verification rules.
        
        Args:
            rules (list): List of Rule objects.
        """
        self.clear_screen()
        # Using '=' instead of '-' for borders
        print(self.colored_text("\n" + "=" * self.width, 'border'))
        print(self.colored_text("VERIFICATION RULES".center(self.width), 'title'))
        print(self.colored_text("=" * self.width + "\n", 'border'))
        
        for i, rule in enumerate(rules, 1):
            print(f"{self.colored_text(str(i) + '. ' + rule.name + ':', 'key')} {self.colored_text(rule.description, 'normal')}")
        
        print(self.colored_text("\n" + "-" * self.width, 'border'))
        input(self.colored_text("\nPress Enter to return...", 'hint'))
    
    def display_help(self):
        """
        Display help information.
        """
        self.clear_screen()
        # Using '=' instead of '-' for borders
        print(self.colored_text("\n" + "=" * self.width, 'border'))
        print(self.colored_text("AVAILABLE COMMANDS".center(self.width), 'title'))
        print(self.colored_text("=" * self.width + "\n", 'border'))
        
        commands = [
            ("approve", "Approve the current traveler"),
            ("deny", "Deny the current traveler"),
            ("hint", "Request a hint from Veritas"),
            ("rules", "Display current verification rules"),
            ("save", "Save your current game progress"),
            ("help", "Show this help information"),
            ("quit", "Exit the game")
        ]
        
        for cmd, desc in commands:
            print(f"{self.colored_text(cmd.ljust(10), 'command')} - {self.colored_text(desc, 'normal')}")
        
        print(self.colored_text("\n" + "-" * self.width, 'border'))
        input(self.colored_text("\nPress Enter to return...", 'hint'))
    
    def display_feedback(self, is_correct, narrative_update):
        """
        Display feedback based on the player's decision.
        
        Args:
            is_correct (bool): Whether the player's decision was correct.
            narrative_update (str): The narrative update to display.
        """
        if is_correct:
            self.colored_print("\n✓ Correct decision!", 'success')
        else:
            self.colored_print("\n✗ Incorrect decision!", 'error')
        
        print(self.colored_text(f"\n{narrative_update}", 'normal'))
    
    def display_ai_reasoning(self, reasoning, confidence):
        """
        Display AI reasoning for a decision.
        
        Args:
            reasoning (str): The AI's reasoning.
            confidence (float): The AI's confidence level.
        """
        print(self.colored_text("\nBorder Control AI Assessment:", 'header'))
        
        # Color the confidence based on its level
        confidence_pct = int(confidence * 100)
        confidence_style = 'success' if confidence_pct > 75 else 'warning' if confidence_pct > 50 else 'error'
        
        print(f"{self.colored_text('Confidence:', 'key')} {self.colored_text(f'{confidence_pct}%', confidence_style)}")
        print(f"{self.colored_text('Reasoning:', 'key')} {self.colored_text(reasoning, 'normal')}")
    
    def display_game_over(self, ending_type, ending_message):
        """
        Display the game over screen.
        
        Args:
            ending_type (str): Type of ending ('good', 'bad', 'corrupt', 'strict').
            ending_message (str): The ending message to display.
        """
        self.clear_screen()
        self.draw_border("GAME OVER")
        
        print(self.colored_text(ending_message.center(self.width) + "\n", 'normal'))
        
        ending_style = {
            'good': 'success',
            'corrupt': 'error',
            'strict': 'warning',
            'bad': 'error'
        }.get(ending_type, 'normal')
        
        if ending_type == 'good':
            msg = "Congratulations! You've successfully completed your mission."
        elif ending_type == 'corrupt':
            msg = "Your corruption has caught up with you."
        elif ending_type == 'strict':
            msg = "Your strict adherence to rules has made you unpopular."
        else:
            msg = "Your career has come to an unfortunate end."
            
        print(self.colored_text(msg.center(self.width), ending_style))
        
        print("\n" + self.colored_text("=" * self.width, 'border'))
        input(self.colored_text("\nPress Enter to exit...".center(self.width), 'hint'))
    
    def get_user_input(self):
        """
        Get input from the user with command completion.
        
        Returns:
            str: The user's command.
        """
        try:
            user_input = prompt(
                HTML('<span style="fg:ansicyan">Enter command</span> <span style="fg:ansiwhite">&gt;</span> '),
                completer=command_completer,
                style=pt_style
            )
            return user_input.strip().lower()
        except KeyboardInterrupt:
            return "quit"
    
    def display_status(self, day, score, state_summary):
        """
        Display status information.
        
        Args:
            day (int): Current day.
            score (int): Current score.
            state_summary (str): Summary of the narrative state.
        """
        # Using '=' instead of '-' for borders
        print(self.colored_text("\n" + "=" * self.width, 'border'))
        print(f"{self.colored_text('Day:', 'key')} {self.colored_text(str(day), 'value')} | {self.colored_text('Score:', 'key')} {self.colored_text(str(score), 'value')}")
        print(self.colored_text(state_summary, 'border_info'))
        print(self.colored_text("=" * self.width, 'border'))
    
    def display_setting_info(self, setting):
        """
        Display information about the current border setting.
        
        Args:
            setting (dict): The current border setting.
        """
        # Using '=' instead of '-' for borders
        print(self.colored_text("\n" + "=" * self.width, 'border'))
        print(self.colored_text(f"CURRENT ASSIGNMENT: {setting['name']}", 'title'))
        print(self.colored_text(f"\n{setting['situation']}", 'normal'))
        
        print(self.colored_text("\nDocument Requirements:", 'header'))
        for req in setting['document_requirements']:
            print(self.colored_text(f"- {req}", 'normal'))
        
        print(self.colored_text("\nCommon Issues:", 'header'))
        for issue in setting['common_issues']:
            print(self.colored_text(f"- {issue}", 'normal'))
            
        print(self.colored_text("\n" + "-" * self.width, 'border'))
        input(self.colored_text("\nPress Enter to continue...", 'hint'))
