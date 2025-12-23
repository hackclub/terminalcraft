"""
This module is responsible for all the output displayed to the user.
It will format and print the game state, menus, and event descriptions.
"""
import textwrap
from colorama import Fore, Style
class Renderer:
    """Handles rendering game information to the console."""
    def __init__(self, line_width=80):
        self.line_width = line_width
    def display_world_state(self, world):
        """Displays the status of all kingdoms."""
        print(f"{Fore.CYAN}{Style.BRIGHT}--- WORLD STATE: YEAR {world.current_year} ---{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}Global Tension: {world.global_tension:.1f}{Style.RESET_ALL}")
        self.display_prophecies(world)
        for kingdom in world.kingdoms:
            if kingdom.is_alive:
                status_color = Fore.GREEN if kingdom.stability > 60 else Fore.YELLOW if kingdom.stability > 30 else Fore.RED
                print(f"{Style.BRIGHT}{kingdom.name.upper()} ({', '.join(kingdom.traits)}){Style.RESET_ALL}")
                print(f"  {status_color}Status: {'Stable' if kingdom.stability > 60 else 'Unrest' if kingdom.stability > 30 else 'Collapsing'}{Style.RESET_ALL}")
                print(f"  - Population: {kingdom.population:,}")
                print(f"  - Stability: {kingdom.stability}")
                print(f"  - Military: {kingdom.military_strength:,}")
                print(f"  - Food Reserves: {kingdom.food_reserves:,}")
                print(f"  - Wealth: {kingdom.wealth:,}")
                if kingdom.allies:
                    print(f"  {Fore.GREEN}Allies: {', '.join(kingdom.allies)}{Style.RESET_ALL}")
                if kingdom.rivals:
                    print(f"  {Fore.RED}Rivals: {', '.join(kingdom.rivals)}{Style.RESET_ALL}")
                if kingdom.wonder_project:
                    progress = (kingdom.wonder_project.progress / kingdom.wonder_project.cost) * 100
                    print(f"  {Fore.CYAN}Wonder Project: {kingdom.wonder_project.name} ({progress:.1f}% complete){Style.RESET_ALL}")
                if kingdom.wonders:
                    for wonder in kingdom.wonders:
                        print(f"  {Fore.YELLOW}Great Wonder: {wonder.name} ({wonder.description}){Style.RESET_ALL}")
                if kingdom.heroes:
                    for hero in kingdom.heroes:
                        print(f"  {Fore.YELLOW}Legendary Hero: {hero.name}, {hero.title} ({hero.lifespan} years left){Style.RESET_ALL}")
            else:
                print(f"{Style.BRIGHT}{kingdom.name.upper()}{Style.RESET_ALL}")
                print(f"  {Fore.RED}Status: Fallen{Style.RESET_ALL}")
            print("-" * 20)
        if world.available_heroes:
            print(f"{Fore.YELLOW}{Style.BRIGHT}--- AVAILABLE HEROES ---{Style.RESET_ALL}")
            for hero in world.available_heroes:
                print(f"  - {hero.name}, {hero.title} ({hero.description}){Style.RESET_ALL}")
            print("-" * 20)
    def display_prophecies(self, world):
        if world.active_prophecies:
            print(f"{Fore.MAGENTA}{Style.BRIGHT}--- ACTIVE PROPHECIES ---{Style.RESET_ALL}")
            for i, prophecy in enumerate(world.active_prophecies):
                wrapped_text = textwrap.fill(f'  {i+1}. "{prophecy.text}"', self.line_width)
                print(f"{Fore.MAGENTA}{wrapped_text}{Style.RESET_ALL}")
            print("\n")
    def display_main_menu(self, world):
        """Shows the main list of actions to the player."""
        print("\n" + "="*self.line_width)
        print("                         ORACLE'S SANCTUM                          ")
        print("What is your command?")
        print("  [view]: View world state")
        print("  [adv]: Advance time by one year")
        print("  [predict] [famine|war] [kingdom1] [kingdom2?]: Ask a question")
        print("  [influence] [harvest|stability] [kingdom]: Exert your will")
        print("  [rewrite] [id] target [kingdom]: Rewrite a prophecy's fate")
        print("  [ally] [kingdom1] [kingdom2]: Encourage an alliance (costs tension)")
        print("  [rival] [kingdom1] [kingdom2]: Sow discord (costs tension)")
        print("  [wonder] [kingdom] [wonder_name]: Inspire the construction of a Great Wonder")
        print("  [recruit] [kingdom] [hero_name]: Recruit a Legendary Hero (costs wealth)")
        print("  [save]: Freeze the timeline (save game)")
        print("  [load]: Restore a frozen timeline (load game)")
        print("  [quit]: Exit the simulation")
        print("="*self.line_width)
    def display_message(self, message, color_name='white'):
        """Displays a generic message to the user, accepting a color name."""
        color_map = {
            'red': Fore.RED,
            'green': Fore.GREEN,
            'yellow': Fore.YELLOW,
            'blue': Fore.BLUE,
            'magenta': Fore.MAGENTA,
            'cyan': Fore.CYAN,
            'white': Fore.WHITE,
        }
        if "\033[" in message:
            color = ""
        else:
            color = color_map.get(color_name.lower(), Fore.WHITE)
        wrapped_message = textwrap.fill(str(message), self.line_width)
        print(f"{color}{wrapped_message}{Style.RESET_ALL}")