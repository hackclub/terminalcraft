from simple_colors import *
import keyboard, os, time

#* Importing the Games
import Pacman.main
import Wordle.main
import Tic_Tac_Toe.main
import Minesweeper.main
import Hangman.main
import Connect_4.main

def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

if __name__ == "__main__":
    clear()
    print("Welcome to", green("Terminal Games!", 'bold'))
    while True:
        print(blue("Press 1 to"), green("play"), blue("2 to"), red("quit"))
        while True:
            if keyboard.is_pressed("1"):
                keyboard.press_and_release("backspace")
                print(
                    blue("Press:\n"), cyan("c"), blue("for Connect 4\n"), cyan("h"),
                    blue("for Hangman\n"), cyan("m"), blue("for Minsweeper\n"), cyan("p"),
                    blue("for PacMan\n"), cyan("t"), blue("for Tic Tac Toe\n"), cyan("w"),
                    blue("for Wordle\n"), red("q"), blue("to quit")
                )
                # clear()
                while True:
                    if keyboard.is_pressed("c"):
                        clear()
                        keyboard.press_and_release("backspace")
                        Connect_4.main.run()
                        time.sleep(3)
                        clear()
                        break
                    
                    elif keyboard.is_pressed("h"):
                        clear()
                        keyboard.press_and_release("backspace")
                        Hangman.main.run()
                        time.sleep(3)
                        clear()
                        break
                    elif keyboard.is_pressed("m"):
                        clear()
                        keyboard.press_and_release("backspace")
                        Minesweeper.main.run()
                        time.sleep(3)
                        clear()
                        break
                    
                    elif keyboard.is_pressed("p"):
                        clear()
                        keyboard.press_and_release("backspace")
                        Pacman.main.run()
                        time.sleep(3)
                        clear()
                        break
                    
                    elif keyboard.is_pressed("t"):
                        clear()
                        keyboard.press_and_release("backspace")
                        Tic_Tac_Toe.main.run()
                        time.sleep(3)
                        clear()
                        break
                    
                    elif keyboard.is_pressed("w"):
                        clear()
                        keyboard.press_and_release("backspace")
                        Wordle.main.run()
                        time.sleep(3)
                        clear()
                        break
                    
                    elif keyboard.is_pressed("q"):
                        clear()
                        keyboard.press_and_release("backspace")
                        quit()
                break
            elif keyboard.is_pressed("2"):
                keyboard.press_and_release("backspace")
                quit()