import random
import time
import os
import threading
from threading import Timer

jeffreyStay = False

jeffreyIntro = ["jeffrey the destroyer                    ", "jeffrey the destroyer -                  ", "jeffrey the destroyer --                ", "jeffrey the destroyer ---               ", "jeffrey the destroyer --->              ", "jeffrey the destroyer ---> ₍ᐢ._.ᐢ₎♡          ","jeffrey the destroyer ---> ₍ᐢ._.ᐢ₎♡           ", "jeffrey the destroyer --->              ", "jeffrey the destroyer --                ", "jeffrey the destroyer                   ", "jeffrey the destroyer has               ", "jeffrey the destroyer has challenged    ", "jeffrey the destroyer has challenged you"]

characterOne = ["\033[5;1H (*ᴗ͈ˬᴗ͈)ꕤ*.ﾟ\n /    \\ \n _| |_", "\033[5;1H(*ᴗ͈ˬᴗ͈)ꕤ*.ﾟ \n/    \\ \n_/  \\_"]
characterTwo = [ "\033[5;1H (•́ ⍜ •̀)｡𖦹°⭒\n /     \\ \n  _| |_", "\033[5;1H(•́ ⍜ •̀)⋆｡𖦹°⭒ \n/     \\ \n _/  \\_"]
characterThree = [ "\033[5;1H (¬_¬”)\n /    \\ \n _| |_", "\033[5;1H(¬_¬”)\n/    \\ \n_/  \\_"]
jeffrey = ["\033[7;20H₍ᐢ._.ᐢ₎", "\033[6;20H₍ᐢ._.ᐢ₎♡\n\033[7;20H |   |  "]
jeffreyHit = ["\033[6;18H♡ ₍ᐢ._.ᐢ₎♡\n\033[7;1H _| |_\033[7;20H |   |  ", "\033[6;15H♡    ₍ᐢ._.ᐢ₎♡\n\033[7;1H _| |_\033[7;20H |   |  ","\033[6;12H♡       ₍ᐢ._.ᐢ₎♡\n\033[7;1H _| |_\033[7;20H |   |  "]
attackOne = ["\033[5;1H (*ᴗ͈ˬᴗ͈) ꕤ*.ﾟ\n /    \\ \n _| |_","\033[5;1H (*ᴗ͈ˬᴗ͈)   ꕤ*.ﾟ\n /    \\ \n _| |_", "\033[5;1H (*ᴗ͈ˬᴗ͈)     ꕤ*.ﾟ\n /    \\ \n _| |_", "\033[5;1H (*ᴗ͈ˬᴗ͈)       ꕤ*.ﾟ\n /    \\ \n _| |_", "\033[5;1H (*ᴗ͈ˬᴗ͈)\n /    \\ \n _| |_ "]
attackTwo = ["\033[5;1H (•́ ⍜ •̀)｡𖦹°⭒\n /     \\ \n  _| |_  ", "\033[5;1H (•́ ⍜ •̀)  ｡𖦹°⭒\n /     \\ \n  _| |_", "\033[5;1H (•́ ⍜ •̀)    ｡𖦹°⭒\n /     \\ \n  _| |_", "\033[5;1H (•́ ⍜ •̀)       ｡𖦹°⭒\n /     \\ \n  _| |_"]
attackThree = ["\033[5;1H (¬_¬”)✪ ✪ ✪\n /    \\ \n _| |_", " (¬_¬”)   ✪ ✪ ✪\n /    \\ \n _| |_", " (¬_¬”)      ✪ ✪ ✪\n /    \\ \n _| |_", " (¬_¬”)        ✪ ✪ ✪\n /    \\ \n _| |_"]
defending = ["\033[5;1H (*ᴗ͈ˬᴗ͈)\n /    --) \n _| |_","\033[5;1H (•́ ⍜ •̀)\n /     --) \n  _| |_  ","\033[5;1H (¬_¬”)\n /    --) \n _| |_"]
AttackedFace = ["\033[5;1H(˶°ㅁ°) !!\n/    \\ \n _| |_","\033[5;1H (˘ŏ_ŏ)\n /     \\ \n  _| |_", "\033[5;1H(⊙ ⍜ ⊙)\n /    \\ \n    _| |_"]
healBinary = ["0011", "1010", "11001", "111000", "10111", "11110", "1101", "010101", "100011", "111101", "011110", "1010011", "00011101", "1101100"]  
healAnswers = ["3", "10", "25", "56", "23", "30", "13", "21", "35", "61", "30", "83", "29", "108"] 
whichBinary = 0
healInterval = 0
hp = 8
enemy = 8
hps = ["hp: --------", "hp: ------- ", "hp: ------  ", "hp: -----   ", "hp: ----    ", "hp: ---     ", "hp: --      ", "hp: -       ", "hp: !!"]
hpShown = abs(hp - 8)
start = False
characterPicked = False
charFrames = 0
animationPlaying = True
defendStreak = 0



