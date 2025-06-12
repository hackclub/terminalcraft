import os 
import time 
import pickle 
import random 
import threading 
from pets .pet_base import Pet 
from pets .species import get_species_list ,create_pet 
from pets .customization import PetCustomization 
from simulation .needs import NeedsEngine 
from simulation .behavior import BehaviorEngine 
from simulation .weather import WeatherSystem 
from mini_games .feeding_game import FeedingGame 
from mini_games .training_game import TrainingGame 
from mini_games .social_game import SocialGame 
from mini_games .grooming_game import GroomingGame 
from mini_games .healing_game import HealingGame 
from mini_games .adventure_game import AdventureGame 
from systems .marketplace import Marketplace 
from pets .talents import get_talents_list 
from simulation .time_system import TimeSystem 
from systems .housing import HousingSystem 
def clear_screen ():
    os .system ('cls'if os .name =='nt'else 'clear')
class PetVerseGame :
    def __init__ (self ):
        self .pets =[]
        self .current_pet =None 
        self .last_update_time =time .time ()
        self .needs_engine =NeedsEngine ()
        self .behavior_engine =BehaviorEngine ()
        self .weather_system =WeatherSystem ()
        self .pet_customization =PetCustomization ()
        self .marketplace =Marketplace ()
        self .time_system =TimeSystem ()
        self .housing_system =HousingSystem ()
        self .game_log =[]
        self .weather_thread =threading .Thread (target =self .update_weather_loop ,daemon =True )
        self .weather_thread .start ()
        self .time_thread =threading .Thread (target =self .update_time_loop ,daemon =True )
        self .time_thread .start ()
        self .load_game ()
    def load_game (self ):
        try :
            with open ('save_data.pkl','rb')as f :
                save_data =pickle .load (f )
                self .pets =save_data .get ('pets',[])
                for pet in self .pets :
                    if not hasattr (pet ,'customization'):
                        pet .customization ={
                        "hat":"None",
                        "accessory":"None",
                        "color":"Default"
                        }
                    if not hasattr (pet ,'inventory'):
                        pet .inventory =[]
                    if not hasattr (pet ,'unlocked_customizations'):
                        pet .unlocked_customizations =[]
                    if not hasattr (pet ,'pet_coins'):
                        pet .pet_coins =0 
                    if not hasattr (pet ,'talents'):
                        pet .talents =[]
                    if not hasattr (pet ,'talent_points'):
                        pet .talent_points =0 
                if self .pets :
                    self .current_pet =self .pets [0 ]
                if 'weather'in save_data :
                    self .weather_system .current_weather =save_data ['weather']
                if 'unlocked_customizations'in save_data :
                    self .pet_customization .unlocked_items =save_data ['unlocked_customizations']
                if 'marketplace_data'in save_data :
                    self .marketplace .load_data (save_data ['marketplace_data'])
                if 'time_system_data'in save_data :
                    self .time_system .load_data (save_data ['time_system_data'])
                if 'housing_data'in save_data :
                    self .housing_system .load_data (save_data ['housing_data'])
                if 'game_log'in save_data :
                    self .game_log =save_data ['game_log']
                print ("Game loaded successfully!")
        except FileNotFoundError :
            print ("No saved game found. Starting new game.")
        except Exception as e :
            print (f"Error loading game: {e }")
    def save_game (self ):
        try :
            save_data ={
            'pets':self .pets ,
            'weather':self .weather_system .current_weather ,
            'unlocked_customizations':self .pet_customization .unlocked_items ,
            'marketplace_data':self .marketplace .save_data (),
            'time_system_data':self .time_system .save_data (),
            'housing_data':self .housing_system .save_data (),
            'game_log':self .game_log 
            }
            with open ('save_data.pkl','wb')as f :
                pickle .dump (save_data ,f )
            print ("Game saved successfully!")
        except Exception as e :
            print (f"Error saving game: {e }")
    def create_new_pet (self ):
        clear_screen ()
        print ("=== Create a New Pet ===")
        species_list =get_species_list ()
        print ("Available species:")
        for i ,species in enumerate (species_list ):
            print (f"{i +1 }. {species ['name']}")
        choice =int (input ("\nSelect a species (number): "))-1 
        if 0 <=choice <len (species_list ):
            name =input ("Give your pet a name: ")
            new_pet =create_pet (species_list [choice ],name )
            self .pets .append (new_pet )
            self .current_pet =new_pet 
            print (f"\nYou've created {name } the {species_list [choice ]['name']}!")
        else :
            print ("Invalid choice.")
    def select_pet (self ):
        if not self .pets :
            print ("You don't have any pets yet!")
            return 
        clear_screen ()
        print ("=== Select a Pet ===")
        for i ,pet in enumerate (self .pets ):
            print (f"{i +1 }. {pet .name } ({pet .species }) - {pet .age } days old")
        choice =int (input ("\nSelect a pet (number): "))-1 
        if 0 <=choice <len (self .pets ):
            self .current_pet =self .pets [choice ]
            print (f"\nYou selected {self .current_pet .name }!")
        else :
            print ("Invalid choice.")
    def update_weather_loop (self ):
        while True :
            if self .weather_system .update_weather ():
                print ("\nThe weather has changed!")
            for pet in self .pets :
                if pet .is_alive :
                    weather_resistance =0 
                    for talent in pet .talents :
                        if talent ['effect']['type']=='weather_resistance':
                            weather_resistance +=talent ['effect']['value']
                    self .weather_system .apply_weather_effects (pet ,weather_resistance )
            time .sleep (30 )
    def update_time_loop (self ):
        while True :
            self .time_system .update_time ()
            time .sleep (10 )
    def update_pets (self ):
        current_time =time .time ()
        elapsed_time =current_time -self .last_update_time 
        self .last_update_time =current_time 
        if elapsed_time >10 :
            current_phase =self .time_system .get_current_phase ()
            current_weather =self .weather_system .get_weather_name ()
            placed_furniture =self .housing_system .get_all_placed_furniture ()
            for pet in self .pets :
                if pet .is_alive :
                    events =self .needs_engine .update_needs (pet ,elapsed_time ,current_weather ,current_phase ,placed_furniture ,self .housing_system )
                    self .game_log .extend (events )
                    if len (self .game_log )>20 :
                        self .game_log =self .game_log [-20 :]
                    self .behavior_engine .update_behavior (pet ,current_phase )
                    pet .check_evolution ()
                    pet .age +=(elapsed_time /120 )
    def interact_with_pet (self ):
        if not self .current_pet :
            print ("You don't have a pet selected!")
            return 
        while True :
            if not self .current_pet .is_alive :
                print (f"{self .current_pet .name } has passed away. RIP.")
                return 
            clear_screen ()
            print (f"=== {self .current_pet .name } the {self .current_pet .species } ===")
            print (f"Time of Day: {self .time_system .get_current_phase ()}")
            print (f"Age: {self .current_pet .age :.1f} days")
            print (f"Evolution Stage: {self .current_pet .evolution_stage }")
            self .current_pet .display_needs ()
            print (f"Mood: {self .current_pet .mood }")
            print ("\nStats:")
            for stat ,value in self .current_pet .stats .items ():
                print (f"{stat .capitalize ()}: {value :.1f}/100")
            print (f"Current behavior: {self .current_pet .current_behavior }")
            print (f"PetCoins: {self .current_pet .pet_coins }")
            print (f"Talent Points: {self .current_pet .talent_points }")
            if self .game_log :
                print (f"\n[LOG] {self .game_log [-1 ]}")
            print ("\nWhat would you like to do?")
            print ("1. Feed")
            print ("2. Play")
            print ("3. Clean")
            print ("4. Train")
            print ("5. Rest")
            print ("6. Socialize")
            print ("7. Groom")
            print ("8. Heal")
            print ("9. Go on Adventure")
            print ("10. Customize Pet")
            print ("11. View Weather")
            print ("12. Enter Marketplace")
            print ("13. View Talents")
            print ("14. Manage Housing")
            print ("15. Back to main menu")
            choice =input ("\nEnter your choice: ")
            if choice =="1":
                feeding_game =FeedingGame ()
                success_level =feeding_game .play (self .current_pet .species )
                self .current_pet .feed (success_level )
                input ("\nPress Enter to continue...")
            elif choice =="2":
                self .current_pet .play ()
                input ("\nPress Enter to continue...")
            elif choice =="3":
                self .current_pet .clean ()
                input ("\nPress Enter to continue...")
            elif choice =="4":
                training_game =TrainingGame ()
                training_boost =self .current_pet .stats ['intelligence']/50.0 
                xp_boost =0.0 
                if any (t ['name']=='Quick Learner'for t in self .current_pet .talents ):
                    talent =next ((t for t in self .current_pet .talents if t ['name']=='Quick Learner'),None )
                    if talent :
                        xp_boost =talent ['effect']['value']
                        print ("Quick Learner talent is active! Gaining extra experience.")
                success_level ,xp_boost =training_game .play (self .current_pet .species ,training_boost ,xp_boost )
                self .current_pet .train (success_level ,xp_boost )
                input ("\nPress Enter to continue...")
            elif choice =="5":
                self .current_pet .rest ()
                input ("\nPress Enter to continue...")
            elif choice =="6":
                social_game =SocialGame ()
                charisma_boost =self .current_pet .stats ['charisma']/50.0 
                xp_boost =0.0 
                if any (t ['name']=='Quick Learner'for t in self .current_pet .talents ):
                    talent =next ((t for t in self .current_pet .talents if t ['name']=='Quick Learner'),None )
                    if talent :
                        xp_boost =talent ['effect']['value']
                        print ("Quick Learner talent is active! Gaining extra experience.")
                success_level ,xp_boost =social_game .play (self .current_pet .species ,charisma_boost ,xp_boost )
                self .current_pet .socialize (success_level ,xp_boost )
                input ("\nPress Enter to continue...")
            elif choice =="7":
                grooming_game =GroomingGame ()
                success_level =grooming_game .play (self .current_pet .species )
                self .current_pet .groom (success_level )
                input ("\nPress Enter to continue...")
            elif choice =="8":
                healing_game =HealingGame ()
                success_level =healing_game .play (self .current_pet .species )
                self .current_pet .heal (success_level )
                input ("\nPress Enter to continue...")
            elif choice =="9":
                adventure_game =AdventureGame ()
                adventure_luck =self .current_pet .stats ['intelligence']/200.0 
                xp_boost =0.0 
                if any (t ['name']=='Quick Learner'for t in self .current_pet .talents ):
                    talent =next ((t for t in self .current_pet .talents if t ['name']=='Quick Learner'),None )
                    if talent :
                        xp_boost =talent ['effect']['value']
                        print ("Quick Learner talent is active! Gaining extra experience.")
                success_level ,found_treasure ,coins_earned ,xp_boost =adventure_game .play (self .current_pet .species ,self .current_pet .stats ,adventure_luck ,xp_boost )
                self .current_pet .go_adventure (success_level ,found_treasure ,xp_boost ,coins_earned )
                input ("\nPress Enter to continue...")
            elif choice =="10":
                self .customize_pet ()
            elif choice =="11":
                self .display_weather ()
            elif choice =="12":
                self .enter_marketplace ()
            elif choice =="13":
                self .view_talents ()
            elif choice =="14":
                self .manage_housing ()
            elif choice =="15":
                break 
            else :
                print ("Invalid choice.")
                input ("\nPress Enter to continue...")
    def customize_pet (self ):
        if not self .current_pet :
            print ("You don't have a pet selected!")
            return 
        clear_screen ()
        print (f"=== Customize {self .current_pet .name } ===\n")
        print ("Current Customization:")
        for category ,item in self .current_pet .customization .items ():
            print (f"{category .capitalize ()}: {item }")
        print ("\nAvailable Categories:")
        print ("1. Hats")
        print ("2. Accessories")
        print ("3. Colors")
        print ("4. Back")
        category_choice =input ("\nSelect a category: ")
        if category_choice =="4":
            return 
        category_map ={"1":"hat","2":"accessory","3":"color"}
        if category_choice in category_map :
            category =category_map [category_choice ]
            available_items =self .pet_customization .get_available_items (category ,self .current_pet .unlocked_customizations )
            clear_screen ()
            print (f"=== Available {category .capitalize ()}s ===\n")
            if not available_items :
                print ("No items available in this category yet.")
                input ("\nPress Enter to continue...")
                return 
            for i ,item in enumerate (available_items ):
                print (f"{i +1 }. {item ['name']} - {item ['description']}")
            print (f"{len (available_items )+1 }. Back")
            item_choice =input ("\nSelect an item: ")
            try :
                item_index =int (item_choice )-1 
                if 0 <=item_index <len (available_items ):
                    selected_item =available_items [item_index ]
                    self .current_pet .customize (category ,selected_item ['name'])
                    input ("\nPress Enter to continue...")
            except ValueError :
                pass 
    def display_weather (self ):
        """Display the current weather and its effects"""
        clear_screen ()
        print ("=== Current Weather ===\n")
        weather =self .weather_system .current_weather 
        weather_name =weather ["name"]
        weather_effects =weather ["effects"]
        print (f"Current Weather: {weather_name }")
        print (f"Description: {self .weather_system .get_weather_description ()}")
        print ("\nEffects on Pets:")
        for need ,effect in weather_effects .items ():
            effect_str =f"+{effect }"if effect >0 else str (effect )
            print (f"{need .capitalize ()}: {effect_str }")
        if self .current_pet :
            print (f"\nSpecies-specific effects for {self .current_pet .species }:")
            has_special_effect =False 
            if weather_name =="Rainy"and self .current_pet .species =="Aqualing":
                print ("Happiness: +5.0 (Aqualings enjoy rain)")
                has_special_effect =True 
            if weather_name =="Sunny"and self .current_pet .species =="Emberspark":
                print ("Energy: +5.0 (Embersparks thrive in sunshine)")
                has_special_effect =True 
            if weather_name =="Snowy"and self .current_pet .species =="Fluffball":
                print ("Happiness: +5.0 (Fluffballs love snow)")
                has_special_effect =True 
            if not has_special_effect :
                print ("No special effects for this species.")
        input ("\nPress Enter to continue...")
    def enter_marketplace (self ):
        clear_screen ()
        print ("=== Welcome to the Marketplace! ===")
        print (f"You have {self .current_pet .pet_coins } PetCoins.")
        while True :
            print ("\n1. Buy Items")
            print ("2. Sell Items")
            print ("3. Exit Marketplace")
            choice =input ("\nEnter your choice: ")
            if choice =="1":
                self .buy_from_marketplace ()
            elif choice =="2":
                self .sell_to_marketplace ()
            elif choice =="3":
                break 
            else :
                print ("Invalid choice.")
        input ("\nPress Enter to continue...")
    def buy_from_marketplace (self ):
        clear_screen ()
        print ("=== Items for Sale ===")
        available_items =self .marketplace .get_available_items ()
        category_choice =self ._select_category (available_items .keys ())
        if not category_choice :
            return 
        items_in_category =available_items [category_choice ]
        self ._display_items (items_in_category )
        try :
            item_idx =int (input ("\nSelect an item to buy (number): "))-1 
            if 0 <=item_idx <len (items_in_category ):
                item_to_buy =items_in_category [item_idx ]
                if self .marketplace .buy_item (self .current_pet ,item_to_buy ):
                    if item_to_buy .get ('type')=='Furniture':
                        self .housing_system .buy_furniture (item_to_buy )
            else :
                print ("Invalid item number.")
        except ValueError :
            print ("Invalid input.")
        input ("\nPress Enter to continue...")
    def sell_to_marketplace (self ):
        clear_screen ()
        print ("=== Your Inventory ===")
        if not self .current_pet .inventory :
            print ("Your inventory is empty.")
            input ("\nPress Enter to continue...")
            return 
        self ._display_items (self .current_pet .inventory )
        try :
            item_idx =int (input ("\nSelect an item to sell (number): "))-1 
            if 0 <=item_idx <len (self .current_pet .inventory ):
                item_to_sell =self .current_pet .inventory [item_idx ]
                self .marketplace .sell_item (self .current_pet ,item_to_sell ['name'])
            else :
                print ("Invalid item number.")
        except ValueError :
            print ("Invalid input.")
        input ("\nPress Enter to continue...")
    def _select_category (self ,categories ):
        print ("\nSelect a category:")
        cat_list =list (categories )
        for i ,cat in enumerate (cat_list ):
            print (f"{i +1 }. {cat .capitalize ()}")
        try :
            choice =int (input ("\nEnter your choice: "))-1 
            if 0 <=choice <len (cat_list ):
                return cat_list [choice ]
        except ValueError :
            print ("Invalid input.")
        return None 
    def _display_items (self ,items ):
        for i ,item in enumerate (items ):
            price =item .get ('price','N/A')
            desc =item .get ('description','')
            print (f"{i +1 }. {item ['name']} - Price: {price } - {desc }")
    def view_talents (self ):
        clear_screen ()
        print ("=== Pet Talents ===")
        print (f"Talent Points: {self .current_pet .talent_points }")
        print ("\nLearned Talents:")
        if not self .current_pet .talents :
            print ("None")
        else :
            for talent in self .current_pet .talents :
                print (f"- {talent ['name']}: {talent ['description']}")
        print ("\nAvailable Talents:")
        available_talents =[t for t in get_talents_list ()if t not in self .current_pet .talents ]
        if not available_talents :
            print ("No new talents to learn.")
        else :
            for i ,talent in enumerate (available_talents ):
                print (f"{i +1 }. {talent ['name']} (Cost: {talent ['cost']}) - {talent ['description']}")
        try :
            choice =int (input ("\nSelect a talent to learn (number), or 0 to go back: "))
            if choice ==0 :
                return 
            if 1 <=choice <=len (available_talents ):
                self .current_pet .learn_talent (available_talents [choice -1 ])
            else :
                print ("Invalid choice.")
        except ValueError :
            print ("Invalid input.")
        input ("\nPress Enter to continue...")
    def manage_housing (self ):
        while True :
            clear_screen ()
            print ("=== Housing Management ===")
            for room ,details in self .housing_system .rooms .items ():
                print (f"\n--- {room } ---")
                if not details ['furniture']:
                    print ("Empty")
                else :
                    for item in details ['furniture']:
                        print (f"- {item ['name']}")
            print ("\n--- Unplaced Furniture ---")
            if not self .housing_system .owned_furniture :
                print ("None")
            else :
                for i ,item in enumerate (self .housing_system .owned_furniture ):
                    print (f"{i +1 }. {item ['name']}")
            print ("\nOptions:")
            print ("1. Place Furniture")
            print ("2. Back to Pet Menu")
            choice =input ("\nEnter your choice: ")
            if choice =='1':
                self ._place_furniture ()
            elif choice =='2':
                break 
            else :
                print ("Invalid choice.")
                time .sleep (1 )
    def _place_furniture (self ):
        clear_screen ()
        print ("=== Place Furniture ===")
        if not self .housing_system .owned_furniture :
            print ("You have no furniture to place.")
            input ("\nPress Enter to continue...")
            return 
        print ("Select furniture to place:")
        for i ,item in enumerate (self .housing_system .owned_furniture ):
            print (f"{i +1 }. {item ['name']}")
        try :
            furniture_choice =int (input ("\nEnter your choice (or 0 to cancel): "))
            if furniture_choice ==0 :
                return 
            if not (1 <=furniture_choice <=len (self .housing_system .owned_furniture )):
                print ("Invalid choice.")
                time .sleep (1 )
                return 
            selected_furniture =self .housing_system .owned_furniture [furniture_choice -1 ]
            print ("\nSelect a room:")
            rooms =list (self .housing_system .rooms .keys ())
            for i ,room in enumerate (rooms ):
                print (f"{i +1 }. {room }")
            room_choice =int (input ("\nEnter your choice (or 0 to cancel): "))
            if room_choice ==0 :
                return 
            if not (1 <=room_choice <=len (rooms )):
                print ("Invalid choice.")
                time .sleep (1 )
                return 
            selected_room =rooms [room_choice -1 ]
            self .housing_system .add_furniture_to_room (selected_furniture ,selected_room )
        except ValueError :
            print ("Invalid input.")
        input ("\nPress Enter to continue...")
    def main_menu (self ):
        while True :
            self .update_pets ()
            clear_screen ()
            print ("=== PetVerse: Virtual Pet Simulator ===")
            if self .current_pet and self .current_pet .is_alive :
                print (f"\nCurrent pet: {self .current_pet .name } the {self .current_pet .species }")
                print (f"Mood: {self .current_pet .mood }")
                print (f"Behavior: {self .current_pet .current_behavior }")
            if self .game_log :
                print (f"\n[LOG] {self .game_log [-1 ]}")
            print ("\n1. Create new pet")
            print ("2. Select pet")
            print ("3. Interact with current pet")
            print ("4. Save game")
            print ("5. Exit")
            choice =input ("\nEnter your choice: ")
            if choice =="1":
                self .create_new_pet ()
                input ("\nPress Enter to continue...")
            elif choice =="2":
                self .select_pet ()
                input ("\nPress Enter to continue...")
            elif choice =="3":
                self .interact_with_pet ()
            elif choice =="4":
                self .save_game ()
                input ("\nPress Enter to continue...")
            elif choice =="5":
                self .save_game ()
                print ("Thanks for playing PetVerse!")
                break 
if __name__ =="__main__":
    os .makedirs ("saves",exist_ok =True )
    game =PetVerseGame ()
    game .main_menu ()