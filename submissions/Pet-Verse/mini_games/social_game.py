import random 
import os 
import time 
class SocialGame :
    def __init__ (self ):
        self .social_scenarios =[
        {"name":"Pet Playdate","difficulty":0.8 ,"preferred_by":["Fluffball","Leafling"]},
        {"name":"Community Event","difficulty":1.0 ,"preferred_by":["Aqualing","Emberspark"]},
        {"name":"Training Class","difficulty":1.2 ,"preferred_by":["Stoneshell","Emberspark"]},
        {"name":"Pet Show","difficulty":1.5 ,"preferred_by":["Fluffball","Aqualing"]}
        ]
        self .conversation_options =[
        {"prompt":"Another pet approaches yours. What do you do?",
        "options":["Encourage friendly greeting","Keep distance","Let your pet decide","Show off a trick"],
        "best":0 },
        {"prompt":"Your pet seems nervous in the social setting. How do you help?",
        "options":["Remove them immediately","Offer treats as distraction","Provide gentle encouragement","Ignore the behavior"],
        "best":2 },
        {"prompt":"Another pet owner wants to know about your pet. How do you respond?",
        "options":["Give minimal information","Share enthusiastically","Ask about their pet first","Walk away"],
        "best":2 }
        ]
    def clear_screen (self ):
        os .system ('cls'if os .name =='nt'else 'clear')
    def play (self ,pet_species =None ,charisma_boost =1.0 ,xp_boost =0.0 ):
        self .clear_screen ()
        print ("=== Pet Socialization Game ===")
        print ("Help your pet develop social skills!")
        print ("Choose a social scenario for your pet.")
        if pet_species :
            print (f"Hint: {pet_species } may prefer certain social settings!")
        print ("\nAvailable social scenarios:")
        for i ,scenario in enumerate (self .social_scenarios ):
            print (f"{i +1 }. {scenario ['name']}")
        try :
            choice =int (input ("\nChoose a scenario (1-4): "))-1 
            if 0 <=choice <len (self .social_scenarios ):
                selected_scenario =self .social_scenarios [choice ]
                print (f"\nYou selected {selected_scenario ['name']}!")
                preference_bonus =0.0 
                if pet_species and pet_species in selected_scenario .get ("preferred_by",[]):
                    preference_bonus =0.2 
                    print (f"Your pet seems particularly comfortable in this setting! +0.2 bonus")
                success_level =self ._run_social_game (selected_scenario )*charisma_boost 
                success_level +=preference_bonus 
                print (f"\nSocialization success level: {success_level :.1f}")
                return success_level ,xp_boost 
            else :
                print ("Invalid choice. Using default scenario.")
                return 0.5 
        except ValueError :
            print ("Invalid input. Using default scenario.")
            return 0.5 
    def _run_social_game (self ,scenario ):
        conversation =random .choice (self .conversation_options )
        print (f"\n{conversation ['prompt']}")
        for i ,option in enumerate (conversation ['options']):
            print (f"{i +1 }. {option }")
        try :
            answer =int (input ("\nYour choice (1-4): "))-1 
            if answer ==conversation ['best']:
                print ("Great choice! Your pet is responding well.")
                base_success =1.0 
            elif abs (answer -conversation ['best'])==1 :
                print ("That works reasonably well.")
                base_success =0.7 
            else :
                print ("Your pet seems uncomfortable with that approach.")
                base_success =0.4 
            print ("\nQuick! Your pet is looking to you for guidance. Press Enter at the right moment...")
            time .sleep (random .uniform (1.5 ,3.0 ))
            start_time =time .time ()
            input ()
            reaction_time =time .time ()-start_time 
            if reaction_time <0.8 :
                timing_bonus =0.5 
                print ("Perfect timing! You responded to your pet's social cues perfectly!")
            elif reaction_time <1.5 :
                timing_bonus =0.3 
                print ("Good timing! Your pet appreciates your guidance.")
            elif reaction_time <2.5 :
                timing_bonus =0.1 
                print ("Your pet was looking for quicker guidance.")
            else :
                timing_bonus =0.0 
                print ("You missed your pet's social cues.")
            success_level =(base_success +timing_bonus )/scenario ['difficulty']
            return min (1.5 ,success_level )
        except ValueError :
            print ("Invalid input.")
            return 0.5 
        except KeyboardInterrupt :
            print ("\nSocialization cancelled.")
            return 0.3 