def clearScreen():
    os.system('clear')

    
def animate(frames, delay=0.7):
    jeffreyFrame = 0
    for i in range(len(frames)):
        if i < len(frames) - 1:
            clearScreen()
            print("\033[1;20H" + hps[abs(8 - enemy)])
            print("\033[1;1H" + hps[abs(8 - hp)])
        print("\033[5;1H" + frames[i])
        if len(frames) - 1 > 1:
            jeffreyFrame = 0
        else:
            if jeffreyFrame == 0:
                jeffreyFrame += 1
            elif jeffreyFrame == 1:
                print("\033[6;20H                       ")
                jeffreyFrame -= 1
        print("\033[1;20H" + jeffrey[jeffreyFrame])
        time.sleep(delay)

def animateChar(animation, repeat):
    for _ in range(repeat):  
        animate(animation)

def animateJeffrey(frames):
    for frame in frames:
        print("\033[2K\033[1G" + frame, end="\r", flush=True)
        time.sleep(0.3)
    
def updateHealInterval():
    global healInterval
    healInterval += 1
    #print(f"HealInterval: {healInterval}")
    threading.Timer(1, updateHealInterval).start() 

def jeffreyHealthUp():
    global healCountdown
    global enemy
    enemy += 1
    return enemy
    threading.Timer(20, jeffreyHealthUp).start() 






name = input("name: ")
print("welcome..."+name)
time.sleep(0.5)
animateJeffrey(jeffreyIntro)
answer = input("\ndo you accept? ")
while start == False:
    if answer.lower() == "yes" or answer.lower() == "y":
        start = True
    elif answer.lower() == "no" or answer.lower() == "n":
        exit()
    else:
        answer = input("is that a yes or a no? ")

if start == True and characterPicked == False:
    charPick = int(input("pick your character:\n1: (*ᴗ͈ˬᴗ͈) ꕤ*.ﾟ      2: (•́ ⍜ •̀) ⋆｡𖦹°⭒         3:(¬_¬”) ✪ ✪ ✪\n"))
    if charPick in [1, 2, 3]:
        characterPicked = True
        if charPick == 1:
            charFrames = characterOne
        elif charPick == 2:
            charFrames = characterTwo
        elif charPick == 3:
            charFrames = characterThree
    else:
        print("i don't believe that was an option")

