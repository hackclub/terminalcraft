import time
import sys
import random
import subprocess
import os

# Initial score
score = 0
# List of possible weapons
random_weapon = []
def mission_succeed():
    print("You returned back to the historia again")
    time.sleep(2)
    print("Unknown: You have succeed in the mission, Andrew!")
    time.sleep(2)
    print("Suddenly, there is a box started to appear on the surface")
    time.sleep(2)

def bussiness_towers_bomb():
    print("Do you see this citizen plane?")
    time.sleep(1)
    print("Andrew: Oh my god! I think he will do it!")
    time.sleep(2)
    print("The plane is going towards the two towers")
    time.sleep(2)
    print("Ran Away andrew!!!")
    time.sleep(1)
    print("booom! (The plane has crashed into the towers)")
    print("Your mission failed andrew!")
    print("---------------------------------------------")
    time.sleep(2)
    print("You are forced to the historia again!")
    time.sleep(2)
    print("The historia box turned red color and the unknown voice said:")
    time.sleep(2)
    print("Unknown: Are you Idiot Andrew?, You were going to do a special mission and you failed in it.")
    start_again = input("start again?? (y/n)")
    if start_again == "y":
        os.system('cls' if os.name == 'nt' else 'clear')
        instructions()
    elif start_again == "n":
        sys.exit()





def chyrnobel_mission():
    print("============ Chyrnobel Mission! ============")
    time.sleep(2)
    print("You chose to enter the chyrnobel mission portal.....Goodluck")
    time.sleep(2)
    print("-----------------------------------------------------")
    time.sleep(2)
    print("You found yourself in chyrnobel powerstation before the disaster bi 1hour only!!")
    time.sleep(2)
    print("You must to stop them frommaking the simulation in the station 4")
    time.sleep(2)
    enter_chyrnobel = input("choose 1 to enter the station or choose 2 to go away")
    if enter_chyrnobel == "1":
        print("You entered the 4th station in chyrnobel")
        time.sleep(2)
        print("you saw the workers in the station trying to operate the station and start the simulation")
        time.sleep(2)
        alert_workers = input("choose 1 to alert them to do not start or choose 2 to neglict them")
        if alert_workers == "1":
            print("The head worker: You are honest man! ,You have succeed in saving the chyrnobel station number 4")
            time.sleep(2)
            print("The head of the workers rewarded you and gave you a special remote and told you to hide it away because there is an unknown man try to reach it")
            time.sleep(2)
            print("Will you hide it?")
            time.sleep(2)
            hide_remote = input("Enter 1 to hide the remote inside your bag or enter 2 to save it in your hand")
            global saved_remote
            saved_remote = ""
            if hide_remote == "1":
                print("The remote is now more safe")
            elif hide_remote == "2":
                print("Ok, no problem. Take care of it")
            else:
                hide_remote = input("Enter 1 to hide the remote inside your bag or enter 2 to save it in your hand")
            def first_fight():
                print("One of the workers saw you and thought that you are a soviet spy")
                time.sleep(2)
                print("He started running behined you!")
                time.sleep(2)
                fight_the_man = input("Enter 1 to fight the man or enter 2 to run away")
                if fight_the_man == "1":
                    print("You decided to fight this worker!")
                    time.sleep(2)
                    print("You killed the worker!")
                elif fight_the_man == "2":
                    print("You decided to run away")
                    print("you returned to historia again!")
            def first_return():
                if hide_remote == "1":
                    print("The remote is now more safe")
                elif hide_remote == "2":
                    print("Ok, no problem. Take care of it")
            mission_succeed()
            time.sleep(2)
            print("Unknown: Put the remote in the box please, Andrew!")
            if hide_remote == "1":
                put_remote = input("please choose 1 to put the remote in the chest or 2 to keep it in your hand")
                if put_remote == "1":
                    print("the remote was saved")
                    print("Mission succeed!")
                    saved_remote = "saved"
                elif put_remote == "2":
                    print("the remote was kept in your hand")
                    saved_remote = "notsaved"
                    Enter_Second_Portal = input("Enter 1 to jump into the portal or enter 2 to stay in the historia")
            elif hide_remote == "2":
                print("You searched for the remote in your bag, but you didn't find it")
                time.sleep(1)
                print("Historia started shooting you and then the second portal opened")
                Enter_Second_Portal = input("Enter 1 to jump into the portal or enter 2 to stay in the historia")
                if Enter_Second_Portal == "1":
                    september_11_attack()
                else:
                    print("invalid input!")
                    Enter_Second_Portal = input("Enter 1 to jump into the portal or enter 2 to stay in the historia")
        elif alert_workers == "2":
            print("booom! (The 4th station was destroyed)")
            time.sleep(2)
            print("You fainted!")
            print("Your mission failed andrew!")
            print("---------------------------------------------")
            time.sleep(2)
            print("You are forced to the historia again!")
            time.sleep(2)
            print("The historia box turned red color and the unknown voice said:")
            time.sleep(2)
            print("Unknown: Are you Idiot Andrew?, You were going to do a special mission and you failed in it.")
            start_again = input("start again?? (y/n)")
            if start_again == "y":
                os.system('cls' if os.name == 'nt' else 'clear')
                instructions()
            elif start_again == "n":
                sys.exit()
            else:
                print("invalid input")
                start_again = input("start again?? (y/n)")

        else:
            print("invalid input")
            alert_workers = input("choose 1 to alert them to do not start or choose 2 to neglict them")
            

            

    elif enter_chyrnobel == "2":
        #going_away()
        print("you decided to go away")
        time.sleep(2)
        print("---------------------------------------------")
        time.sleep(2)
        print("You are forced to the historia again!")
        time.sleep(2)
        print("The historia box turned red color and the unknown voice said:")
        time.sleep(2)
        print("Unknown: Are you Idiot Andrew?, You were going to do a special mission and you failed in it.")
        start_again = input("start again?? (y/n)")
        if start_again == "y":
            os.system('cls' if os.name == 'nt' else 'clear')
            instructions()
        elif start_again == "n":
            sys.exit()


