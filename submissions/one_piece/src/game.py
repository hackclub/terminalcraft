#!/usr/bin/env python3
import os
import random
import sys
import time
from typing import Dict, List, Any, Optional, Tuple
from characters import Character, create_character
from locations import get_location, Location
from events import trigger_random_event
from items import Item
import utils
class Game:
    def __init__(self):
        self.player = None
        self.current_location = None
        self.inventory: List[Item] = []
        self.turn_count = 0
        self.time_limit = 50  
        self.game_state = {
            "current_level": 6,  
            "allies": [],        
            "enemies": [],       
            "discovered_areas": set(),  
            "flags": {},         
            "health": 100,       
            "disguised": False,  
        }
    def initialize_game(self):
        """Set up the game world and player character."""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.display_intro()
        print("\nBefore we begin, tell me about yourself, prisoner...")
        name = input("What is your name? ").strip()
        background_choice = utils.get_choice(
            "What was your life before imprisonment?",
            ["Pirate", "Revolutionary", "Former Marine", "Civilian caught in the crossfire"]
        )
        crime_choice = utils.get_choice(
            "What heinous 'crime' brought you to Impel Down?",
            ["Defied the World Government", "Crossed a Celestial Dragon", 
             "Knew too much about the Void Century", "Associated with infamous pirates"]
        )
        backgrounds = ["Pirate", "Revolutionary", "Former Marine", "Civilian caught in the crossfire"]
        crimes = ["Defied the World Government", "Crossed a Celestial Dragon", 
                 "Knew too much about the Void Century", "Associated with infamous pirates"]
        self.player = create_character(name, backgrounds[background_choice], crimes[crime_choice])
        location = get_location("level_6_cell")
        if location is None:
            print("Error: Starting location not found. Game cannot continue.")
            sys.exit(1)
        self.current_location = location
        self.game_state['discovered_areas'].add(self.current_location.id)
        self.display_game_start()
    def display_intro(self):
        """Display the game's introduction screen."""
        utils.slow_print("""
    ______                                  _____                         _   _____                     
   |  ____|                                |_   _|                       | | |  __ \\                    
   | |__   ___  ___ __ _ _ __   ___  __   __ | |  _ __ ___  _ __   ___  | | | |  | | _____      ___ __  
   |  __| / __|/ __/ _` | '_ \\ / _ \\ \\ \\ / / | | | '_ ` _ \\| '_ \\ / _ \\ | | | |  | |/ _ \\ \\ /\\ / / '_ \\ 
   | |____\\__ \\ (_| (_| | |_) |  __/  \\ V / _| |_| | | | | | |_) |  __/ | | | |__| | (_) \\ V  V /| | | |
   |______|___/\\___\\__,_| .__/ \\___|   \\_/ |_____|_| |_| |_| .__/ \\___| |_| |_____/ \\___/ \\_/\\_/ |_| |_|
                        | |                                 | |                                          
                        |_|                                 |_|                                          
        """, color=utils.TITLE_COLOR)
        intro_text = """
Welcome to the most secure underwater prison of the World Government.
Six levels of hell await those who dare to challenge the world's justice.
Many have entered... None have escaped.
        """
        box = utils.create_box(intro_text, width=80, color=utils.DIVIDER_COLOR)
        utils.slow_print(box, delay=0.01)
    def display_game_start(self):
        """Display the game's starting scenario."""
        utils.clear_screen()
        start_title = utils.display_title("THE ESCAPE BEGINS", width=80, char="═")
        print(start_title)
        print(f"{utils.DIVIDER_COLOR}┃")
        scenario_text = """
The air is thick and stale in your cell on Level 6 of Impel Down, 
the World Government's inescapable underwater prison.
Just as you're contemplating another day of endless torment, 
you hear distant explosions, followed by screams and the sounds of combat.
{explosion}*BOOM* A massive explosion rocks the entire level!{reset}
The cell doors around you begin to malfunction, their seastone locks disengaging.
Your own cell door slowly creaks open...
{question}Freedom? Or just another kind of hell?
The choice is yours.{reset}
""".format(
            explosion=utils.Fore.RED + utils.Style.BRIGHT,
            question=utils.Fore.YELLOW + utils.Style.BRIGHT,
            reset=utils.Style.RESET_ALL
        )
        for line in scenario_text.split('\n'):
            if line.strip():
                utils.slow_print(f"{utils.DIVIDER_COLOR}┃ {line}", delay=0.04)
            else:
                utils.slow_print(f"{utils.DIVIDER_COLOR}┃", delay=0.01)
        print(f"{utils.DIVIDER_COLOR}┃")
        print(f"{utils.create_vertical_divider(80)}")
        input(f"\n{utils.PROMPT_COLOR}Press Enter to begin your escape...{utils.Style.RESET_ALL}\n")
    def display_status(self):
        """Show the player's current status."""
        utils.clear_screen()
        top_border = utils.create_vertical_divider(80)
        print(f"\n{top_border}")
        if self.current_location is None:
            print(f"{utils.Fore.RED}ERROR: No current location")
            return
        location_info = f"{utils.LOCATION_COLOR}LOCATION: {self.current_location.name} (Level {self.game_state['current_level']})"
        print(f"┃ {location_info}")
        health_bar = utils.display_health_bar(self.game_state['health'])
        print(f"┃ HEALTH: {health_bar}")
        turn_color = utils.Fore.YELLOW if self.turn_count > (self.time_limit * 0.7) else utils.Fore.WHITE
        print(f"┃ TURN: {turn_color}{self.turn_count}/{self.time_limit}")
        if self.game_state['disguised']:
            print(f"┃ {utils.Fore.GREEN}STATUS: Disguised as a guard")
        if self.inventory:
            print(f"┃")
            print(f"┃ {utils.INVENTORY_COLOR}INVENTORY:")
            for item in self.inventory:
                print(f"┃ {utils.Fore.WHITE}- {item.name}")
        if self.game_state['allies']:
            print(f"┃")
            print(f"┃ {utils.ALLY_COLOR}ALLIES:")
            for ally in self.game_state['allies']:
                print(f"┃ {utils.Fore.WHITE}- {ally.name}")
        bottom_border = utils.create_vertical_divider(80)
        print(f"{bottom_border}\n")
    def process_turn(self):
        """Process a single game turn."""
        self.turn_count += 1
        if self.turn_count >= self.time_limit:
            return self.poison_ending()
        self.display_status()
        if self.current_location is None:
            print("ERROR: No current location. Game cannot continue.")
            return False
        print(self.current_location.description)
        if self.turn_count > self.time_limit - 10 and not self.game_state.get('poison_warning', False):
            utils.slow_print("\nA prison-wide announcement blares: 'WARNING! POISON GAS WILL BE RELEASED SOON! ALL PERSONNEL EVACUATE!'")
            self.game_state['poison_warning'] = True
        if random.random() < 0.2:
            event_result = trigger_random_event(self.game_state, self.current_location, self.inventory)
            if event_result.get('game_over'):
                return False
            for key, value in event_result.items():
                if key == 'message':
                    utils.slow_print(value)
                elif key == 'item_add' and value:
                    self.inventory.append(value)
                    utils.slow_print(f"\nYou acquired: {value.name}")
                elif key == 'item_remove' and value in self.inventory:
                    self.inventory.remove(value)
                elif key == 'health':
                    self.game_state['health'] += value
                    if value < 0:
                        utils.slow_print(f"\nYou took {abs(value)} damage!")
                    else:
                        utils.slow_print(f"\nYou recovered {value} health!")
                    if self.game_state['health'] <= 0:
                        return self.death_ending("Your injuries were too severe.")
        options = self.current_location.get_options(self.game_state, self.inventory)
        for item in self.inventory:
            if item.can_use_at(self.current_location.id):
                options.append({
                    'text': f"Use {item.name}",
                    'action': 'use_item',
                    'item_id': item.id
                })
        options.append({'text': 'Wait and observe', 'action': 'wait'})
        print(f"{utils.DIVIDER_COLOR}┃")
        print(f"{utils.DIVIDER_COLOR}┃ {utils.TITLE_COLOR}YOUR OPTIONS:")
        print(f"{utils.DIVIDER_COLOR}┃")
        choice_idx = utils.get_choice("What will you do?", [opt['text'] for opt in options])
        chosen_option = options[choice_idx]
        return self.process_action(chosen_option)
    def process_action(self, option):
        """Process the player's chosen action."""
        action_type = option.get('action', '')
        if action_type == 'move':
            target_location = get_location(option['target_location'])
            if target_location is None:
                print(f"ERROR: Could not find location {option['target_location']}.")
                return True
            self.current_location = target_location
            self.game_state['discovered_areas'].add(self.current_location.id)
            if 'new_level' in option and option['new_level'] != self.game_state['current_level']:
                self.game_state['current_level'] = option['new_level']
                utils.slow_print(f"\nYou've reached Level {self.game_state['current_level']}!")
                if option['new_level'] == 1:
                    utils.slow_print("\nYou can almost taste freedom! The sea breeze is getting stronger.")
        elif action_type == 'use_item':
            item_id = option.get('item_id')
            item = next((i for i in self.inventory if i.id == item_id), None)
            if item:
                result = item.use(self.game_state, self.current_location)
                utils.slow_print(result['message'])
                if result.get('consume', False):
                    self.inventory.remove(item)
                for effect, value in result.items():
                    if effect == 'disguise':
                        self.game_state['disguised'] = value
                    elif effect == 'health':
                        self.game_state['health'] += value
                    elif effect == 'move_to':
                        new_location = get_location(value)
                        if new_location is not None:
                            self.current_location = new_location
                        else:
                            print(f"ERROR: Could not find location {value}.")
                    elif effect == 'add_flag':
                        self.game_state['flags'][value] = True
                    elif effect == 'remove_flag':
                        if value in self.game_state['flags']:
                            del self.game_state['flags'][value]
        elif action_type == 'story':
            event_id = option.get('event_id')
            result = self.process_story_event(event_id)
            if result.get('game_over'):
                return False
            if result.get('move_to'):
                new_location = get_location(result['move_to'])
                if new_location is not None:
                    self.current_location = new_location
                else:
                    print(f"ERROR: Could not find location {result['move_to']}.")
        elif action_type == 'wait':
            utils.slow_print("\nYou wait and observe your surroundings carefully...")
            if random.random() < 0.3:
                discoveries = [
                    "You notice a small crack in the wall that wasn't visible before.",
                    "You overhear guards mentioning a shift change in 10 minutes.",
                    "You spot a loose stone that might be hiding something.",
                    "You notice the patrol pattern of the guards more clearly now."
                ]
                utils.slow_print(random.choice(discoveries))
        if self.current_location is not None and self.current_location.id == "marine_ship" and not self.game_state.get('ending_triggered'):
            return self.escape_ending()
        return True  
    def process_story_event(self, event_id):
        """Process a special story event."""
        result = {'message': '', 'game_over': False}
        if event_id == 'meet_crocodile':
            utils.slow_print("""
Sir Crocodile stands before you, arms crossed and a cold stare fixed on your face.
"So, you're trying to escape too?" he says with a smirk. "I could use someone expendable."
            """)
            choice = utils.get_choice(
                "How do you respond?",
                ["Accept his offer - 'I'll help you escape.'",
                 "Decline - 'I work alone.'",
                 "Threaten - 'Get out of my way or I'll alert the guards.'"]
            )
            if choice == 0:  
                utils.slow_print("""
"Smart choice," Crocodile says with a cold smile. "Stay close and do exactly as I say."
Crocodile joins you as an ally, albeit a dangerous one.
                """)
                self.game_state['allies'].append(create_character("Sir Crocodile", "Shichibukai", "Former Warlord"))
                self.game_state['flags']['crocodile_alliance'] = True
            elif choice == 1:  
                utils.slow_print("""
"Suit yourself," Crocodile scoffs. "We'll see how far you get alone."
He walks away, neither helping nor hindering you.
                """)
            else:  
                utils.slow_print("""
Crocodile's face darkens. "Bad choice."
Before you can react, he uses his Devil Fruit power. Sand swirls around you,
drying you out and draining your strength.
"Consider that a warning. Cross me again, and I won't be so merciful."
                """)
                self.game_state['health'] -= 30
                self.game_state['enemies'].append(create_character("Sir Crocodile", "Shichibukai", "Former Warlord"))
                self.game_state['flags']['crocodile_enemy'] = True
                if self.game_state['health'] <= 0:
                    result['message'] = "Crocodile's attack was too powerful. You collapse, completely drained."
                    result['game_over'] = True
        elif event_id == 'meet_bon_clay':
            utils.slow_print("""
A voice calls out to you. "Psst! Over here!"
You turn to see a strange man with makeup and ballet attire.
"I'm Bon Clay! But you can call me Bon-chan! Want to escape together?"
            """)
            choice = utils.get_choice(
                "How do you respond?",
                ["Accept his help - 'I could use a friend.'",
                 "Suspicious - 'Why should I trust you?'",
                 "Reject - 'Stay away from me.'"]
            )
            if choice == 0:  
                utils.slow_print("""
"Yay! Friends to the end!" Bon Clay pirouettes with joy.
"I know many secrets of this prison. Together, we'll be unstoppable!"
Bon Clay joins you as a loyal ally.
                """)
                self.game_state['allies'].append(create_character("Bon Clay", "Okama", "Former Baroque Works Officer"))
                self.game_state['flags']['bon_clay_alliance'] = True
            elif choice == 1:  
                utils.slow_print("""
"Smart to be cautious!" Bon Clay nods approvingly. "I was a prisoner like you.
I worked with Straw Hat Luffy before. I believe in friendship and freedom!"
After his explanation, you feel you can trust him.
Bon Clay joins you as an ally.
                """)
                self.game_state['allies'].append(create_character("Bon Clay", "Okama", "Former Baroque Works Officer"))
                self.game_state['flags']['bon_clay_alliance'] = True
            else:  
                utils.slow_print("""
"How cold!" Bon Clay looks genuinely hurt. "Fine, I'll find my own way out.
But remember, in a place like this, friends are more valuable than treasure!"
He dances away, disappointment clear in his movements.
                """)
        return result
    def escape_ending(self):
        """Player successfully escapes Impel Down."""
        utils.clear_screen()
        ending_title = utils.display_title("FREEDOM AT LAST", width=80, char="═")
        print(ending_title)
        print(f"{utils.DIVIDER_COLOR}┃")
        if 'bon_clay_sacrifice' in self.game_state['flags']:
            ending_text = """
As the Marine ship carries you away from Impel Down, you look back at the looming prison.
Somewhere inside, Bon Clay is fighting for your freedom, sacrificing himself so you could escape.
"Thank you, Bon-chan," you whisper, tears in your eyes. "I will never forget you."
The prison grows smaller on the horizon, and with it, the sacrifice of a true friend fades from view,
but never from memory.
You've escaped Impel Down, but at a heavy cost.
            """
            for line in ending_text.split('\n'):
                if line.strip():
                    utils.slow_print(f"{utils.DIVIDER_COLOR}┃ {utils.Fore.CYAN}{line}", delay=0.04)
                else:
                    utils.slow_print(f"{utils.DIVIDER_COLOR}┃", delay=0.01)
        elif 'sea_king_escape' in self.game_state['flags']:
            ending_text = """
Riding on the back of a Sea King, you speed away from Impel Down.
The massive creature, somehow tamed by your mysterious ally, dives and resurfaces,
putting greater distance between you and the underwater hell with each passing moment.
Marines ships fire cannon balls in your direction, but they fall short as you disappear into the mist.
Freedom tastes as salty as the sea spray on your face.
You've successfully escaped Impel Down in the most spectacular way possible!
            """
            for line in ending_text.split('\n'):
                if line.strip():
                    utils.slow_print(f"{utils.DIVIDER_COLOR}┃ {utils.Fore.CYAN}{line}", delay=0.04)
                else:
                    utils.slow_print(f"{utils.DIVIDER_COLOR}┃", delay=0.01)
        else:
            ending_text = """
The stolen Marine ship cuts through the waves, carrying you away from Impel Down.
As the imposing structure recedes into the distance, you finally allow yourself to breathe.
You've done the impossible. You've escaped from the inescapable prison.
What awaits you now in this vast, dangerous world? New adventures? Revenge?
Or perhaps, finally, peace?
Whatever comes next, you know one thing for certain - you are free.
            """
            for line in ending_text.split('\n'):
                if line.strip():
                    utils.slow_print(f"{utils.DIVIDER_COLOR}┃ {utils.Fore.CYAN}{line}", delay=0.04)
                else:
                    utils.slow_print(f"{utils.DIVIDER_COLOR}┃", delay=0.01)
        print(f"{utils.DIVIDER_COLOR}┃")
        print(f"{utils.create_vertical_divider(80)}\n")
        game_over_ascii = """
             _____          __  __ ______    ______      ________ _____  
            / ____|   /\\   |  \\/  |  ____|  / __ \\ \\    / /  ____|  __ \\ 
           | |  __   /  \\  | \\  / | |__    | |  | \\ \\  / /| |__  | |__) |
           | | |_ | / /\\ \\ | |\\/| |  __|   | |  | |\\ \\/ / |  __| |  _  / 
           | |__| |/ ____ \\| |  | | |____  | |__| | \\  /  | |____| | \\ \\ 
            \\_____/_/    \\_\\_|  |_|______|  \\____/   \\/   |______|_|  \\_\\
        """
        utils.slow_print(utils.TITLE_COLOR + game_over_ascii, delay=0.01)
        stats_box = utils.create_vertical_divider(80)
        print(f"\n{stats_box}")
        print(f"{utils.DIVIDER_COLOR}┃ {utils.TITLE_COLOR}FINAL STATS:")
        print(f"{utils.DIVIDER_COLOR}┃ {utils.Fore.YELLOW}Turns taken: {self.turn_count}/{self.time_limit}")
        health_color = utils.HEALTH_COLOR if self.game_state['health'] > 30 else utils.LOW_HEALTH_COLOR
        print(f"{utils.DIVIDER_COLOR}┃ {utils.Fore.WHITE}Health remaining: {health_color}{self.game_state['health']}%")
        allies_text = ", ".join(ally.name for ally in self.game_state['allies'])
        if allies_text:
            print(f"{utils.DIVIDER_COLOR}┃ {utils.Fore.WHITE}Allies at the end: {utils.ALLY_COLOR}{allies_text}")
        else:
            print(f"{utils.DIVIDER_COLOR}┃ {utils.Fore.WHITE}Allies at the end: {utils.Fore.RED}None (solo escape)")
        print(f"{stats_box}")
        return False  
    def poison_ending(self):
        """Player is caught in Magellan's poison flood."""
        utils.clear_screen()
        poison_title = utils.display_title("POISON CLAIMS ANOTHER VICTIM", width=80, char="═")
        print(poison_title)
        print(f"{utils.DIVIDER_COLOR}┃")
        ending_text = """
Alarms blare throughout the prison. "EMERGENCY PROTOCOL INITIATED."
{poison}Suddenly, a wave of purple poison begins flowing through the corridor.{reset}
You try to run, but it's too late. {poison}The poison cloud envelops you...{reset}
Your lungs burn. Your vision blurs. Your strength fails.
As consciousness fades, you hear the heavy footsteps of Magellan approaching.
{voice}"No one escapes Impel Down,"{reset} his voice echoes as darkness claims you.
        """.format(
            poison=utils.Fore.MAGENTA + utils.Style.BRIGHT,
            voice=utils.Fore.RED + utils.Style.BRIGHT,
            reset=utils.Style.RESET_ALL
        )
        for line in ending_text.split('\n'):
            if line.strip():
                utils.slow_print(f"{utils.DIVIDER_COLOR}┃ {line}", delay=0.04)
            else:
                utils.slow_print(f"{utils.DIVIDER_COLOR}┃", delay=0.01)
        print(f"{utils.DIVIDER_COLOR}┃")
        print(f"{utils.create_vertical_divider(80)}\n")
        game_over_ascii = """
             _____          __  __ ______    ______      ________ _____  
            / ____|   /\\   |  \\/  |  ____|  / __ \\ \\    / /  ____|  __ \\ 
           | |  __   /  \\  | \\  / | |__    | |  | \\ \\  / /| |__  | |__) |
           | | |_ | / /\\ \\ | |\\/| |  __|   | |  | |\\ \\/ / |  __| |  _  / 
           | |__| |/ ____ \\| |  | | |____  | |__| | \\  /  | |____| | \\ \\ 
            \\_____/_/    \\_\\_|  |_|______|  \\____/   \\/   |______|_|  \\_\\
        """
        utils.slow_print(utils.Fore.RED + game_over_ascii, delay=0.01)
        return False  
    def death_ending(self, reason):
        """Player dies during escape attempt."""
        utils.clear_screen()
        death_title = utils.display_title("YOUR JOURNEY ENDS HERE", width=80, char="═")
        print(death_title)
        print(f"{utils.DIVIDER_COLOR}┃")
        ending_text = f"""
{utils.Fore.RED}{reason}{utils.Style.RESET_ALL}
Your vision fades as strength leaves your body. The sounds of chaos in Impel Down 
grow distant as darkness closes in.
Your escape attempt ends here, another soul claimed by the world's most fearsome prison.
        """
        for line in ending_text.split('\n'):
            if line.strip():
                utils.slow_print(f"{utils.DIVIDER_COLOR}┃ {line}", delay=0.04)
            else:
                utils.slow_print(f"{utils.DIVIDER_COLOR}┃", delay=0.01)
        print(f"{utils.DIVIDER_COLOR}┃")
        print(f"{utils.create_vertical_divider(80)}\n")
        game_over_ascii = """
             _____          __  __ ______    ______      ________ _____  
            / ____|   /\\   |  \\/  |  ____|  / __ \\ \\    / /  ____|  __ \\ 
           | |  __   /  \\  | \\  / | |__    | |  | \\ \\  / /| |__  | |__) |
           | | |_ | / /\\ \\ | |\\/| |  __|   | |  | |\\ \\/ / |  __| |  _  / 
           | |__| |/ ____ \\| |  | | |____  | |__| | \\  /  | |____| | \\ \\ 
            \\_____/_/    \\_\\_|  |_|______|  \\____/   \\/   |______|_|  \\_\\
        """
        utils.slow_print(utils.Fore.RED + game_over_ascii, delay=0.01)
        return False  
    def run(self):
        """Run the main game loop."""
        self.initialize_game()
        game_running = True
        while game_running:
            game_running = self.process_turn()
            if game_running:
                input("\nPress Enter to continue...\n")
        play_again = input("\nWould you like to play again? (y/n): ").lower().strip() == 'y'
        if play_again:
            self.__init__()
            self.run()
        else:
            print("\nThank you for playing One Piece: Escape from Impel Down!")
if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        print("\nGame terminated by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Game terminated unexpectedly.") 