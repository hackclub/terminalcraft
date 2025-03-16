"""
Main module for Veritaminal

Entry point for the game that initializes components and runs the main game loop.
"""

import sys
import logging
import argparse
import os
from .api import get_veritas_hint, generate_narrative_update
from .gameplay import GameplayManager, Rule
from .narrative import NarrativeManager
from .ui import TerminalUI
from .main_menu import MainMenuManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='veritaminal.log'
)

logger = logging.getLogger(__name__)

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Veritaminal: Terminal-Based Document Verification Game')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--load', type=str, help='Load a saved game file')
    parser.add_argument('--skip-menu', action='store_true', help='Skip main menu and start game immediately')
    return parser.parse_args()

def main():
    """
    Main entry point for the game.
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Configure logging level based on args
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize components
    logger.info("Starting Veritaminal game")
    try:
        # Initialize main menu manager
        menu_manager = MainMenuManager()
        
        # Either show main menu or start game directly based on args
        if args.skip_menu:
            # Start game directly
            if args.load and os.path.exists(args.load):
                # Load specific save file
                success = menu_manager.gameplay_manager.load_game(args.load)
                if not success:
                    logger.error(f"Failed to load game from {args.load}")
                    return 1
            else:
                # Start new game with default border setting
                menu_manager.gameplay_manager.initialize_game()
            
            # Run the gameplay loop
            run_gameplay_loop(menu_manager)
            return 0
        else:
            # Run the main menu
            run_main_menu_loop(menu_manager)
            return 0
    
    except KeyboardInterrupt:
        logger.info("Game interrupted by user")
        print("\nGame interrupted. Goodbye!")
        return 0
    
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"\nAn unexpected error occurred: {e}")
        print("See veritaminal.log for details.")
        return 1

def run_main_menu_loop(menu_manager):
    """
    Run the main menu loop.
    
    Args:
        menu_manager (MainMenuManager): The main menu manager.
    """
    while True:
        # Display main menu and get choice
        choice = menu_manager.display_main_menu()
        
        if choice == "1":  # Start new career
            start_game = menu_manager.start_new_career()
            if start_game:
                # Run the gameplay loop
                run_gameplay_loop(menu_manager)
                
        elif choice == "2":  # Continue previous career
            continue_game = menu_manager.continue_previous_career()
            if continue_game:
                # Run the gameplay loop
                run_gameplay_loop(menu_manager)
                
        elif choice == "3":  # View border settings
            menu_manager.view_border_settings()
            
        elif choice == "4":  # View game rules
            menu_manager.view_game_rules()
            
        elif choice == "5":  # Quit game
            ui = menu_manager.ui
            print("\n" + ui.colored_text("Thank you for playing Veritaminal!", 'success'))
            break

def run_gameplay_loop(menu_manager):
    """
    Run the main gameplay loop.
    
    Args:
        menu_manager (MainMenuManager): The main menu manager containing gameplay components.
    """
    # Create narrative manager and UI for gameplay
    gameplay_manager = menu_manager.gameplay_manager
    ui = menu_manager.ui
    narrative_manager = NarrativeManager()
    
    # Synchronize narrative manager with memory manager's state
    narrative_manager.story_state["day"] = gameplay_manager.memory_manager.memory["game_state"]["day"]
    narrative_manager.story_state["corruption"] = gameplay_manager.memory_manager.memory["game_state"]["corruption"]
    narrative_manager.story_state["trust"] = gameplay_manager.memory_manager.memory["game_state"]["trust"]
    
    # Main game loop
    game_running = True
    while game_running:
        # Check if game is over due to corruption/trust or day limit
        is_game_over, ending_type, ending_message = narrative_manager.check_game_over()
        if is_game_over:
            ui.display_game_over(ending_type, ending_message)
            
            # Update career stats
            menu_manager.update_career_stats(gameplay_manager)
            
            # Reset memory for next game
            gameplay_manager.memory_manager.reset_memory()
            break
            
        # Check if we've completed day 10 and should return to menu
        if gameplay_manager.game_completed:
            day = gameplay_manager.memory_manager.memory["game_state"]["day"]
            score = gameplay_manager.score
            
            # Display completion message
            ui.clear_screen()
            ui.draw_border("CAREER COMPLETE")
            print(ui.colored_text(f"You have completed your 10-day assignment!".center(ui.width), 'success'))
            print(ui.colored_text(f"Final score: {score}".center(ui.width), 'value'))
            
            # Update career stats
            menu_manager.update_career_stats(gameplay_manager)
            
            input("\n" + ui.colored_text("Press Enter to return to main menu...".center(ui.width), 'hint'))
            break
        
        # Generate new document for current day
        document = gameplay_manager.generate_document()
        ui.display_document(document)
        
        # Display status
        ui.display_status(
            narrative_manager.story_state["day"],
            gameplay_manager.get_score(),
            narrative_manager.get_state_summary()
        )
        
        # Process commands until player makes a decision (approve/deny)
        decision_made = False
        while not decision_made and game_running:
            command = ui.get_user_input()
            
            if command == "approve" or command == "deny":
                # Process decision
                is_correct, points = gameplay_manager.make_decision(command)
                
                # Generate narrative update with memory context
                memory_context = gameplay_manager.memory_manager.get_memory_context()
                narrative_update = generate_narrative_update(
                    narrative_manager.story_state,
                    command,
                    is_correct,
                    memory_context
                )
                
                # Update narrative state
                narrative_manager.update_state(command, is_correct, document)
                
                # Sync narrative manager with gameplay manager's memory
                narrative_manager.story_state["corruption"] = gameplay_manager.memory_manager.memory["game_state"]["corruption"]
                narrative_manager.story_state["trust"] = gameplay_manager.memory_manager.memory["game_state"]["trust"]
                
                # Display feedback and AI reasoning if available
                ui.display_feedback(is_correct, narrative_update)
                if command != gameplay_manager.ai_judgment["decision"]:
                    print("\nAI Opinion:")
                    print(f"The AI would have {gameplay_manager.ai_judgment['decision']}ed because: {gameplay_manager.get_ai_reasoning()}")
                
                decision_made = True
                
                # Save game after each decision
                gameplay_manager.save_game()
                
                # Wait for player to continue
                input("\nPress Enter to continue...")
                
            elif command == "hint":
                # Get and display hint with memory context
                memory_context = gameplay_manager.memory_manager.get_memory_context()
                hint = get_veritas_hint(document, memory_context)
                ui.display_veritas_hint(hint)
                
            elif command == "rules":
                # Display rules from the current setting
                setting_rules = gameplay_manager.settings_manager.get_all_rules()
                ui.display_rules([Rule(f"Rule {i+1}", rule, lambda doc: True) 
                                for i, rule in enumerate(setting_rules)])
                ui.display_document(document)  # Re-display document after rules
                
            elif command == "help":
                # Display help
                ui.display_help()
                ui.display_document(document)  # Re-display document after help
                
            elif command == "save":
                # Save game
                if gameplay_manager.save_game():
                    print("\nGame saved successfully.")
                else:
                    print("\nFailed to save game.")
                    
            elif command == "quit":
                # Return to main menu
                game_running = False
                print("\nReturning to main menu...")
                
            else:
                # Invalid command
                print("\nInvalid command. Type 'help' for a list of commands.")
        
        # Advance to next day if a decision was made
        if decision_made:
            day_message = narrative_manager.advance_day()
            
            # Sync day between narrative and memory managers
            gameplay_manager.memory_manager.memory["game_state"]["day"] = narrative_manager.story_state["day"]
            # Also advance the day in the gameplay manager
            gameplay_manager.advance_day()
            
            print(f"\n{day_message}")
            input("\nPress Enter to continue...")

# Keep this block to ensure it works both as a module and as a script
if __name__ == "__main__":
    sys.exit(main())
