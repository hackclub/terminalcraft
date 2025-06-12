import random 
import os 
import time 
class GroomingGame :
    def __init__ (self ):
        self .grooming_tools =[
        {"name":"Brush","best_for":["Fluffball","Leafling"],"difficulty":0.8 },
        {"name":"Comb","best_for":["Emberspark","Fluffball"],"difficulty":0.9 },
        {"name":"Sponge","best_for":["Aqualing","Stoneshell"],"difficulty":1.0 },
        {"name":"Specialty Cleaner","best_for":["Stoneshell","Emberspark"],"difficulty":1.2 }
        ]
        self .grooming_areas =[
        "head","back","left side","right side","belly","tail"
        ]
    def clear_screen (self ):
        os .system ('cls'if os .name =='nt'else 'clear')
    def play (self ,pet_species =None ):
        self .clear_screen ()
        print ("=== Pet Grooming Game ===")
        print ("Keep your pet clean and happy with proper grooming!")
        print ("Choose a grooming tool for your pet.")
        if pet_species :
            print (f"Hint: {pet_species } may prefer certain grooming tools!")
        print ("\nAvailable grooming tools:")
        for i ,tool in enumerate (self .grooming_tools ):
            print (f"{i +1 }. {tool ['name']}")
        try :
            choice =int (input ("\nChoose a grooming tool (1-4): "))-1 
            if 0 <=choice <len (self .grooming_tools ):
                selected_tool =self .grooming_tools [choice ]
                print (f"\nYou selected the {selected_tool ['name']}!")
                preference_bonus =0.0 
                if pet_species and pet_species in selected_tool .get ("best_for",[]):
                    preference_bonus =0.2 
                    print (f"Your {pet_species } loves this grooming tool! +0.2 bonus")
                success_level =self ._run_grooming_game (selected_tool )
                success_level +=preference_bonus 
                print (f"\nGrooming success level: {success_level :.1f}")
                return success_level 
            else :
                print ("Invalid choice. Using default tool.")
                return 0.5 
        except ValueError :
            print ("Invalid input. Using default tool.")
            return 0.5 
    def _run_grooming_game (self ,tool ):
        print ("\nTime to groom your pet! Follow the instructions carefully.")
        print ("When prompted, groom the specified area by pressing Enter.")
        print ("Try to maintain a steady grooming rhythm for best results!")
        input ("\nPress Enter to begin grooming...")
        total_score =0 
        for i in range (4 ):
            area =random .choice (self .grooming_areas )
            print (f"\nGroom your pet's {area } now!")
            optimal_time =random .uniform (0.8 ,2.0 )
            time .sleep (optimal_time )
            sweet_spot_start =time .time ()
            print ("NOW! (Press Enter)")
            try :
                input ()
                reaction_time =time .time ()-sweet_spot_start 
                if reaction_time <0.5 :
                    print ("Perfect grooming technique!")
                    action_score =1.0 
                elif reaction_time <1.0 :
                    print ("Good grooming!")
                    action_score =0.7 
                elif reaction_time <1.5 :
                    print ("Adequate grooming.")
                    action_score =0.4 
                else :
                    print ("Your pet is getting impatient...")
                    action_score =0.2 
                total_score +=action_score 
            except KeyboardInterrupt :
                print ("\nGrooming cancelled.")
                return 0.3 
        avg_score =total_score /4 
        final_score =avg_score /tool ['difficulty']
        if final_score >0.8 :
            print ("\nYour pet looks amazing! They're so clean and happy!")
        elif final_score >0.5 :
            print ("\nYour pet is clean and content with the grooming session.")
        else :
            print ("\nYour pet is cleaner, but the grooming could have gone better.")
        return min (1.5 ,final_score )