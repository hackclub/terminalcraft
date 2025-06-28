import time
import os
import datetime
from zoo import Zoo
from utils import Colors
from save_manager import save_game, load_game
from challenge import CHALLENGES
def show_header(zoo):
    """Displays the main header with key zoo stats."""
    os.system('cls' if os.name == 'nt' else 'clear')
    header = f"{Colors.HEADER}--- {zoo.name} ---{Colors.RESET}"
    reputation_color = Colors.GREEN if zoo.reputation >= 70 else Colors.YELLOW if zoo.reputation >= 40 else Colors.RED
    stats = f"Date: {zoo.game_date.strftime('%Y-%m-%d')} | Money: {Colors.GREEN}${zoo.finance.money:,.2f}{Colors.RESET} | Reputation: {reputation_color}{zoo.reputation:.1f}/100{Colors.RESET} | Animals: {len(zoo.animals)} | Visitors: {len(zoo.visitors)}"
    print(header)
    print(stats)
    if zoo.vip_visit:
        vip = zoo.vip_visit
        objective = vip['objective']
        objective_text = objective['text']
        if 'target_species' in objective:
            objective_text = objective_text.format(animal=objective['target_species'])
        if 'target_habitat' in objective:
            objective_text = objective_text.format(habitat=objective['target_habitat'])
        print(f"\n{Colors.PURPLE}--- VIP VISITOR: {vip['name']} ---{Colors.RESET}")
        print(f"{Colors.YELLOW}Objective: To {objective_text}{Colors.RESET}")
def start_challenge_mode():
    """Handles the challenge mode selection screen."""
    print("\n--- Challenge Mode ---")
    if not CHALLENGES:
        print("No challenges available yet!")
        time.sleep(2)
        return None
    for key, challenge in CHALLENGES.items():
        print(f"{key}. {challenge['name']}")
    choice = input("\nSelect a challenge (or 0 to go back): ")
    if choice in CHALLENGES:
        print(f"\nStarting challenge: {CHALLENGES[choice]['name']}...")
        time.sleep(1)
        return CHALLENGES[choice]['function']()
    elif choice == '0':
        return None
    else:
        print("Invalid choice.")
        time.sleep(1)
        return None
def check_challenge_status(zoo):
    """Checks for win/loss conditions in a challenge and returns False if the game should end."""
    if not hasattr(zoo, 'challenge_data'):
        return True  
    loss_conditions = zoo.challenge_data['loss_conditions']
    win_conditions = zoo.challenge_data['win_conditions']
    if zoo.finance.money <= loss_conditions.get('money', 0):
        print(f"\n{Colors.RED}--- CHALLENGE FAILED ---{Colors.RESET}")
        print("Your zoo has gone bankrupt!")
        input("\nPress Enter to return to the main menu...")
        return False  
    money_goal = win_conditions.get('money', float('inf'))
    reputation_goal = win_conditions.get('reputation', 101) 
    if zoo.finance.money >= money_goal and zoo.reputation >= reputation_goal:
        print(f"\n{Colors.GREEN}--- CHALLENGE COMPLETE! ---{Colors.RESET}")
        print(f"Congratulations! You have successfully completed the {zoo.challenge_data['name']} challenge!")
        input("\nPress Enter to return to the main menu...")
        return False  
    return True  
def main():
    """Main function to run the game."""
    while True:  
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Colors.HEADER}Welcome to Terminal Zoo Tycoon!{Colors.RESET}")
        time.sleep(1)
        zoo = None
        print("\n1. New Game")
        print("2. Load Game")
        print("3. Challenge Mode")
        print("4. Exit")
        menu_choice = input("\nSelect an option: ")
        if menu_choice == '1':
            zoo_name = input("\nEnter the name of your new zoo: ")
            if zoo_name.strip():
                zoo = Zoo(zoo_name)
            else:
                print("Zoo name cannot be empty.")
                time.sleep(1)
        elif menu_choice == '2':
            zoo = load_game()
            if zoo:
                print(f"\nWelcome back to {zoo.name}!")
                time.sleep(2)
        elif menu_choice == '3':
            zoo = start_challenge_mode()
        elif menu_choice == '4':
            print("\nThanks for playing!")
            break
        else:
            print("Invalid choice.")
            time.sleep(1)
        if not zoo:
            continue
        if hasattr(zoo, 'challenge_data'):
            show_header(zoo)
            print(f"\n{Colors.PURPLE}--- Challenge: {zoo.challenge_data['name']} ---{Colors.RESET}")
            print(zoo.challenge_data['description'])
            win_cond_str = f"Win Conditions: Reach ${zoo.challenge_data['win_conditions']['money']:,} AND {zoo.challenge_data['win_conditions']['reputation']} Reputation."
            print(f"{Colors.GREEN}{win_cond_str}{Colors.RESET}")
            print(f"{Colors.RED}Loss Condition: Money drops to $0.{Colors.RESET}")
            input("\nPress Enter to begin...")
        game_running = True
        while game_running:
            show_header(zoo)
            print("\n--- Main Menu ---")
            print("1. View Detailed Reports")
            print("2. Build Habitat")
            print("3. Buy Animal")
            print("4. Hire Staff")
            print("5. Manage Habitats")
            print("6. Manage Staff")
            print("7. Research & Development")
            option_offset = 7
            has_fossil_quest = hasattr(zoo, 'fossil_quest_stage') and zoo.fossil_quest_stage >= 1
            if has_fossil_quest:
                print(f"{Colors.PURPLE}{option_offset+1}. Investigate Fossil{Colors.RESET}")
                option_offset += 1
            print(f"{Colors.YELLOW}{option_offset+1}. Next Day{Colors.RESET}")
            print(f"{Colors.GREEN}{option_offset+2}. Save Game{Colors.RESET}")
            print(f"{Colors.RED}{option_offset+3}. Exit to Main Menu{Colors.RESET}")
            choice = input("\nEnter your choice: ")
            next_day_choice = str(option_offset + 1)
            save_choice = str(option_offset + 2)
            exit_choice = str(option_offset + 3)
            if choice == '1':
                zoo.view_reports()
            elif choice == '2':
                zoo.build_habitat()
            elif choice == '3':
                zoo.buy_animal()
            elif choice == '4':
                zoo.hire_staff()
            elif choice == '5':
                zoo.manage_habitats()
            elif choice == '6':
                zoo.manage_staff()
            elif choice == '7':
                zoo.research_manager.manage_research(zoo)
            elif has_fossil_quest and choice == '8':
                zoo.investigate_fossil()
            elif choice == next_day_choice:
                zoo.next_day()
                if hasattr(zoo, 'challenge_data'):
                    game_running = check_challenge_status(zoo)
            elif choice == save_choice:
                if hasattr(zoo, 'challenge_data'):
                    print("\nCannot save during a challenge.")
                    time.sleep(1)
                else:
                    save_game(zoo)
                    print("\nGame saved!")
                    time.sleep(1)
            elif choice == exit_choice:
                game_running = False
            else:
                print("\nInvalid choice. Please try again.")
                time.sleep(1)
if __name__ == "__main__":
    main()