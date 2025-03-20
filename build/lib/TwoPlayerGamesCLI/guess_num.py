import random
import os
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
def pass_func():
    pass

def description():
    print('''
How to play? 
A random number will be generated  
player1 will type a number the game will tell how closer he is. 
The game will count the number of tries player1 takes. 
After he guesses it player2 will take the next turn.
The one with the least tries wins 
points are based on diffrence of tries taken
          


MODES
 s: here both players would be given the same numbers.
 d: players will be given different numbers

SETUP:
    (<mode_leter>,<range MinNum-MaxNum>)
e.g (d,100,10000) // its also the default mode 

''')
    
def main_game(info_func=description):
    info_func()
    try:
        b = input('>').removeprefix('(').removesuffix(')')
        
        mode,min_range,max_range= b.split(',')
        mode = str(mode)
        min_range = int(min_range)
        max_range = int(max_range)
    except:
        print("invalid format! type again")
        main_game(pass_func)
    number = random.randint(min_range,max_range)
    print('''Lets start! player1 you are up
          ssh.. player2 no peeking!
          ''')
    player1_tries=game(number,min_range,max_range)
    if mode == 'd':
        number = random.randint(min_range,max_range)
    clear_screen()
    print('Player 2 come up now. prove us you are better than player 1')
    player2_tries=game(number,min_range,max_range)

    if player1_tries > player2_tries:
        player1_points = player1_tries -player2_tries
        player2_points = 0
    else:
        player2_points = player2_tries -player1_tries
        player1_points = 0
    
    return (player1_points,player2_points)


def game(number,min_range,max_range):
    
    guess_counter = 0
    guess = 0
    closest_greater_guess = max_range
    closest_lesser_guess = min_range
    print(f'type a value between {min_range} - {max_range}')
    while guess != number:
        try: 
            guess = int(input('>'))
        except:
            guess = min_range

        if guess > number:
            if guess < closest_greater_guess:
                closest_greater_guess = guess
        elif guess < number:
            if guess > closest_lesser_guess:
                closest_lesser_guess = guess

        guess_counter += 1
        print(f'{closest_lesser_guess}< [actual value] < {closest_greater_guess}')
    else:
        print(f'you guessed it correcty ans:{number} | in {guess_counter} tries ')
        return guess_counter