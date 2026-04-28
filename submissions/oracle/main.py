import sys
import os
import pickle
from colorama import init as colorama_init, Fore, Style
from engine.world import World
from engine.oracle import Oracle
from ui.renderer import Renderer
from ui.parser import Parser
from engine.wonder import create_wonder, WONDER_TEMPLATES
class Game:
    """Main game class to hold the state and orchestrate the game flow."""
    def __init__(self):
        colorama_init()
        self.world = World(kingdom_data_path='data/kingdom_data.json')
        self.oracle = Oracle()
        self.renderer = Renderer()
        self.parser = Parser()
        self.is_running = True
        self.save_file_path = "savegame.dat"
    def run(self):
        """Main game loop."""
        self.renderer.display_message(
            "Welcome, Oracle. The threads of fate are yours to observe. "
            "The kingdoms of the world await their destiny, unaware of the "
            "silent power that watches over them.",
            color_name='cyan'
        )
        self.renderer.display_world_state(self.world)
        while self.is_running:
            try:
                self.renderer.display_main_menu(self.world)
                user_input = input("> ")
                self.handle_input(user_input)
            except EOFError:
                self.is_running = False
                print("\nEOF detected. Shutting down gracefully.")
    def handle_input(self, user_input):
        """Processes user input and calls the appropriate game logic."""
        command, args = self.parser.parse_command(user_input)
        if command == 'quit':
            self.is_running = False
            self.renderer.display_message("The Oracle slumbers. The world is left to its own devices.", color_name='magenta')
        elif command == 'advance':
            self.renderer.display_message(f"\n--- Advancing to Year {self.world.current_year + 1} ---", color_name='yellow')
            self.world.tick(self.renderer)
            self.renderer.display_world_state(self.world)
        elif command == 'view':
            self.renderer.display_world_state(self.world)
        elif command == 'predict':
            self.handle_prediction(args)
        elif command == 'influence':
            self.handle_influence(args)
        elif command == 'rewrite':
            self.handle_rewrite(args)
        elif command == 'save':
            self.save_game()
        elif command == 'load':
            self.load_game()
        elif command == 'ally':
            self.handle_diplomacy(args, 'ally')
        elif command == 'rival':
            self.handle_diplomacy(args, 'rival')
        elif command == 'wonder':
            self.handle_wonder_command(args)
        elif command == 'recruit':
            self.handle_recruit_command(args)
        else:
            self.renderer.display_message(f"Your command '{user_input}' is but a whisper in the void, unrecognized.", color_name='red')
    def handle_prediction(self, args):
        if not args:
            self.renderer.display_message("Predict what? (e.g., 'predict famine [kingdom]' or 'predict war [k1] [k2]')", color_name='red')
            return
        pred_type = args[0]
        if pred_type == 'famine':
            if len(args) < 2:
                self.renderer.display_message("Usage: predict famine [kingdom]", color_name='red')
                return
            kingdom = self.world.get_kingdom_by_name(args[1])
            if kingdom:
                self.renderer.display_message(self.oracle.predict_famine(kingdom))
            else:
                self.renderer.display_message(f"Unknown kingdom: {args[1]}", color_name='red')
        elif pred_type == 'war':
            if len(args) < 3:
                self.renderer.display_message("Usage: predict war [kingdom1] [kingdom2]", color_name='red')
                return
            k1 = self.world.get_kingdom_by_name(args[1])
            k2 = self.world.get_kingdom_by_name(args[2])
            if k1 and k2:
                self.renderer.display_message(self.oracle.predict_war(k1, k2))
            else:
                self.renderer.display_message(f"One or more kingdoms not found.", color_name='red')
        else:
            self.renderer.display_message(f"Cannot predict '{pred_type}'.", color_name='red')
    def handle_influence(self, args):
        if not args:
            self.renderer.display_message("Influence what? (e.g., 'influence harvest [kingdom]')", color_name='yellow')
            return
        inf_type = args[0]
        if len(args) < 2:
            self.renderer.display_message(f"Usage: influence {inf_type} [kingdom]", color_name='red')
            return
        kingdom = self.world.get_kingdom_by_name(args[1])
        if not kingdom:
            self.renderer.display_message(f"Unknown kingdom: {args[1]}", color_name='red')
            return
        if inf_type == 'harvest':
            result = self.oracle.influence_harvest(self.world, kingdom)
            self.renderer.display_message(result, color_name='magenta')
            self.renderer.display_world_state(self.world)
        elif inf_type == 'stability':
            result = self.oracle.influence_stability(self.world, kingdom)
            self.renderer.display_message(result, color_name='magenta')
            self.renderer.display_world_state(self.world)
        else:
            self.renderer.display_message(f"Cannot influence '{inf_type}'.", color_name='red')
    def handle_rewrite(self, args):
        """Handles the logic for rewriting a prophecy."""
        if len(args) < 3:
            self.renderer.display_message("Usage: rewrite [prophecy_id] target [kingdom_name]", 'red')
            return
        try:
            prophecy_id = int(args[0]) - 1 
            keyword = args[1]
            new_target_name = args[2]
        except (ValueError, IndexError):
            self.renderer.display_message("Invalid command format. Usage: rewrite [id] target [kingdom]", 'red')
            return
        if keyword.lower() != 'target':
            self.renderer.display_message("You can only rewrite the 'target' of a prophecy for now.", 'yellow')
            return
        if not (0 <= prophecy_id < len(self.world.active_prophecies)):
            self.renderer.display_message("Invalid prophecy ID.", 'red')
            return
        prophecy = self.world.active_prophecies[prophecy_id]
        new_target_kingdom = self.world.get_kingdom_by_name(new_target_name)
        if not new_target_kingdom or not new_target_kingdom.is_alive:
            self.renderer.display_message(f"Kingdom '{new_target_name}' not found or has fallen.", 'red')
            return
        if new_target_name == prophecy.source_kingdom_name:
            self.renderer.display_message("A prophecy cannot target its own source.", 'yellow')
            return
        if new_target_name == prophecy.target_kingdom_name:
            self.renderer.display_message(f"The prophecy already targets {new_target_name}.", 'yellow')
            return
        prophecy.rewrite_target(new_target_kingdom.name)
        tension_cost = 15.0
        self.world.global_tension += tension_cost
        self.renderer.display_message(f"You have bent the threads of fate. The prophecy now targets {new_target_kingdom.name}.", 'magenta')
        self.renderer.display_message(f"The world strains under your influence. Tension rises by {tension_cost:.1f}.", 'magenta')
        self.renderer.display_world_state(self.world)
    def handle_diplomacy(self, args, action):
        """Handles diplomatic actions like forging alliances or rivalries."""
        if len(args) < 2:
            self.renderer.display_message(f"Usage: {action} [kingdom1] [kingdom2]", 'red')
            return
        k1_name, k2_name = args[0], args[1]
        k1 = self.world.get_kingdom_by_name(k1_name)
        k2 = self.world.get_kingdom_by_name(k2_name)
        if not k1 or not k2 or not k1.is_alive or not k2.is_alive:
            self.renderer.display_message("One or both kingdoms not found or have fallen.", 'red')
            return
        if k1 == k2:
            self.renderer.display_message("A kingdom cannot have a diplomatic relationship with itself.", 'yellow')
            return
        tension_cost = 20.0
        if action == 'ally':
            self.world.encourage_alliance(k1, k2)
            self.renderer.display_message(f"You whisper words of friendship into the ears of the rulers of {k1.name} and {k2.name}.", 'magenta')
        elif action == 'rival':
            self.world.sow_discord(k1, k2)
            self.renderer.display_message(f"You plant seeds of doubt and rivalry between {k1.name} and {k2.name}.", 'magenta')
        self.world.global_tension += tension_cost
        self.renderer.display_message(f"The world grows more tense. Tension rises by {tension_cost:.1f}.", 'magenta')
        self.renderer.display_world_state(self.world)
    def handle_wonder_command(self, args):
        """Handles the command to start a wonder project."""
        if len(args) < 2:
            self.renderer.display_message("Usage: wonder [kingdom] [wonder_name]", 'red')
            self.renderer.display_message(f"Available wonders: {', '.join(WONDER_TEMPLATES.keys())}", 'yellow')
            return
        kingdom_name = args[0]
        wonder_name = ' '.join(args[1:]).title()
        kingdom = self.world.get_kingdom_by_name(kingdom_name)
        if not kingdom or not kingdom.is_alive:
            self.renderer.display_message(f"Kingdom '{kingdom_name}' not found or has fallen.", 'red')
            return
        if kingdom.wonder_project:
            self.renderer.display_message(f"{kingdom.name} is already constructing {kingdom.wonder_project.name}.", 'yellow')
            return
        wonder = create_wonder(wonder_name)
        if not wonder:
            self.renderer.display_message(f"Wonder '{wonder_name}' not found.", 'red')
            self.renderer.display_message(f"Available wonders: {', '.join(WONDER_TEMPLATES.keys())}", 'yellow')
            return
        kingdom.wonder_project = wonder
        self.renderer.display_message(f"You have inspired {kingdom.name} to begin the grand project of building {wonder.name}!", 'cyan')
        self.renderer.display_world_state(self.world)
    def handle_recruit_command(self, args):
        """Handles the 'recruit' command."""
        if len(args) < 2:
            self.renderer.display_message("Usage: recruit [kingdom] [hero_name]", 'yellow')
            return
        kingdom_name = args[0]
        hero_name = " ".join(args[1:])
        kingdom = self.world.get_kingdom_by_name(kingdom_name)
        if not kingdom:
            self.renderer.display_message(f"Kingdom '{kingdom_name}' not found.", 'red')
            return
        hero_to_recruit = None
        for hero in self.world.available_heroes:
            if hero.name.lower() == hero_name.lower():
                hero_to_recruit = hero
                break
        if not hero_to_recruit:
            self.renderer.display_message(f"Hero '{hero_name}' not found or is not available.", 'red')
            return
        if kingdom.wealth < hero_to_recruit.cost:
            self.renderer.display_message(f"{kingdom.name} cannot afford to recruit {hero_to_recruit.name}. (Cost: {hero_to_recruit.cost}, Wealth: {kingdom.wealth})", 'red')
            return
        kingdom.wealth -= hero_to_recruit.cost
        kingdom.heroes.append(hero_to_recruit)
        hero_to_recruit.location = kingdom
        self.world.available_heroes.remove(hero_to_recruit)
        self.world.active_heroes.append(hero_to_recruit)
        self.renderer.display_message(f"{hero_to_recruit.name} has been recruited by {kingdom.name}!", 'green')
        self.renderer.display_world_state(self.world)
    def save_game(self):
        """Saves the current game state to a file."""
        try:
            with open(self.save_file_path, 'wb') as f:
                pickle.dump(self.world, f)
            self.renderer.display_message(f"The currents of time are frozen. Game saved to {self.save_file_path}.", 'cyan')
        except Exception as e:
            self.renderer.display_message(f"A cosmic interference prevents the save: {e}", 'red')
    def load_game(self):
        """Loads the game state from a file."""
        if not os.path.exists(self.save_file_path):
            self.renderer.display_message("No scroll of saved time is found.", 'yellow')
            return
        try:
            with open(self.save_file_path, 'rb') as f:
                self.world = pickle.load(f)
            self.renderer.display_message("The threads of a past timeline are restored. Game loaded.", 'cyan')
            self.renderer.display_world_state(self.world)
        except Exception as e:
            self.renderer.display_message(f"The scroll of time is corrupted and cannot be read: {e}", 'red')
def main():
    """Main function to run the game."""
    try:
        game = Game()
        game.run()
    except FileNotFoundError as e:
        print(f"{Fore.RED}Error: Game data file not found. Make sure you are running the game from the root directory.{Style.RESET_ALL}", file=sys.stderr)
        print(f"{Fore.RED}Details: {e}{Style.RESET_ALL}", file=sys.stderr)
    except Exception as e:
        print(f"{Fore.RED}An unexpected error has occurred, Great Oracle: {e}{Style.RESET_ALL}", file=sys.stderr)
if __name__ == "__main__":
    main()