print("\n")
print("RULES\nto attack, press 1.\nto defend, press 2.\nafter each 10s, you will be able press 3 to solve for \nthe denary value of a binary number\nsolve correctly and gain 2hp, or fail and lose 1hp\njeffrey's health will recieve +1hp every 20s \n\nattack strength will be randomised")
print("\n")
time.sleep(6)
clearScreen()
threading.Timer(1, updateHealInterval).start() 
threading.Timer(20, jeffreyHealthUp).start() 
while hp > 0 and enemy > 0:
    print("\033[1;1H" + hps[min(abs(8 - hp),8)])
    print("\n")
    if animationPlaying == True:
        animateChar(charFrames, 3)
        animationPlaying = False
        jeffreyStay = True
    else:
        print("\033[5;1H"+charFrames[0])
        print(jeffrey[0])
    #print("\033[5;1H")
    if jeffreyStay:
        print("\033[6;20H             ")
        print(jeffrey[0])
        print("\033[1;20H" + hps[abs(8 - enemy)])
    print("\033[11;1H\033[2K")
    print("\033[12;1H\033[2K")
    decision = input("\033[10;1Hattack, defend or heal? ")
    if decision == "1":
        startAttack = True
        attack = random.randint(0,3)
        print("\n")
        enemy = enemy - attack
        if attack != 0:
            if charFrames == characterOne:
                print("\033[5;1H")
                animateChar(attackOne, 1)
                print("\033[5;14H      ")
            elif charFrames == characterTwo:
                print("\033[5;1H")
                animateChar(attackTwo, 1)
                print("\033[5;14H      ")
            elif charFrames == characterThree:
                print("\033[5;1H")
                animateChar(attackThree, 1)
                print("\033[5;14H      ")
            #print("\033[7;1H")
            print("\033[11;1Hgood shot! jeffrey lost",str(attack)+"x health  ")
            time.sleep(0.8)

        elif attack == 0:
            #print("\033[7;1H")
            print("\033[11;1Hlol jeffrey lost 0x health                     ")
            time.sleep(0.5)
    elif decision == "2":
        defendStreak += 1
        if defendStreak > 2:
            print("\033[11;1Hyou've already defended twice in a row.\nyou cannot defend again")
            time.sleep(1.5)
            defendStreak -= 2
            startAttack = True
        else:
            attack = random.randint(0,3)
            #print("\033[7;1H")
            print("\033[11;1Hyou deflected an attack of",str(attack)+"x strength")
            time.sleep(0.7)
            print("\033[12;1H\033[2K")
            startAttack = False
            if charFrames == characterOne:
                print("\033[5;1H"+defending[0])
                time.sleep(0.7)
            elif charFrames == characterTwo:
                print("\033[5;1H"+defending[1])
                time.sleep(0.7)
            elif charFrames == characterThree:
                print("\033[5;1H"+defending[2])
                time.sleep(0.7)
    elif decision == "3" and (healInterval - 10) > 0:
        startAttack = True
        healInterval = healInterval - 10
        if whichBinary <= len(healBinary) - 1:
            healInput = int(input(f"\033[11;1Hsolve: {healBinary[whichBinary]}\nanswer: "))
            if str(healInput) == healAnswers[whichBinary]:
                print("\033[12;1Hcorrect! 2hp gained")
                time.sleep(0.5)
                whichBinary += 1
                if hp <= 6:
                    hp = hp + 2
                else:
                    hp = hp + (8 - hp)
            else:
                print("\033[12;1Hunlucky. -1hp.")
                time.sleep(0.5)
                hp -= 1
        else:
            print("\033[11;1Hyou've used up all available heal puzzles")
            time.sleep(0.5)
    elif not (healInterval - 10) > 0:
        print("\033[11;1H10 seconds have not elapsed yet.")
        time.sleep(0.5)
        startAttack = False
    else:
        print("what? ")
    hit = random.randint(0,3)
    if startAttack:
        time.sleep(0.5)
        #print("\033[7;1H")
        print("\033[11;1Hyou were hit with an attack of",str(hit)+"x strength")
        time.sleep(0.9)
        jeffreyAttack = True
        if jeffreyAttack:
            if charPick == 1:
                print("\033[5;1H"+AttackedFace[0])
                animateJeffrey(jeffreyHit)
                jeffreyAttack = False
            elif charPick == 2:
                print("\033[5;1H"+AttackedFace[2])
                animateJeffrey(jeffreyHit)
                clearScreen()
                print("\033[1;1H"+hps[abs(hp-8)])
                print("\033[5;1H"+characterTwo[0])
                time.sleep(0.5)
                jeffreyAttack = False
            elif charPick == 3:
                print("\033[5;1H"+AttackedFace[1])
                animateJeffrey(jeffreyHit)
                jeffreyAttack = False
        time.sleep(0.7)
        jeffreyAttack = False
        hp = hp - hit
        #print("\033[1;30H")
        #print(hps[hpShown])


if hp <= 0 and enemy <= 0:
    time.sleep(0.5)
    clearScreen()
    print("a draw")
    print("\033[2;1H.")
    time.sleep(0.3)
    print("\033[2;1H..")
    time.sleep(0.3)
    print("\033[2;1H...")
    time.sleep(0.3)
    print("lame")
    time.sleep(0.5)
    exit()
elif hp <= 0:
    time.sleep(0.5)
    clearScreen()
    print("\nbetter luck next time")
    time.sleep(1)
    clearScreen()
    print("game over\n¯\\_(ツ)_/¯")
    exit()
elif enemy <= 0:
    time.sleep(0.5)
    clearScreen()
    print("you...beat jeffrey? YOU beat jeffrey?")
    time.sleep(0.6)
    print("huh")
    time.sleep(0.6)
    print("...")
    time.sleep(0.6)
    print("...well done")
    exit()
