import random 
import time 
import os 
class FeedingGame :
    def __init__ (self ):
        self .foods =[
        {"name":"Apple","nutrition":1.0 ,"preferred_by":["Fluffball","Leafling"]},
        {"name":"Carrot","nutrition":0.8 ,"preferred_by":["Fluffball","Leafling"]},
        {"name":"Steak","nutrition":1.5 ,"preferred_by":["Emberspark","Stoneshell"]},
        {"name":"Fish","nutrition":1.2 ,"preferred_by":["Aqualing"]},
        {"name":"Cake","nutrition":0.5 ,"preferred_by":[]},
        {"name":"Berries","nutrition":0.9 ,"preferred_by":["Leafling"]},
        {"name":"Crystals","nutrition":1.3 ,"preferred_by":["Stoneshell"]},
        {"name":"Ember Fruit","nutrition":1.4 ,"preferred_by":["Emberspark"]},
        {"name":"Seaweed","nutrition":1.1 ,"preferred_by":["Aqualing"]}
        ]
    def clear_screen (self ):
        os .system ('cls'if os .name =='nt'else 'clear')
    def play (self ,pet_species =None ):
        self .clear_screen ()
        print ("=== Feeding Game ===")
        print ("Choose the right food for your pet!")
        print ("The healthier the food, the more nutrition your pet gets.")
        if pet_species :
            print (f"Hint: {pet_species } has specific food preferences!")
        random .shuffle (self .foods )
        options =self .foods [:3 ]
        print ("\nAvailable foods:")
        for i ,food in enumerate (options ):
            print (f"{i +1 }. {food ['name']}")
        try :
            choice =int (input ("\nChoose a food (1-3): "))-1 
            if 0 <=choice <len (options ):
                selected_food =options [choice ]
                print (f"\nYou selected {selected_food ['name']}!")
                preference_bonus =0.0 
                if pet_species and pet_species in selected_food .get ("preferred_by",[]):
                    preference_bonus =0.3 
                    print (f"Your pet loves {selected_food ['name']}! +0.3 bonus")
                print ("\nQuick! Press Enter when you see 'NOW!'...")
                time .sleep (random .uniform (1.0 ,3.0 ))
                print ("NOW!")
                start_time =time .time ()
                input ()
                reaction_time =time .time ()-start_time 
                if reaction_time <0.5 :
                    reaction_bonus =0.5 
                    print ("Perfect timing!")
                elif reaction_time <1.0 :
                    reaction_bonus =0.3 
                    print ("Good timing!")
                elif reaction_time <2.0 :
                    reaction_bonus =0.1 
                    print ("Okay timing.")
                else :
                    reaction_bonus =0.0 
                    print ("Too slow!")
                success_level =selected_food ["nutrition"]+reaction_bonus +preference_bonus 
                print (f"\nFeeding success level: {success_level :.1f}")
                return success_level 
            else :
                print ("Invalid choice. Using default food.")
                return 0.5 
        except ValueError :
            print ("Invalid input. Using default food.")
            return 0.5 
        except KeyboardInterrupt :
            print ("\nFeeding cancelled.")
            return 0.3 