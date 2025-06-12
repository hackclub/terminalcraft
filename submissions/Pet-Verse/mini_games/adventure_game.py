import random 
import os 
import time 
class AdventureGame :
    def __init__ (self ):
        self .adventure_locations =[
        {"name":"Forest","difficulty":0.8 ,"preferred_by":["Leafling","Fluffball"]},
        {"name":"Mountain","difficulty":1.2 ,"preferred_by":["Stoneshell","Emberspark"]},
        {"name":"Lake","difficulty":1.0 ,"preferred_by":["Aqualing"]},
        {"name":"Cave","difficulty":1.5 ,"preferred_by":["Stoneshell","Emberspark"]},
        {"name":"Meadow","difficulty":0.7 ,"preferred_by":["Fluffball","Leafling"]}
        ]
        self .treasures =[
        {"name":"Shiny Stone","rarity":"common","stat_boost":{"strength":1.0 }},
        {"name":"Magic Leaf","rarity":"common","stat_boost":{"intelligence":1.0 }},
        {"name":"Swift Feather","rarity":"common","stat_boost":{"agility":1.0 }},
        {"name":"Friendly Flower","rarity":"common","stat_boost":{"charisma":1.0 }},
        {"name":"Crystal Gem","rarity":"uncommon","stat_boost":{"strength":2.0 ,"intelligence":1.0 }},
        {"name":"Ancient Scroll","rarity":"uncommon","stat_boost":{"intelligence":2.0 ,"charisma":1.0 }},
        {"name":"Golden Acorn","rarity":"uncommon","stat_boost":{"agility":2.0 ,"strength":1.0 }},
        {"name":"Rainbow Shell","rarity":"uncommon","stat_boost":{"charisma":2.0 ,"agility":1.0 }},
        {"name":"Legendary Artifact","rarity":"rare","stat_boost":{"strength":3.0 ,"intelligence":2.0 ,"agility":1.0 }},
        {"name":"Ancient Crown","rarity":"rare","stat_boost":{"charisma":3.0 ,"intelligence":2.0 ,"strength":1.0 }}
        ]
        self .obstacles =[
        {"name":"Fallen Tree","skill_check":"strength","difficulty":0.8 },
        {"name":"Puzzle Lock","skill_check":"intelligence","difficulty":1.0 },
        {"name":"Narrow Ledge","skill_check":"agility","difficulty":1.2 },
        {"name":"Territorial Animal","skill_check":"charisma","difficulty":0.9 },
        {"name":"Rushing River","skill_check":"agility","difficulty":1.1 },
        {"name":"Ancient Riddle","skill_check":"intelligence","difficulty":1.3 },
        {"name":"Heavy Boulder","skill_check":"strength","difficulty":1.4 },
        {"name":"Suspicious Stranger","skill_check":"charisma","difficulty":1.0 }
        ]
    def clear_screen (self ):
        os .system ('cls'if os .name =='nt'else 'clear')
    def play (self ,pet_species =None ,pet_stats =None ,adventure_luck =0.0 ,xp_boost =0.0 ):
        if not pet_stats :
            pet_stats ={"strength":10.0 ,"intelligence":10.0 ,"agility":10.0 ,"charisma":10.0 }
        self .clear_screen ()
        print ("=== Pet Adventure ===")
        print ("Take your pet on an exciting adventure to find treasures!")
        print ("Your pet will face challenges that test their abilities.")
        if pet_species :
            print (f"Hint: {pet_species } may prefer certain locations!")
        print ("\nAvailable adventure locations:")
        for i ,location in enumerate (self .adventure_locations ):
            print (f"{i +1 }. {location ['name']}")
        try :
            choice =int (input ("\nChoose a location (1-5): "))-1 
            if 0 <=choice <len (self .adventure_locations ):
                selected_location =self .adventure_locations [choice ]
                print (f"\nYou selected {selected_location ['name']}!")
                preference_bonus =0.0 
                if pet_species and pet_species in selected_location .get ("preferred_by",[]):
                    preference_bonus =0.2 
                    print (f"Your {pet_species } feels right at home in this location! +0.2 bonus")
                success_level ,found_treasure ,coins_earned =self ._run_adventure (selected_location ,pet_stats ,adventure_luck )
                success_level +=preference_bonus 
                print (f"\nAdventure success level: {success_level :.1f}")
                return success_level ,found_treasure ,coins_earned ,xp_boost 
            else :
                print ("Invalid choice. Using default location.")
                return 0.5 ,None ,0 ,xp_boost 
        except ValueError :
            print ("Invalid input. Using default location.")
            return 0.5 ,None ,0 ,xp_boost 
    def _run_adventure (self ,location ,pet_stats ,adventure_luck =0.0 ):
        print (f"\nYour pet begins exploring the {location ['name']}...")
        time .sleep (1.5 )
        num_obstacles =random .randint (2 ,3 )
        adventure_obstacles =random .sample (self .obstacles ,num_obstacles )
        total_success =0.0 
        for i ,obstacle in enumerate (adventure_obstacles ):
            print (f"\nObstacle {i +1 }: Your pet encounters a {obstacle ['name']}!")
            skill_check =obstacle ['skill_check']
            print (f"This requires {skill_check .capitalize ()} to overcome.")
            print (f"Your pet's {skill_check .capitalize ()}: {pet_stats [skill_check ]:.1f}")
            stat_value =pet_stats [skill_check ]
            base_chance =stat_value /(stat_value +(obstacle ['difficulty']*50 ))
            print ("\nQuick! Help your pet overcome this obstacle! Press Enter at the right moment...")
            time .sleep (random .uniform (1.0 ,2.5 ))
            start_time =time .time ()
            print ("NOW!")
            input ()
            reaction_time =time .time ()-start_time 
            if reaction_time <0.5 :
                timing_bonus =0.3 
                print ("Perfect timing! Your pet moves with incredible precision!")
            elif reaction_time <1.0 :
                timing_bonus =0.2 
                print ("Good timing! Your pet handles the situation well.")
            elif reaction_time <1.5 :
                timing_bonus =0.1 
                print ("Decent timing. Your pet manages adequately.")
            else :
                timing_bonus =0.0 
                print ("Your pet struggles with the timing.")
            obstacle_success =base_chance +timing_bonus 
            if obstacle_success >=0.6 :
                print (f"Success! Your pet overcomes the {obstacle ['name']}!")
                total_success +=1.0 
            elif obstacle_success >=0.3 :
                print (f"Partial success. Your pet struggles but manages to get past the {obstacle ['name']}.")
                total_success +=0.5 
            else :
                print (f"Your pet couldn't overcome the {obstacle ['name']} and had to find another way.")
            time .sleep (1.5 )
        adventure_success =total_success /num_obstacles 
        adventure_success =adventure_success /location ['difficulty']
        found_treasure =None 
        if random .random ()<adventure_luck or adventure_success >=0.7 :
            if adventure_success >0.9 and random .random ()<0.3 :
                treasure_pool =[t for t in self .treasures if t ['rarity']=='rare']
            elif adventure_success >0.7 and random .random ()<0.6 :
                treasure_pool =[t for t in self .treasures if t ['rarity']=='uncommon']
            else :
                treasure_pool =[t for t in self .treasures if t ['rarity']=='common']
            found_treasure =random .choice (treasure_pool )
            print (f"\nYour pet found a treasure: {found_treasure ['name']}!")
            print ("This will boost your pet's stats:")
            for stat ,boost in found_treasure ['stat_boost'].items ():
                print (f"  {stat .capitalize ()}: +{boost }")
        else :
            print ("\nYour pet didn't find any treasures this time, but gained valuable experience!")
        coins_earned =int (adventure_success *20 )+(len (adventure_obstacles )*5 )
        if found_treasure :
            coins_earned +=25 
        print (f"\nYour pet earned {coins_earned } PetCoins from the adventure!")
        return min (1.5 ,adventure_success ),found_treasure ,coins_earned 