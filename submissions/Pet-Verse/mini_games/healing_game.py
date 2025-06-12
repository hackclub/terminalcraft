import random 
import os 
import time 
class HealingGame :
    def __init__ (self ):
        self .treatments =[
        {"name":"Herbal Remedy","best_for":["Leafling","Fluffball"],"difficulty":0.9 },
        {"name":"Warm Compress","best_for":["Emberspark","Stoneshell"],"difficulty":0.8 },
        {"name":"Cool Bath","best_for":["Aqualing","Emberspark"],"difficulty":1.0 },
        {"name":"Rest & Nutrition","best_for":["Stoneshell","Fluffball"],"difficulty":0.7 }
        ]
        self .symptoms =[
        "fever","lethargy","loss of appetite","sneezing","coughing","rash"
        ]
        self .healing_questions =[
        {
        "question":"What's most important when your pet is sick?",
        "options":["Immediate treatment","Careful observation first","Asking other pet owners","Ignoring minor symptoms"],
        "correct":1 
        },
        {
        "question":"How often should you check on a sick pet?",
        "options":["Once a day","Every few hours","Constantly","Only when giving medicine"],
        "correct":1 
        },
        {
        "question":"What should you monitor during illness?",
        "options":["Just temperature","Only eating habits","Multiple symptoms and behaviors","Just energy levels"],
        "correct":2 
        }
        ]
    def clear_screen (self ):
        os .system ('cls'if os .name =='nt'else 'clear')
    def play (self ,pet_species =None ):
        self .clear_screen ()
        print ("=== Pet Healing Game ===")
        print ("Your pet isn't feeling well! Help them recover.")
        print ("Choose a treatment approach for your pet.")
        if pet_species :
            print (f"Hint: {pet_species } may respond better to certain treatments!")
        pet_symptoms =random .sample (self .symptoms ,2 )
        print (f"\nYour pet is showing symptoms of: {pet_symptoms [0 ]} and {pet_symptoms [1 ]}")
        print ("\nAvailable treatments:")
        for i ,treatment in enumerate (self .treatments ):
            print (f"{i +1 }. {treatment ['name']}")
        try :
            choice =int (input ("\nChoose a treatment (1-4): "))-1 
            if 0 <=choice <len (self .treatments ):
                selected_treatment =self .treatments [choice ]
                print (f"\nYou selected {selected_treatment ['name']}!")
                preference_bonus =0.0 
                if pet_species and pet_species in selected_treatment .get ("best_for",[]):
                    preference_bonus =0.2 
                    print (f"Your {pet_species } responds well to this treatment! +0.2 bonus")
                success_level =self ._run_healing_game (selected_treatment )
                success_level +=preference_bonus 
                print (f"\nHealing success level: {success_level :.1f}")
                return success_level 
            else :
                print ("Invalid choice. Using default treatment.")
                return 0.5 
        except ValueError :
            print ("Invalid input. Using default treatment.")
            return 0.5 
    def _run_healing_game (self ,treatment ):
        question_data =random .choice (self .healing_questions )
        print (f"\n{question_data ['question']}")
        for i ,option in enumerate (question_data ['options']):
            print (f"{i +1 }. {option }")
        try :
            answer =int (input ("\nYour answer (1-4): "))-1 
            if answer ==question_data ['correct']:
                print ("That's right! You know how to care for your pet.")
                knowledge_score =1.0 
            elif abs (answer -question_data ['correct'])==1 :
                print ("Not bad, but there's a better approach.")
                knowledge_score =0.6 
            else :
                print (f"Actually, {question_data ['options'][question_data ['correct']]} is the best approach.")
                knowledge_score =0.3 
            print ("\nTime to apply the treatment! You need to maintain a steady rhythm.")
            print ("Press Enter each time you see 'Apply treatment now!'")
            application_score =0 
            for i in range (3 ):
                time .sleep (random .uniform (1.0 ,3.0 ))
                start_time =time .time ()
                print ("Apply treatment now!")
                input ()
                reaction_time =time .time ()-start_time 
                if reaction_time <0.7 :
                    print ("Perfect application!")
                    application_score +=1.0 
                elif reaction_time <1.2 :
                    print ("Good application.")
                    application_score +=0.7 
                elif reaction_time <2.0 :
                    print ("Adequate application.")
                    application_score +=0.4 
                else :
                    print ("Your timing was off.")
                    application_score +=0.2 
                time .sleep (0.5 )
            avg_application =application_score /3 
            success_level =(knowledge_score *0.4 +avg_application *0.6 )/treatment ['difficulty']
            if success_level >0.8 :
                print ("\nYour pet is recovering quickly! Great job!")
            elif success_level >0.5 :
                print ("\nYour pet is showing signs of improvement.")
            else :
                print ("\nYour pet's recovery might take a bit longer.")
            return min (1.5 ,success_level )
        except ValueError :
            print ("Invalid input.")
            return 0.5 
        except KeyboardInterrupt :
            print ("\nTreatment cancelled.")
            return 0.3 