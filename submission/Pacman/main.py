from Pacman.pacman import *
from os import system, name
import keyboard, time

def clear():
    if name == 'nt':
        system('cls')
    else:
        system('clear')

def run():
    board = Board()
    while True:
        win = board.update()
        if win == True:
            break
        elif win == "LOSS":
            break
        clear()
        print(board)
        if keyboard.is_pressed("w"):
            board.pac.n_direction = 2
            keyboard.press_and_release("backspace")
        if keyboard.is_pressed("a"):
            board.pac.n_direction = 4
            keyboard.press_and_release("backspace")
        if keyboard.is_pressed("s"):
            board.pac.n_direction = 1
            keyboard.press_and_release("backspace")
        if keyboard.is_pressed("d"):
            board.pac.n_direction = 3
            keyboard.press_and_release("backspace")
        time.sleep(1/30)

    clear()
    print(board)
