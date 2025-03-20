player1_points = []
player2_points = []
p1_total = 0
p2_total =0
games = []
reactions = ["⚆_⚆", "🫡", "😊", "😁", "😀", "😎", "🤨", ";D", "(⓿_⓿)", "^_^", "><", "(^_^)", "⊙﹏⊙∥"]
import guess_num
import os
import TruthLie 
import WordChain
import Unscramble
import ConnectFour
import HangMan
import random
a = '''
Pls select your games . 
you may select as many as you like 

enter it in form of a list 
in the following format
[1,5,3,1] 
you can type the number repeatedly for playing the same game game over
note only int game numbers are accepted


Games:
1) Number guessing 🔢
2) Hang man 😵
5) 2 truths and a lie 🤫
6) coonect 4 (⓿_⓿)
7) word chain ⛓️
8) scramble unscramble word 🧠
>
'''
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def take_games(extra_text=''):
    try:
        global games
        games = eval(input(a+extra_text))
        count = 0
        for i in range(len(games)):
            games[i] = int(games[i]) 
    except:
        
         take_games('invalid pls retype it>')
    print(games)



def output_marks():
    global p1_total, p2_total
    score_variancy = p1_total - p2_total
    winner = 'Player1' if score_variancy > 0 else 'Player2' if score_variancy < 0 else 'null'
    print(f'''
Player 1 | total = {p1_total} | marks spectator = {player1_points}
Player 2 | total = {p2_total} | marks spectator = {player2_points}
{winner} wins by {abs(score_variancy)} points.
''')
    
def appending_points(mytuple=(0,0)):
    global p1_total, p2_total
    p1,p2 = mytuple
    player1_points.append(p1)
    player2_points.append(p2)
    p1_total += p1
    p2_total += p2
    print(f'''
Player 1 | total = {p1_total} | marks gained = {p1}
Player 2 | total = {p2_total} | marks gained = {p2}
''')

def next_game():
    print(reactions[random.randint(0,len(reactions)-1)])
    print('Press enter to start the next game')
    input('>')
    clear_screen()
    
game_dict={
   0 : 0+0,
   1 : guess_num.main_game,
   2 : HangMan.hangman_game,
   5 : TruthLie.game,
   6 : ConnectFour.play_game,
   7 : WordChain.word_chain_game,
   8 : Unscramble.scrambled_word_game
}
game_name_dict={
   0 : 0+0,
   1 : 'guess_num',
   2 : 'HangMan',
   5 : 'TruthLie',
   6 : 'ConnectFour',
   7 : 'WordChain',
   8 : 'Unscramble'
}
def main():
    take_games()
    for v in range(len(games)):
        appending_points(game_dict.get(games[v], lambda: (0,0))())
        try:
            print(f'The next game is :{game_name_dict.get(games[v+1],lambda :(0+0))}')
        except:
            print('The games are finished')
        next_game()
    output_marks()
    x = input('Press enter to leave')

