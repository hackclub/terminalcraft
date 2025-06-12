import random 
import time 
import os 
class TrainingGame :
    def __init__ (self ):
        self .training_types =[
        {"name":"Strength Training","stat":"strength","difficulty":1.0 ,"preferred_by":["Emberspark","Stoneshell"]},
        {"name":"Intelligence Puzzle","stat":"intelligence","difficulty":1.2 ,"preferred_by":["Aqualing","Leafling"]},
        {"name":"Agility Course","stat":"agility","difficulty":0.9 ,"preferred_by":["Fluffball","Aqualing"]},
        {"name":"Social Exercise","stat":"charisma","difficulty":0.8 ,"preferred_by":["Fluffball","Leafling"]}
        ]
    def clear_screen (self ):
        os .system ('cls'if os .name =='nt'else 'clear')
    def play (self ,pet_species =None ,training_boost =1.0 ,xp_boost =0.0 ):
        self .clear_screen ()
        print ("=== Training Game ===")
        print ("Choose a training exercise for your pet!")
        print ("Different exercises improve different stats.")
        if pet_species :
            print (f"Hint: {pet_species } has specific training preferences!")
        print ("\nAvailable training exercises:")
        for i ,training in enumerate (self .training_types ):
            print (f"{i +1 }. {training ['name']} (improves {training ['stat']})")
        try :
            choice =int (input ("\nChoose a training exercise (1-4): "))-1 
            if 0 <=choice <len (self .training_types ):
                selected_training =self .training_types [choice ]
                print (f"\nYou selected {selected_training ['name']}!")
                preference_bonus =0.0 
                if pet_species and pet_species in selected_training .get ("preferred_by",[]):
                    preference_bonus =0.2 
                    print (f"Your pet excels at this type of training! +0.2 bonus")
                success_level =self ._run_quiz_game (selected_training )*training_boost 
                success_level +=preference_bonus 
                print (f"\nTraining success level: {success_level :.1f}")
                return success_level ,xp_boost 
            else :
                print ("Invalid choice. Using default training.")
                return 0.5 
        except ValueError :
            print ("Invalid input. Using default training.")
            return 0.5 
    def _run_quiz_game (self ,training ):
        questions =[
        {
        "question":"What's the best way to approach this training?",
        "options":["With patience","With force","With treats","With no breaks"],
        "correct":0 
        },
        {
        "question":"How often should you train your pet?",
        "options":["Once a year","Every few days","24/7","When they misbehave"],
        "correct":1 
        },
        {
        "question":"What's most important during training?",
        "options":["Pushing to exhaustion","Consistency","Punishment","Competition"],
        "correct":1 
        }
        ]
        question_data =random .choice (questions )
        print (f"\n{question_data ['question']}")
        for i ,option in enumerate (question_data ['options']):
            print (f"{i +1 }. {option }")
        try :
            answer =int (input ("\nYour answer (1-4): "))-1 
            if answer ==question_data ['correct']:
                print ("Correct! Great training technique!")
                base_success =1.0 
            else :
                print (f"Not quite right. The best approach was: {question_data ['options'][question_data ['correct']]}")
                base_success =0.5 
            print ("\nQuick! Press Enter when your pet performs the trick...")
            time .sleep (random .uniform (1.5 ,3.0 ))
            start_time =time .time ()
            input ()
            reaction_time =time .time ()-start_time 
            if reaction_time <0.7 :
                reaction_bonus =0.5 
                print ("Perfect timing!")
            elif reaction_time <1.2 :
                reaction_bonus =0.3 
                print ("Good timing!")
            elif reaction_time <2.0 :
                reaction_bonus =0.1 
                print ("Okay timing.")
            else :
                reaction_bonus =0.0 
                print ("Too slow! Your pet got distracted.")
            success_level =(base_success +reaction_bonus )/training ['difficulty']
            return min (1.5 ,success_level )
        except ValueError :
            print ("Invalid input.")
            return 0.5 
        except KeyboardInterrupt :
            print ("\nTraining cancelled.")
            return 0.3 