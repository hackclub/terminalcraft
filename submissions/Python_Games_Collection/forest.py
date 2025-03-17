import time
import sys

def slow_print(text, delay=0.05):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def print_intro():
    slow_print("Welcome to the Forest of Shadows!")
    slow_print("You find yourself at the edge of a dark and mysterious forest.")
    slow_print("Legends say that those who enter never return...")
    slow_print("But you are brave. You step forward into the unknown.\n")

def choose_path():
    slow_print("You come across a fork in the path.")
    slow_print("To the left, you see a faint glow in the distance.")
    slow_print("To the right, you hear the sound of running water.")
    slow_print("Straight ahead, the path is dark and overgrown.")
    choice = input("Do you go left, right, or straight? (left/right/straight): ").lower()
    return choice

def left_path():
    slow_print("\nYou follow the path to the left.")
    slow_print("The glow grows brighter, and you find a clearing with a strange, glowing crystal.")
    slow_print("As you approach, you feel a surge of energy.")
    slow_print("Do you touch the crystal or leave it alone?")
    choice = input("Touch or leave? (touch/leave): ").lower()
    if choice == "touch":
        slow_print("\nThe crystal shatters, and a wave of energy knocks you unconscious.")
        slow_print("You wake up hours later, feeling stronger and more aware.")
        slow_print("You gain the power of foresight!")
        return "foresight"
    else:
        slow_print("\nYou decide to leave the crystal alone and continue your journey.")
        return None

def right_path():
    slow_print("\nYou follow the path to the right.")
    slow_print("You come across a river with a rickety bridge.")
    slow_print("Do you attempt to cross the bridge or look for another way?")
    choice = input("Cross or search? (cross/search): ").lower()
    if choice == "cross":
        slow_print("\nThe bridge collapses under your weight, but you manage to grab onto a branch.")
        slow_print("You pull yourself up and continue your journey, shaken but unharmed.")
        return None
    else:
        slow_print("\nYou find a hidden path along the riverbank and safely continue your journey.")
        return None

def straight_path():
    slow_print("\nYou venture straight into the dark and overgrown path.")
    slow_print("The trees close in around you, and you hear strange whispers.")
    slow_print("Suddenly, a shadowy figure blocks your path!")
    slow_print("Do you fight or try to reason with it?")
    choice = input("Fight or reason? (fight/reason): ").lower()
    if choice == "fight":
        slow_print("\nThe shadowy figure is too powerful. You are defeated.")
        return "game_over"
    else:
        slow_print("\nYou speak calmly, and the figure steps aside, revealing a hidden treasure!")
        slow_print("You find a magical amulet that protects you from harm.")
        return "amulet"

def game_over():
    slow_print("\nYour journey ends here. The Forest of Shadows has claimed another soul.")
    slow_print("Game Over.")

def victory():
    slow_print("\nYou emerge from the Forest of Shadows, stronger and wiser.")
    slow_print("You have conquered the darkness and uncovered its secrets.")
    slow_print("Congratulations! You win!")

def main():
    print_intro()
    player_has_amulet = False
    player_has_foresight = False

    while True:
        path = choose_path()

        if path == "left":
            result = left_path()
            if result == "foresight":
                player_has_foresight = True
        elif path == "right":
            result = right_path()
        elif path == "straight":
            result = straight_path()
            if result == "amulet":
                player_has_amulet = True
            elif result == "game_over":
                game_over()
                break
        else:
            slow_print("Invalid choice. Try again.")
            continue

        if player_has_amulet and player_has_foresight:
            victory()
            break

if __name__ == "__main__":
    main()