def september_11_attack():
    print("You jumped into the second portal and the second mission started!")
    time.sleep(2)
    print("""
        ---------------------------------------------------------
             ============September 11th attacks============
    """)
    time.sleep(2)
    print("You reached the 2 bussiness towers before the attack")
    time.sleep(2)
    print("You saw a shadow of a man with the remote moving inside a building")
    run_towards_the_man = input("Enter 1 to run behined the man or enter 2 to neglict him and buy an icecream")
    if run_towards_the_man == "1":
        print("You decided to run behined the unknown man")
        time.sleep(2)
        print("You ran behined him until reached a stalemate")
        time.sleep(2)
        fight_man = input("enter1 to fight the man or enter 2 to call the cops")
        if fight_man == "1":
            print("You decided to fight the man!")
            time.sleep(2)
            print("You killed the man and got the remote back again!")
        elif fight_man == "2":
            print("You decided to call the cops!")
            time.sleep(2)
            print("Watch out! this man ran away with the remote!")
            time.sleep(2)
            print("You started running after him!")
            time.sleep(2)
            print("Oh shit! he reached the bussiness towers")

            





def instructions():
    print("Unknown: Before you start your mission, you must learn the game instructions")
    time.sleep(2)
    print("Andrew: Sure, please tell me!")
    time.sleep(2)
    print("Unknown: sure! As I said, You are stuck here and you must do some different missions to get out of here!")
    time.sleep(2)
    print("Suddenly, some portals were opened in the box")
    time.sleep(2)
    print("You have 2 main portals each one has a mission to be completed")
    time.sleep(2)
    print("Unknown: You should enter one portal, Andrew!")
    portal_choice = input("Please choose 1 portal from 1 to 2")
    if portal_choice == "1":
        os.system('cls' if os.name == 'nt' else 'clear')
        chyrnobel_mission()
    elif portal_choice == "2":
        september_11_attack()
    else: 
        print("not work")







def chyrnobel():
    saved_remote = ""
    if saved_remote == "saved":
        print("Mission has been completed!")
        instructions()
    elif saved_remote == "notsaved":
        chyrnobel_mission()

chyrnobel()


#start function
def start():
    """
    Function to start the game and present the initial choices to the player.
    """
    global score
    print("""            ===============================    Welcome To......  ===============================
             ==============================       Historia  v.1.0   ==============================
             =============================                      =============================
                                  The unknown place.......shouting out!
    """)
    list_of_numbers = [10, 20, 25, 85, 99]
    time.sleep(2)
    list_count = len(list_of_numbers)
    for i in range(list_count):
        print("loading " +  str(list_of_numbers[i]) + "%")
        time.sleep(1)
        
    time.sleep(5)
    choice = input("Please enter 1 to start the main game or 2 to return to the start menu: ")
    while choice != "1" and choice != "2":
        choice = input("Invalid input. Please enter 1 or 2: ")
    if choice == "1":
        print("The game started.......NOW!")
        time.sleep(3)
        print("In a lightless place, faraway, with no sound but deafening silence. Andrew the Orion is an adventurer lying on a strange floor in this strange dark place.")
        time.sleep(3)
        print("After a few seconds of starting the scene, Andrew woke up because he heard a creeking sound from outside and he was shocked.")
        time.sleep(3)
        print(" He found himself in a massive black box, while he was shocked and trying to get out of this place.")
        time.sleep(3)
        print("Andrew: where am I, and what is this damn place??")
        time.sleep(3)
        print(" he heard to a deep voice came from an unknown place")
        time.sleep(3)
        print("“Unknown: Welcome,  Andrew. You are stuck here until you do what I order you, Are you ready…?”.")
        time.sleep(1)
        start_game_res = input("please enter (y/n)").lower()
        if start_game_res == "y":
            instructions()
        elif start_game_res == "n":
            print("You decided not to play...Exiting game in query...")
            start_again = input("start again?? (y/n)")
            if start_again == "y":
                os.system('cls' if os.name == 'nt' else 'clear')
                instructions()
            elif start_again == "n":
                sys.exit()
        else:
            start_game_res = input("please enter (y/n)").lower()

    else:
        print("You decided not to play...Exiting game in query...")
        start_again = input("start again?? (y/n)")
        if start_again == "y":
            os.system('cls' if os.name == 'nt' else 'clear')
            instructions()
        elif start_again == "n":
            sys.exit()

start()