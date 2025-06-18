import time
import os
import datetime
from zoo import Zoo
from utils import Colors
from save_manager import save_game, load_game
def show_header(zoo):
    """Displays the main header with key zoo stats."""
    os.system('cls' if os.name == 'nt' else 'clear')
    header = f"{Colors.HEADER}--- {zoo.name} ---{Colors.RESET}"
    stats = f"Date: {zoo.game_date.strftime('%Y-%m-%d')} | Money: {Colors.GREEN}${zoo.finance.money:,.2f}{Colors.RESET} | Animals: {len(zoo.animals)} | Visitors: {len(zoo.visitors)}"
    print(header)
    print(stats)
def main():
    """Main function to run the game."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.HEADER}Welcome to Terminal Zoo Tycoon!{Colors.RESET}")
    time.sleep(1)
    zoo = None
    print("\n1. New Game")
    print("2. Load Game")
    choice = input("Select an option: ")
    if choice == '2':
        zoo = load_game()
        if zoo:
            print(f"\nWelcome back to {zoo.name}!")
            time.sleep(2)
        else:
            time.sleep(2)
    if not zoo:
        zoo_name = input("\nEnter the name of your new zoo: ")
        zoo = Zoo(zoo_name)
    while True:
        show_header(zoo)
        print("\n--- Main Menu ---")
        print("1. View Detailed Reports")
        print("2. Build Habitat")
        print("3. Buy Animal")
        print("4. Hire Staff")
        print("5. Manage Habitats")
        print("6. Manage Staff")
        print("7. Research & Development")
        print(f"{Colors.YELLOW}8. Next Day{Colors.RESET}")
        print(f"{Colors.GREEN}9. Save Game{Colors.RESET}")
        print(f"{Colors.RED}10. Exit{Colors.RESET}")
        choice = input("\nEnter your choice: ")
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
        elif choice == '8':
            zoo.next_day()
        elif choice == '9':
            save_game(zoo)
            print("Game saved!")
            time.sleep(1)
        elif choice == '10':
            print("Thanks for playing!")
            break
        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)
if __name__ == "__main__":
    main()