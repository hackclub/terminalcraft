import random
import time
import json
import os
import curses
from random import randint
from random import randrange
from curses import initscr, curs_set, newwin, KEY_RIGHT, KEY_LEFT, KEY_DOWN, KEY_UP

# Variables for the snake game tha is available on Menu > Mini games > Play snake
# Capitalize all letters for proper curses syntax
WIDTH = 40
HEIGHT = 16
MAX_X = WIDTH - 2
MAX_Y = HEIGHT - 2
SNAKE_LENGTH = 5
SNAKE_X = SNAKE_LENGTH + 1
SNAKE_Y = 3
TIMEOUT = 100


# Information about the snake
class Snake(object):
    # Erase everything inside the snake object and add REV_DIR_MAP
    REV_DIR_MAP = {
        KEY_UP: KEY_DOWN, KEY_DOWN: KEY_UP,
        KEY_LEFT: KEY_RIGHT, KEY_RIGHT: KEY_LEFT,
    }

    def __init__(self, x, y, window):
        self.body_list = []
        self.hit_score = 0
        self.timeout = TIMEOUT

        for i in range(SNAKE_LENGTH, 0, -1):
            self.body_list.append(Body(x - i, y))

        # Define and append the snakes head,
        self.body_list.append(Body(x, y, '0'))
        self.window = window
        self.direction = KEY_RIGHT
        # Set snakes lst head coordinate
        self.last_head_coor = (x, y)
        # Define direction map
        # In case of a bug/ misfunction check curses documentation for updated keys
        self.direction_map = {
            KEY_UP: self.move_up,
            KEY_DOWN: self.move_down,
            KEY_LEFT: self.move_left,
            KEY_RIGHT: self.move_right
        }

    # Make Properties on the objects, which is a special decorator that modifies the function. makes it so when you
    # access the attribute,it auto calls the function.
    @property
    def score(self):
        return 'Score : {}'.format(self.hit_score)

    def add_body(self, body_list):
        self.body_list.extend(body_list)

    # Whenever the snake eats some food increase the body size by one unless the limit is reached
    def eat_food(self, food):
        food.reset()
        body = Body(self.last_head_coor[0], self.last_head_coor[1])
        self.body_list.insert(-1, body)
        self.hit_score += 1
        if self.hit_score % 3 == 0:
            self.timeout -= 5
            self.window.timeout(self.timeout)

    # Once the snake touched it's own body give negative value and then prepare to terminate the game
    @property
    def collided(self):
        return any([body.coor == self.head.coor
                    for body in self.body_list[:-1]])

    # get the x.y. coordinates of the snakes body and update the screen with the new movement
    def update(self):
        last_body = self.body_list.pop(0)
        last_body.x = self.body_list[-1].x
        last_body.y = self.body_list[-1].y
        self.body_list.insert(-1, last_body)
        self.last_head_coor = (self.head.x, self.head.y)
        self.direction_map[self.direction]()

    def change_direction(self, direction):
        if direction != Snake.REV_DIR_MAP[self.direction]:
            self.direction = direction

    def render(self):
        for body in self.body_list:
            self.window.addstr(body.y, body.x, body.char)

    @property
    def head(self):
        return self.body_list[-1]

    # Function that define the snakes movement
    @property
    def coor(self):
        return self.head.x, self.head.y

    def move_up(self):
        self.head.y -= 1
        if self.head.y < 1:
            self.head.y = MAX_Y

    def move_down(self):
        self.head.y += 1
        if self.head.y > MAX_Y:
            self.head.y = 1

    def move_left(self):
        self.head.x -= 1
        if self.head.x < 1:
            self.head.x = MAX_X

    def move_right(self):
        self.head.x += 1
        if self.head.x > MAX_X:
            self.head.x = 1


# Info about the games borders and the snakes body
class Body(object):
    # Initialize Self [body]
    def __init__(self, x, y, char='='):
        self.x = x
        self.y = y
        self.char = char

    # Modify function with special property decorator
    @property
    def coor(self):
        return self.x, self.y


# Food Class with all info and objects that are nemeses for letting the snake to eat food
class Food(object):
    # Initialize the Food
    def __init__(self, window, char='&'):
        # Pick a random position for food whenever its Initialized
        self.x = randint(1, MAX_X)
        self.y = randint(1, MAX_Y)
        # Complete the arguments, and sett the food character
        self.char = char
        self.window = window

    def render(self):
        self.window.addstr(self.y, self.x, self.char)

    # Reset food when necessary
    def reset(self):
        self.x = randint(1, MAX_X)
        self.y = randint(1, MAX_Y)


# A Player class with information and objects that the player will use during the game.
class Player:
    def __init__(self, p_reliability, p_health, p_name, p_role):
        self.reliability = p_reliability
        self.health = p_health
        self.name = p_name
        self.role = p_role

    # Get users info
    # With the function below can be called each of the players info outside of menu.py
    def get_health(self):
        return self.health

    def get_name(self):
        return self.name

    def get_reliability(self):
        return self.reliability

    def get_role(self):
        return self.role

    # Change the users info if necessary
    def set_health(self, new_health):
        self.health = new_health

    def set_name(self, new_name):
        self.name = new_name

    def set_reliability(self, new_reliability):
        self.reliability = new_reliability

    def set_role(self, new_role):
        self.role = new_role


# A Civilian class with information and objects that the civilian will use during the game.
class Civilians:
    def __init__(self, c_reliability, c_health, c_name, c_role, c_cat, c_pic, c_hair, c_eyes, c_item, c_story, c_alibi,
                 c_line, c_wline):
        self.reliability = c_reliability
        self.health = c_health
        self.name = c_name
        self.role = c_role
        self.category = c_cat
        self.picture = c_pic
        self.hair = c_hair
        self.eyes = c_eyes
        self.item = c_item
        self.story = c_story
        self.alibi = c_alibi
        self.pro_line = c_line
        self.w_line = c_wline

    def get_health(self):
        return self.health

    def get_name(self):
        return self.name

    def get_reliability(self):
        return self.reliability

    def get_role(self):
        return self.role

    def get_category(self):
        return self.category

    def get_picture(self):
        return self.picture

    def get_hair(self):
        return self.hair

    def get_eyes(self):
        return self.eyes

    def get_item(self):
        return self.item

    def get_story(self):
        return self.story

    def get_alibi(self):
        return self.alibi

    def get_pro_line(self):
        return self.pro_line

    def get_w_line(self):
        return self.w_line

    # Change the users info if necessary
    def set_health(self, new_health):
        self.health = new_health

    def set_name(self, new_name):
        self.name = new_name

    def set_reliability(self, new_reliability):
        self.reliability = new_reliability

    def set_role(self, new_role):
        self.role = new_role

    def set_picture(self, new_picture):
        self.picture = new_picture


# A Mafia class with information and objects that the doctor will use during the game.
class Mafia:
    def __init__(self, m_reliability, m_health, m_name, m_role, m_weapon, m_pic, m_hair, m_eyes, m_item, m_frole,
                 m_story, m_alibi, m_line, m_wline):
        # define the basic info for the Mafioso
        self.reliability = m_reliability
        self.health = m_health
        self.name = m_name
        self.role = m_role
        self.weapon = m_weapon
        self.picture = m_pic
        self.hair = m_hair
        self.eyes = m_eyes
        self.item = m_item
        self.real_role = m_frole
        self.story = m_story
        self.alibi = m_alibi
        self.pro_line = m_line
        self.w_line = m_wline

    # With the function below can be called each of the players info outside of menu.py
    def get_health(self):
        return self.health

    def get_name(self):
        return self.name

    def get_reliability(self):
        return self.reliability

    def get_role(self):
        return self.role

    def get_weapon(self):
        return self.weapon

    def get_picture(self):
        return self.picture

    def get_hair(self):
        return self.hair

    def get_eyes(self):
        return self.eyes

    def get_item(self):
        return self.item

    def get_real_role(self):
        return self.real_role

    def get_story(self):
        return self.story

    def get_alibi(self):
        return self.alibi

    def get_pro_line(self):
        return self.pro_line

    def get_w_line(self):
        return self.w_line

    # Change the users info if necessary
    def set_health(self, new_health):
        self.health = new_health

    def set_name(self, new_name):
        self.name = new_name

    def set_reliability(self, new_reliability):
        self.reliability = new_reliability

    def set_role(self, new_role):
        self.role = new_role

    def set_weapon(self, new_weapon):
        self.weapon = new_weapon

    def set_fake_role(self, new_real_role):
        self.real_role = new_real_role


# A Detective class with information and objects that the doctor will use during the game.
class Detective:
    def __init__(self, d_reliability, d_health, d_name, d_role, d_pic, d_hair, d_eyes, d_item, d_story, d_alibi, d_line,
                 d_wline):
        # define the basic info for the Detective
        self.reliability = d_reliability
        self.health = d_health
        self.name = d_name
        self.role = d_role
        self.picture = d_pic
        self.hair = d_hair
        self.eyes = d_eyes
        self.item = d_item
        self.story = d_story
        self.alibi = d_alibi
        self.pro_line = d_line
        self.w_line = d_wline

    # With the function below can be called each of the players info outside of menu.py
    def get_health(self):
        return self.health

    def get_name(self):
        return self.name

    def get_reliability(self):
        return self.reliability

    def get_role(self):
        return self.role

    def get_picture(self):
        return self.picture

    def get_hair(self):
        return self.hair

    def get_eyes(self):
        return self.eyes

    def get_item(self):
        return self.item

    def get_story(self):
        return self.story

    def get_alibi(self):
        return self.alibi

    def get_pro_line(self):
        return self.pro_line

    def get_w_line(self):
        return self.w_line

    # Change the users info if necessary
    def set_health(self, new_health):
        self.health = new_health

    def set_name(self, new_name):
        self.name = new_name

    def set_reliability(self, new_reliability):
        self.reliability = new_reliability

    def set_role(self, new_role):
        self.role = new_role

    def set_picture(self, new_picture):
        self.picture = new_picture


# A Doctor Class created in order to have an organised structure for the bots info that can be used through the game
class Doctor:
    def __init__(self, dc_reliability, dc_health, dc_name, dc_role, dc_pic, dc_hair, dc_eyes, dc_item, dc_story,
                 dc_alibi, dc_line, dc_wline):
        self.reliability = dc_reliability
        self.health = dc_health
        self.name = dc_name
        self.role = dc_role
        self.picture = dc_pic
        self.hair = dc_hair
        self.eyes = dc_eyes
        self.item = dc_item
        self.story = dc_story
        self.alibi = dc_alibi
        self.pro_line = dc_line
        self.w_line = dc_wline

    # With the function below can be called each of the players info outside of menu.py
    def get_health(self):
        return self.health

    def get_name(self):
        return self.name

    def get_reliability(self):
        return self.reliability

    def get_role(self):
        return self.role

    def get_picture(self):
        return self.picture

    def get_hair(self):
        return self.hair

    def get_eyes(self):
        return self.eyes

    def get_item(self):
        return self.item

    def get_story(self):
        return self.story

    def get_alibi(self):
        return self.alibi

    def get_pro_line(self):
        return self.pro_line

    def get_w_line(self):
        return self.w_line

    # Change the users info if necessary
    def set_health(self, new_health):
        self.health = new_health

    def set_name(self, new_name):
        self.name = new_name

    def set_reliability(self, new_reliability):
        self.reliability = new_reliability

    def set_role(self, new_role):
        self.role = new_role

    def set_picture(self, new_picture):
        self.picture = new_picture


# Get input from the user and create the main character
def create_char():  # Get the users information
    # Start a loop for the the character creation until user is done. Then break the loop and continue
    main_loop = True
    while main_loop:
        # Set an empty list for the player role.
        # The program could run without it but it sometimes creates a small bug without it during mid-game
        playerRole = ""

        # Set players health
        # Player is going to receive damage in future versions of the game
        player_health = 100

        # Set starting reliability.
        # Depending on this number some characters may be friendly or hostile in the game.
        player_reliability = random.randint(50, 100)

        # Ensure that the screen is clear before anything new is printed
        os.system('cls' if os.name == 'nt' else 'clear')

        # Print the screen were the player enters his/her name
        print(5 * "\n")
        print("                                         Mafia: The terminal game          ")
        print("                                +--------------------------------------------+")
        print("                                | Hello Player! It's time to pick your name! |")
        print("                                +--------------------------------------------+")
        ask_name = input("                                + My name is: ")

        player_name = ask_name  # Get the name taken from above and set it in a final variable

        # Clear the screen
        os.system('cls' if os.name == 'nt' else 'clear')
        # Print a menu with the available roles
        # In the future this could be more dynamic with proper curses use
        print(5 * "\n")
        print("                                         Mafia: The terminal game          ")
        print("                                +--------------------------------------------+")
        print("                                |   The available roles for the game are:    |")
        print("                                |                                            |")
        print("                                |   [1] Doctor                               |")
        print("                                |   [2] Mafioso                              |")
        print("                                |   [3] Detective                            |")
        print("                                |                                            |")
        print("                                +--------------------------------------------+")
        ask_role = input("                                + Pick a role [1-3]: ")

        if ask_role == "1":  # Player registers as a doctor
            os.system('cls' if os.name == 'nt' else 'clear')

            # Set the player role and use it in the bottom of the function
            player_role = "Doctor"

            # Print a screen asking if the info is correct
            print(5 * "\n")
            print("                               +---------------------------------------------+")
            print(f"                               |    Your name is {player_name}                |")
            print(f"                               |    And, you will be a {player_role}          |")
            print("                               +---------------------------------------------+")
            ask_if_done = input("                                 Are these information correct? [Y/N]: ")
            # If the player is ready pressed to generate the other players else restart the loop
            if ask_if_done == "y":
                os.system('cls' if os.name == 'nt' else 'clear')
                return player_reliability, player_health, player_name, player_role
            elif ask_if_done == "n":
                os.system('cls' if os.name == 'nt' else 'clear')
                print(5 * "\n")
                print("                               +---------------------------------------------+")
                print(f"                               |                                             |")
                print(f"                               |    Ok then lets change the information!     |")
                print(f"                               |                                             |")
                print("                               +---------------------------------------------+")
                time.sleep(2)
                os.system('cls' if os.name == 'nt' else 'clear')
        # Set the player role and use it in the bottom of the function
        elif ask_role == "2":  # Player registers as a member of the Mafia
            os.system('cls' if os.name == 'nt' else 'clear')
            player_role = "Mafioso"
            print(5 * "\n")
            print("                               +---------------------------------------------+")
            print(f"                               |    Your name is {player_name}                |")
            print(f"                               |    And, you will be a {player_role}          |")
            print("                               +---------------------------------------------+")
            ask_if_done = input("                                 Are these information correct? [Y/N]: ")
            # If the player is ready pressed to generate the other players else restart the loop
            if ask_if_done == "y":
                os.system('cls' if os.name == 'nt' else 'clear')
                # If done return all made variables
                return player_reliability, player_health, player_name, player_role
            elif ask_if_done == "n":
                os.system('cls' if os.name == 'nt' else 'clear')
                print(5 * "\n")
                print("                               +---------------------------------------------+")
                print(f"                               |                                             |")
                print(f"                               |    Ok then lets change the information!     |")
                print(f"                               |                                             |")
                print("                               +---------------------------------------------+")
                time.sleep(2)
                os.system('cls' if os.name == 'nt' else 'clear')
        elif ask_role == "3":  # Player registers as a Detective
            os.system('cls' if os.name == 'nt' else 'clear')

            player_role = "Detective"
            print(5 * "\n")
            print("                               +---------------------------------------------+")
            print(f"                               |    Your name is {player_name}                |")
            print(f"                               |    And, you will be a {player_role}          |")
            print("                               +---------------------------------------------+")
            ask_if_done = input("                                 Are these information correct? [Y/N]: ")
            if ask_if_done == "y":
                os.system('cls' if os.name == 'nt' else 'clear')
                return player_reliability, player_health, player_name, player_role
            elif ask_if_done == "n":
                os.system('cls' if os.name == 'nt' else 'clear')
                print(5 * "\n")
                print("                           +---------------------------------------------+")
                print(f"                          |                                             |")
                print(f"                          |    Ok then lets change the information!     |")
                print(f"                          |                                             |")
                print("                           +---------------------------------------------+")
                time.sleep(2)
                os.system('cls' if os.name == 'nt' else 'clear')
        else:  # Inform the user about the incorrect input
            os.system('cls' if os.name == 'nt' else 'clear')

            print(5 * "\n")
            print("                                         Mafia: The terminal game          ")
            print("                                +--------------------------------------------+")
            print("                                |       Invalid selection! Try again         |")
            print("                                +--------------------------------------------+")
            time.sleep(2)
            os.system('cls' if os.name == 'nt' else 'clear')


def create_civilians():
    # create an empty list to set temporarily information
    # Mostly needed as safety net for bugs within the actually game
    temp = []
    # Set the category to each player so it can be compared with the others in the late game
    category = "Civilian"
    # Create a list with professions that will be given to four of the players
    roles = ["biologist", "tour-guide", "programmer", "librarian", "baker", "teacher", "photographer", "writer",
             "blogger"]
    # Standard health.
    # In later versions civilians could take damage
    health = 100
    # Reliability that will be seen on the very first meeting with the player
    reliability = random.randint(50, 100)
    role = str(*random.choices(roles, weights=(12, 12, 12, 12, 12, 12, 12, 12, 12), k=1))
    # Open the name with all names available and pick one randomly
    file = open("names.txt", "r")
    lines = file.readlines()
    name = lines[random.randint(0, len(lines) - 1)][:-1]
    char = name
    file.close()

    # Open the files with all male names
    with open("male_names.txt", "r") as file:
        file.seek(0)  # set position to start of file
        lines = file.read().splitlines()  # now we won't have newlines
        if char in lines:   # If the name above is found in the male file then the character is a male
            # Since character is male then pick a male avatar from collection
            pics = ("ascii/male_one.txt", "ascii/male_two.txt", "ascii/male_three.txt",
                    "ascii/male_four.txt", "ascii//male_five.txt", "ascii//male_six.txt",
                    "ascii//male_seven.txt", "ascii/male_eight.txt", "ascii/male_nine.txt")
            pick_choice = str(*random.choices(pics, weights=(12, 12, 12, 12, 12, 12, 12, 12, 12), k=1))
        # If the name is not in the male names then the user is clearly a female (for simplicity)
        else:
            # write to file
            pics = ("ascii/female_one.txt", "ascii/female_two.txt", "ascii/female_three.txt",
                    "ascii/female_four.txt", "ascii/female_five.txt", "ascii/female_six.txt",
                    "ascii/female_seven.txt", "ascii/female_eight.txt", "ascii/female_nine.txt")
            pick_choice = str(*random.choices(pics, weights=(12, 12, 12, 12, 12, 12, 12, 12, 12), k=1))

    # Get the picture and pass it in the final variable for the picture that will be sent down
    pic = pick_choice

    hair_colors = ["blue", "brown", "black", "green", "grey", "white", "blonde"]
    # Shuffle to lower the risk of picking the same item twice
    random.shuffle(hair_colors)
    hair = str(*random.choices(hair_colors, weights=(12, 12, 12, 12, 12, 12, 12), k=1))

    eye_colors = ["blue", "brown", "black", "green", "grey", "white", "blonde"]
    # Shuffle to lower the risk of picking the same item twice
    random.shuffle(eye_colors)
    eyes = str(*random.choices(eye_colors, weights=(12, 12, 12, 12, 12, 12, 12), k=1))

    items = ["book", "smartphone", "wallet", "watch", "hair brush", "makeup set", "pen", "pack of tissues",
             "plastic duck", "protein bar", "small sandwich", "power-bank", "swiss army knife", "flashlight"]
    # Shuffle to lower the risk of picking the same item twice
    random.shuffle(items)
    item = str(*random.choices(items, weights=(12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12)))

    # Create a list and store lines about every characters connection with uncle Ben
    stories = [
        "I knew Ben since we where kids. We grew up in the same neighbourhood and kept in touch all these years.",
        "We used to go to the same school and even work part time in the same place when we were teenagers",
        "I didn't know him very well to be honest. My brother used to work with him in a business of sorts so ",
        "I got the chance to get to know him a bit but besides that we didn't speak much",
        "Together with Ben we served in the military for two years. Since then we were good friends. He was a good man ",
        "With Ben we worked on the same company for several years. Then he came one day and said that he decided to take a risk and start a business of his own",
        "I have been helping Ben with his taxes for the last five years. Ever since he started his own business he needed all the help that he could get",
        "I met Ben when I first came to the town in search of work. He introduced me to one of his friends that own a convenience store a few blocks from here"]

    # Shuffle to lower the risk of picking the same item twice
    random.shuffle(stories)
    # Pick a random story and assign it to a civilian
    story = str(*random.choices(stories, weights=(12, 12, 12, 12, 12, 12, 12, 12), k=1))

    # Create a list and store lines about every characters alibi
    alibies = [
        "Before the assassination happened I was in the staff room trying to clean my clothes. I was drinking some wine you see and I had a small accident.",
        "I was downstairs in the kitchen. I wanted some water and that's why I went there to get some.",
        "As far as I remember I was pretty much drunk the hole time. When I heard about the assassination I was with that detective and we had a discussion about old criminals.",
        "Well that's a bit embracing but when the police came in the house I was in the toilet. You see I had some spicy food before the party and my stomach was killing me.",
        "Before the incident I remember going outside to smoke a cigarette. Once I was done, I came back in and heard about the murder.",
        "Well I was very tired that night to be honest and I decided to sneak in one of the bedrooms and take a quick nap. Unfortunately I woke up and the police was here asking me about the murder.",
        "I was in the hallway looking at the painting when I heard a gunshot from upstairs. I was scared and I immediately run out of the house",
        "Before the assassination I was outside the house, having a phone-call with my daughter.",
        "I was in the buffet in the main hall. I was quite hungry and there were plenty of great foods and drinks waiting for me",
        "To be honest I was in the kitchen in my phone texting some friends. When I heard the gunshot I ran towards the living room to check with the others what happened"]
    # Shuffle to lower the risk of picking the same item twice
    random.shuffle(alibies)
    # Pick an alibi and assign it to a civilian
    alibi = str(*random.choices(alibies, weights=(12, 12, 12, 12, 12, 12, 12, 12, 12, 12), k=1))

    # Create a list and store lines about every characters alibi
    profession_lines = ["Its not very exciting to be honest",
                        "It has its own ups and downs but I can't complain I like that work.",
                        "Although it might be quite boring at times its an interesting and fun job",
                        "Its a profession that may seem boring to some but is fun most of the times.",
                        "My father used to be one also and I decided to keep this profession in the family.",
                        "The money you get out of it are very good and it is a job with a lot of opportunities",
                        "Sometimes it becomes one of the most interesting professions and other times it is just ok",
                        "As a job it may not seem very compelling but I like it because I get to help a lot of people",
                        "I would actually quit my job if it was on my hand but it is not easy to find a new one in this town",
                        "I find it to be one of the most boring jobs out there but it pays a lot of money. So I guess it's not that bad after all"]

    # Shuffle to lower the risk of picking the same item twice
    random.shuffle(profession_lines)
    # Pick an alibi and assign it to a civilian
    pro_line = str(*random.choices(profession_lines, weights=(12, 12, 12, 12, 12, 12, 12, 12, 12, 12), k=1))

    # Create a list and store lines about anything weird seen during the party
    w_lines = [" Well I am not sure....There was a lot of noise that night. Nothing out of the ordinary",
               "I may be wrong but I think I saw someone seeking in the house about 21:40. It was a man with a black coat",
               "At some point I went to the bathroom and I heard two members of the staff whispering. It may be nothing but they seemed concerned",
               " While I was in the kitchen, trying to get my self some water, I found some broken glass on the floor.",
               "I guess the only suspicious thing that I saw was these two guys out of the house but they were part of the security",
               "There was this guy called Mark who claimed to be Ben's friend from high school. I didn't really like him.",
               "I think I saw some broken glass near the window on the library upstairs.",
               "There was this lady that was looking at her phone the whole night. It looked like she was waiting for a phone-call or something.",
               " Well, while I was in the main hall drinking some wine, I overheard a guy talking on his phone about an important event taking place the day after",
               "Once I was outside the house I saw a black BMV parked behind some trees. I don't know if that's helpful but it may be of use for investigation"]

    # Shuffle to lower the risk of picking the same item twice
    random.shuffle(w_lines)
    # Pick an alibi and assign it to a civilian
    w_line = str(*random.choices(w_lines, weights=(12, 12, 12, 12, 12, 12, 12, 12, 12, 12), k=1))

    # Return all in the Civilian class so they can be accessed later on without problem
    return reliability, health, char, role, category, pic, hair, eyes, item, story, alibi, pro_line, w_line


# Create the mafia character
# It works with the same logic as the create_civilians function
def create_mafia():
    temp = []
    file = open("names.txt", "r")
    lines = file.readlines()
    name = lines[random.randint(0, len(lines) - 1)][:-1]
    char = name
    file.close()

    with open("male_names.txt", "r") as file:
        file.seek(0)  # set position to start of file
        lines = file.read().splitlines()  # now we won't have those newlines
        if char in lines:
            pics = ("ascii/male_one.txt", "ascii/male_two.txt", "ascii/male_three.txt",
                    "ascii/male_four.txt", "ascii//male_five.txt", "ascii//male_six.txt",
                    "ascii//male_seven.txt", "ascii/male_eight.txt", "ascii/male_nine.txt")
            pick_choice = str(*random.choices(pics, weights=(12, 12, 12, 12, 12, 12, 12, 12, 12), k=1))

        else:
            # write to file
            pics = ("ascii/female_one.txt", "ascii/female_two.txt", "ascii/female_three.txt",
                    "ascii/female_four.txt", "ascii/female_five.txt", "ascii/female_six.txt",
                    "ascii/female_seven.txt", "ascii/female_eight.txt", "ascii/female_nine.txt")
            pick_choice = str(*random.choices(pics, weights=(12, 12, 12, 12, 12, 12, 12, 12, 12), k=1))

    pic = pick_choice

    # Create a list with weapons and then randomly assign one to each mafioso
    # The weapons will be used more frequently in feature versions of the game.
    weapon = ["pistol", "knife", "rope", "fire extinguisher", "shovel", "hammer", "chair", "keyboard", "book"]
    weapon = str(*random.choices(weapon, weights=(12, 12, 12, 12, 12, 12, 12, 12, 12), k=1))

    health = 100
    # Depending on the difficulty of the game the reliability could be lowered for easy mode and increased for hard mode
    reliability = random.randint(50, 100)

    # Each mafia member has a fake rol that is seen by all and a hidden real role
    real_role = "Mafioso"

    roles = ["biologist", "tour-guide", "programmer", "librarian", "baker", "teacher", "photographer", "writer",
             "blogger"]
    # This represents the role shown to public
    role = str(*random.choices(roles, weights=(12, 12, 12, 12, 12, 12, 12, 12, 12), k=1))

    hair_colors = ["blue", "brown", "black", "green", "grey", "white", "blonde"]
    hair = str(*random.choices(hair_colors, weights=(12, 12, 12, 12, 12, 12, 12), k=1))

    eye_colors = ["blue", "brown", "black", "green", "grey", "white", "blonde"]
    eyes = str(*random.choices(eye_colors, weights=(12, 12, 12, 12, 12, 12, 12), k=1))

    items = ["book", "smartphone", "wallet", "watch", "hair brush", "makeup set", "pen", "pack of tissues",
             "plastic duck", "protein bar", "small sandwich", "power-bank", "swiss army knife", "flashlight"]
    item = str(*random.choices(items, weights=(12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12)))

    # Create a list and store lines about every characters connection with uncle Ben
    stories = [
        "Well, I met him about ten years ago when he first came to the neighborhood. Good guy and very polite with all",
        "We were actually business partners. He and I had a plan years ago about starting a fast-food franchise.",
        "I work in an advertising company and your uncle wanted help to promote a store or something similar.",
        "I got to meet Ben back in homeschool. We were good friends.",
        "I didn't actually know him very well. I work in the bank and he used to come often in order to make a deposit in his account",
        "Mr. Ben hired me a few years ago as his personal assistant. I helped him with organising his business and speak with potential business investors",
        "I used to work here as a chef until last year. It was great working here but i found a new job offering double the money and more opportunities for me."]

    # Shuffle to lower the risk of picking the same item twice
    random.shuffle(stories)
    # Pick a random story and assign it to a civilian
    story = str(*random.choices(stories, weights=(12, 12, 12, 12, 12, 12, 12), k=1))

    # Create a list and store lines about every characters alibi
    alibies = [
        "That night I was hanging out near the fireplace with some other guest. We were talking about the upcoming elections",
        "When I heard the gunshot, I was outside in the garden. I got dizzy and I needed some fresh air",
        "Hmm...I remember going towards the main hall to grab a drink for me and my wife and then I heard a loud noise from upstairs",
        "I remember going out to take my jacket. While I was out I think I saw someone jumping out of the window, a woman maybe, but it was dark so I may be wrong",
        "Back then I remember talking with Sam, a friend of Ben's, and then we both heard a scream from upstairs"]

    # Shuffle to lower the risk of picking the same item twice
    random.shuffle(alibies)
    # Pick an alibi and assign it to a civilian
    alibi = str(*random.choices(alibies, weights=(12, 12, 12, 12, 12), k=1))

    # Create a list and store lines about every characters alibi
    profession_lines = ["Its not very exciting to be honest",
                        "It has its own ups and downs but I can't complain I like that work.",
                        "Although it might be quite boring at times its an interesting and fun job",
                        "Its a profession that may seem boring to some but is fun most of the times.",
                        "My father used to be one also and I decided to keep this profession in the family.",
                        "The money you get out of it are very good and it is a job with a lot of opportunities",
                        "Sometimes it becomes one of the most interesting professions and other times it is just ok",
                        "As a job it may not seem very compelling but I like it because I get to help a lot of people",
                        "I would actually quit my job if it was on my hand but it is not easy to find a new one in this town",
                        "I find it to be one of the most boring jobs out there but it pays a lot of money. So I guess it's not that bad after all"]

    # Shuffle to lower the risk of picking the same item twice
    random.shuffle(profession_lines)
    # Pick an alibi and assign it to a civilian
    pro_line = str(*random.choices(profession_lines, weights=(12, 12, 12, 12, 12, 12, 12, 12, 12, 12), k=1))

    # Create a list and store lines about anything weird seen during the party
    w_lines = ["I think I heard this woman called Veronica talk about an important event taking place the day after the party. I am not sure if that helps you.",
               "Once I got out of the toilet I overheard some guys talking about a shipment taking place at midnight. They had some serious and troublesome faces",
               "I think I saw that old woman hiding something on her bag. I might be wrong but it could have easily been a small handgun",
               "At some point during the party I got outside in order to smoke a cigarette. Suddenly out of nowhere I heard a man and a blonde woman strongly arguing over an import issue of sorts",
               "It might be my imagination but I think I saw someone with dark hair heading upstairs about 10 minutes before the murder"]

    # Shuffle to lower the risk of picking the same item twice
    random.shuffle(w_lines)
    # Pick an alibi and assign it to a civilian
    w_line = str(*random.choices(w_lines, weights=(12, 12, 12, 12, 12), k=1))

    # Return info to the mafia class in order to create later on a character
    return reliability, health, char, role, weapon, pic, hair, eyes, item, real_role, story, alibi, pro_line, w_line


# Create the detective character
# It works with the same logic as the create_civilians function
def create_detective():
    temp = []
    file = open("names.txt", "r")
    lines = file.readlines()
    name = lines[random.randint(0, len(lines) - 1)][:-1]
    char = name
    file.close()

    with open("male_names.txt", "r") as file:
        file.seek(0)  # set position to start of file
        lines = file.read().splitlines()  # now we won't have those newlines
        if char in lines:
            pics = ("ascii/male_one.txt", "ascii/male_two.txt", "ascii/male_three.txt",
                    "ascii/male_four.txt", "ascii//male_five.txt", "ascii//male_six.txt",
                    "ascii//male_seven.txt", "ascii/male_eight.txt", "ascii/male_nine.txt")
            pick_choice = str(*random.choices(pics, weights=(12, 12, 12, 12, 12, 12, 12, 12, 12), k=1))

        else:
            # write to file
            pics = ("ascii/female_one.txt", "ascii/female_two.txt", "ascii/female_three.txt",
                    "ascii/female_four.txt", "ascii/female_five.txt", "ascii/female_six.txt",
                    "ascii/female_seven.txt", "ascii/female_eight.txt", "ascii/female_nine.txt")
            pick_choice = str(*random.choices(pics, weights=(12, 12, 12, 12, 12, 12, 12, 12, 12), k=1))

    pic = pick_choice

    health = 100
    reliability = random.randint(50, 100)
    role = "Detective"

    hair_colors = ["blue", "brown", "black", "green", "grey", "white", "blonde"]
    hair = str(*random.choices(hair_colors, weights=(12, 12, 12, 12, 12, 12, 12), k=1))

    eye_colors = ["blue", "brown", "black", "green", "grey", "white", "blonde"]
    eyes = str(*random.choices(eye_colors, weights=(12, 12, 12, 12, 12, 12, 12), k=1))

    items = ["book", "smartphone", "wallet", "watch", "hair brush", "makeup set", "pen", "pack of tissues",
             "plastic duck", "protein bar", "small sandwich", "power-bank", "swiss army knife", "flashlight"]
    item = str(*random.choices(items, weights=(12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12)))

    # Create a list and store lines about every characters connection with uncle Ben
    stories = [
        "I knew Ben since we where kids. We grew up in the same neighbourhood and kept in touch all these years.",
        "We used to go to the same school and even work part time in the same place when we were teenagers",
        "I didn't know him very well to be honest. My brother used to work with him in a business of sorts so ",
        "I got the chance to get to know him a bit but besides that we didn't speak much",
        "Together with Ben we served in the military for two years. Since then we were good friends. He was a good man ",
        "With Ben we worked on the same company for several years. Then he came one day and said that he decided to take a risk and start a business of his own",
        "I have been helping Ben with his taxes for the last five years. Ever since he started his own business he needed all the help that he could get",
        "I met Ben when I first came to the town in search of work. He introduced me to one of his friends that own a convenience store a few blocks from here"]

    # Shuffle to lower the risk of picking the same item twice
    random.shuffle(stories)
    # Pick a random story and assign it to a civilian
    story = str(*random.choices(stories, weights=(12, 12, 12, 12, 12, 12, 12, 12), k=1))

    # Create a list and store lines about every characters alibi
    alibies = [
        "Before the assassination happened I was in the staff room trying to clean my clothes. I was drinking some wine you see and I had a small accident.",
        "I was downstairs in the kitchen. I wanted some water and that's why I went there to get some.",
        "As far as I remember I was pretty much drunk the hole time. When I heard about the assassination I was with that detective and we had a discussion about old criminals.",
        "Well that's a bit embracing but when the police came in the house I was in the toilet. You see I had some spicy food before the party and my stomach was killing me.",
        "Before the incident I remember going outside to smoke a cigarette. Once I was done, I came back in and heard about the murder.",
        "Well I was very tired that night to be honest and I decided to sneak in one of the bedrooms and take a quick nap. Unfortunately I woke up and the police was here asking me about the murder.",
        "I was in the hallway looking at the painting when I heard a gunshot from upstairs. I was scared and I immediately run out of the house",
        "Before the assassination I was outside the house, having a phone-call with my daughter.",
        "I was in the buffet in the main hall. I was quite hungry and there were plenty of great foods and drinks waiting for me",
        "To be honest I was in the kitchen in my phone texting some friends. When I heard the gunshot I ran towards the living room to check with the others what happened"]
    # Shuffle to lower the risk of picking the same item twice
    random.shuffle(alibies)
    # Pick an alibi and assign it to a civilian
    alibi = str(*random.choices(alibies, weights=(12, 12, 12, 12, 12, 12, 12, 12, 12, 12), k=1))

    # Create a list and store lines about every characters alibi
    profession_lines = ["It has its own ups and downs but I can't complain I like that work.",
                        "Although it might be quite boring at times its an interesting and fun job. You get to meet plenty of people.",
                        "My father used to be a detective for 15 years. Since it payed very well and I liked it I decided to keep this profession in the family.",
                        "As a job it may not seem very compelling due to the stress and dangers that it has but I like it because I get to help a lot of people",
                        "Being a detective takes a lot of nerves and a strong stomach. It's not an easy profession"]

    # Shuffle to lower the risk of picking the same item twice
    random.shuffle(profession_lines)
    # Pick an alibi and assign it to a civilian
    pro_line = str(*random.choices(profession_lines, weights=(12, 12, 12, 12, 12), k=1))

    # Create a list and store lines about anything weird seen during the party
    w_lines = ["Well if I was to decide about it, the old sheff should be the prime suspect not us. That person seemed very nervous the hole time.",
               "I may be wrong but I think I saw someone seeking in the house about 21:40. It was a man with a black coat",
               "At some point I went to the bathroom and I heard two members of the staff whispering. It may be nothing but they seemed concerned",
               "I guess the only suspicious thing that I saw was these two guys out of the house but they were part of the security",
               "I think I saw some broken glass near the office upstairs. If you ask me they should have taken fingerprints before rushing in conclusions",
               "There was this lady that was looking at her phone the whole night. It looked like she was waiting for a phone-call or something.",
               " Well, while I was in the main hall drinking some wine, I overheard a guy talking on his phone about an important event taking place the day after",
               "If I was in charge of this investigation I would definitely start with the unknown car that was parked outside of the house"]

    # Shuffle to lower the risk of picking the same item twice
    random.shuffle(w_lines)
    # Pick an alibi and assign it to a civilian
    w_line = str(*random.choices(w_lines, weights=(12, 12, 12, 12, 12, 12, 12, 12), k=1))

    # Return all info to the appropriate character class
    return reliability, health, char, role, pic, hair, eyes, item, story, alibi, pro_line, w_line


# Create the doctor character
# It works with the same logic as the create_civilians function
def create_doctor():
    temp = []
    file = open("names.txt", "r")
    lines = file.readlines()
    name = lines[random.randint(0, len(lines) - 1)][:-1]
    char = name
    file.close()

    with open("male_names.txt", "r") as file:
        file.seek(0)  # set position to start of file
        lines = file.read().splitlines()  # now we won't have those newlines
        if char in lines:
            pics = ("ascii/male_one.txt", "ascii/male_two.txt", "ascii/male_three.txt",
                    "ascii/male_four.txt", "ascii//male_five.txt", "ascii//male_six.txt",
                    "ascii//male_seven.txt", "ascii/male_eight.txt", "ascii/male_nine.txt")
            pick_choice = str(*random.choices(pics, weights=(12, 12, 12, 12, 12, 12, 12, 12, 12), k=1))

        else:
            # write to file
            pics = ("ascii/female_one.txt", "ascii/female_two.txt", "ascii/female_three.txt",
                    "ascii/female_four.txt", "ascii/female_five.txt", "ascii/female_six.txt",
                    "ascii/female_seven.txt", "ascii/female_eight.txt", "ascii/female_nine.txt")
            pick_choice = str(*random.choices(pics, weights=(12, 12, 12, 12, 12, 12, 12, 12, 12), k=1))

    pic = pick_choice

    health = 100
    reliability = random.randint(50, 100)
    role = "Doctor"

    hair_colors = ["blue", "brown", "black", "green", "grey", "white", "blonde"]
    hair = str(*random.choices(hair_colors, weights=(12, 12, 12, 12, 12, 12, 12), k=1))

    eye_colors = ["blue", "brown", "black", "green", "grey", "white", "blonde"]
    eyes = str(*random.choices(eye_colors, weights=(12, 12, 12, 12, 12, 12, 12), k=1))

    items = ["book", "smartphone", "wallet", "watch", "hair brush", "makeup set", "pen", "pack of tissues",
             "plastic duck", "protein bar", "small sandwich", "power-bank", "swiss army knife", "flashlight"]
    item = str(*random.choices(items, weights=(12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12)))

    # Create a list and store lines about every characters connection with uncle Ben
    stories = [
        "I knew Ben since we where kids. We grew up in the same neighbourhood and kept in touch all these years.",
        "We used to go to the same school and even work part time in the same place when we were teenagers",
        "I didn't know him very well to be honest. My brother used to work with him in a business of sorts so ",
        "I got the chance to get to know him a bit but besides that we didn't speak much",
        "Together with Ben we served in the military for two years. Since then we were good friends. He was a good man ",
        "With Ben we worked on the same company for several years. Then he came one day and said that he decided to take a risk and start a business of his own",
        "I have been helping Ben with his taxes for the last five years. Ever since he started his own business he needed all the help that he could get",
        "I met Ben when I first came to the town in search of work. He introduced me to one of his friends that own a convenience store a few blocks from here"]

    # Shuffle to lower the risk of picking the same item twice
    random.shuffle(stories)
    # Pick a random story and assign it to a civilian
    story = str(*random.choices(stories, weights=(12, 12, 12, 12, 12, 12, 12, 12), k=1))

    # Create a list and store lines about every characters alibi
    alibies = [
        "Before the assassination happened I was in the staff room trying to clean my clothes. I was drinking some wine you see and I had a small accident.",
        "I was downstairs in the kitchen. I wanted some water and that's why I went there to get some.",
        "As far as I remember I was pretty much drunk the hole time. When I heard about the assassination I was with that detective and we had a discussion about old criminals.",
        "Well that's a bit embracing but when the police came in the house I was in the toilet. You see I had some spicy food before the party and my stomach was killing me.",
        "Before the incident I remember going outside to smoke a cigarette. Once I was done, I came back in and heard about the murder.",
        "Well I was very tired that night to be honest and I decided to sneak in one of the bedrooms and take a quick nap. Unfortunately I woke up and the police was here asking me about the murder.",
        "I was in the hallway looking at the painting when I heard a gunshot from upstairs. I was scared and I immediately run out of the house",
        "Before the assassination I was outside the house, having a phone-call with my daughter.",
        "I was in the buffet in the main hall. I was quite hungry and there were plenty of great foods and drinks waiting for me",
        "To be honest I was in the kitchen in my phone texting some friends. When I heard the gunshot I ran towards the living room to check with the others what happened"]
    # Shuffle to lower the risk of picking the same item twice
    random.shuffle(alibies)
    # Pick an alibi and assign it to a civilian
    alibi = str(*random.choices(alibies, weights=(12, 12, 12, 12, 12, 12, 12, 12, 12, 12), k=1))

    # Create a list and store lines about every characters alibi
    profession_lines = ["As a doctor you work a lot and sometimes you don't really get enough credit for your work",
                        "Although it might be very stressful at times its an amazing profession since you help people",
                        "My mother used to be a doctor as well for 22 years. I grew up learning a lot about medicine and biology and because of that I decided to become a doctor as well",
                        "As a job it may not seem very compelling due to the stress and responsibility that it needs but I like it because I get to help a lot of people",
                        "Being a doctor takes a lot and you have to put you patience above everything else"]

    # Shuffle to lower the risk of picking the same item twice
    random.shuffle(profession_lines)
    # Pick an alibi and assign it to a civilian
    pro_line = str(*random.choices(profession_lines, weights=(12, 12, 12, 12, 12), k=1))

    # Create a list and store lines about anything weird seen during the party
    w_lines = [" To be honest with you, there was a lot of noise and people all over the place that night. Nothing out of the ordinary",
               "The only suspicious thing in my opinion was that weird guy that was drinking whiskey the whole time",
               "At some point I went to the staff room to check on one of the maid that accidentally cut her hand with some glass. On the way there an old woman kept looking on her phone intensively.",
               "I guess the only suspicious thing that I saw was these two guys out of the house but they were part of the security"]

    # Shuffle to lower the risk of picking the same item twice
    random.shuffle(w_lines)
    # Pick an alibi and assign it to a civilian
    w_line = str(*random.choices(w_lines, weights=(12, 12, 12, 12), k=1))

    # Return all info to the doctor class
    return reliability, health, char, role, pic, hair, eyes, item, story, alibi, pro_line, w_line


# Open the json file and save the players data in
def save_player_info():
    # open the data file and "r" read it and check if it is all appropriately there
    game_file = open("data.json", "r")
    json_object = json.load(game_file)
    game_file.close()  # Close the file for avoiding any problem/ corrupting the data

    # Create targets for the information of the data.json file
    # There can be saved data depending on the order of the returned info from the create_x functions
    player = json_object["player"]
    player["name"] = class_data[2]
    player["reliability"] = class_data[0]
    player["role"] = class_data[3]
    player["health"] = class_data[1]

    # If all of the above is correct then open the file again but overwrite the data with new
    # data given in the beginning of the game
    game_file = open("data.json", "w")
    json.dump(json_object, game_file)
    game_file.close()


# Same logic as save_player_info function
def save_civilian_1_info():
    game_file = open("data.json", "r")
    json_object = json.load(game_file)
    game_file.close()

    civilian_1 = json_object["civilian_1"]
    civilian_1["reliability"] = civilian_data[0]
    civilian_1["health"] = civilian_data[1]
    civilian_1["name"] = civilian_data[2]
    civilian_1["role"] = civilian_data[3]
    civilian_1["category"] = civilian_data[4]
    civilian_1["picture"] = civilian_data[5]
    civilian_1["hair"] = civilian_data[6]
    civilian_1["eyes"] = civilian_data[7]
    civilian_1["item"] = civilian_data[8]
    civilian_1["story"] = civilian_data[9]
    civilian_1["alibi"] = civilian_data[10]
    civilian_1["pro_line"] = civilian_data[11]
    civilian_1["w_line"] = civilian_data[12]

    game_file = open("data.json", "w")
    json.dump(json_object, game_file)
    game_file.close()


# Same logic as save_player_info function
def save_civilian_2_info():
    game_file = open("data.json", "r")
    json_object = json.load(game_file)
    game_file.close()

    civilian_2 = json_object["civilian_2"]
    civilian_2["name"] = civilian_data[2]
    civilian_2["reliability"] = civilian_data[0]
    civilian_2["role"] = civilian_data[3]
    civilian_2["health"] = civilian_data[1]
    civilian_2["category"] = civilian_data[4]
    civilian_2["picture"] = civilian_data[5]
    civilian_2["hair"] = civilian_data[6]
    civilian_2["eyes"] = civilian_data[7]
    civilian_2["item"] = civilian_data[8]
    civilian_2["story"] = civilian_data[9]
    civilian_2["alibi"] = civilian_data[10]
    civilian_2["pro_line"] = civilian_data[11]
    civilian_2["w_line"] = civilian_data[12]

    game_file = open("data.json", "w")
    json.dump(json_object, game_file)
    game_file.close()


# Same logic as save_player_info function
def save_civilian_3_info():
    game_file = open("data.json", "r")
    json_object = json.load(game_file)
    game_file.close()

    civilian_3 = json_object["civilian_3"]
    civilian_3["name"] = civilian_data[2]
    civilian_3["reliability"] = civilian_data[0]
    civilian_3["role"] = civilian_data[3]
    civilian_3["health"] = civilian_data[1]
    civilian_3["category"] = civilian_data[4]
    civilian_3["picture"] = civilian_data[5]
    civilian_3["hair"] = civilian_data[6]
    civilian_3["eyes"] = civilian_data[7]
    civilian_3["item"] = civilian_data[8]
    civilian_3["story"] = civilian_data[9]
    civilian_3["alibi"] = civilian_data[10]
    civilian_3["pro_line"] = civilian_data[11]
    civilian_3["w_line"] = civilian_data[12]

    game_file = open("data.json", "w")
    json.dump(json_object, game_file)
    game_file.close()


# Same logic as save_player_info function
def save_civilian_4_info():
    game_file = open("data.json", "r")
    json_object = json.load(game_file)
    game_file.close()

    civilian_4 = json_object["civilian_4"]
    civilian_4["name"] = civilian_data[2]
    civilian_4["reliability"] = civilian_data[0]
    civilian_4["role"] = civilian_data[3]
    civilian_4["health"] = civilian_data[1]
    civilian_4["category"] = civilian_data[4]
    civilian_4["picture"] = civilian_data[5]
    civilian_4["hair"] = civilian_data[6]
    civilian_4["eyes"] = civilian_data[7]
    civilian_4["item"] = civilian_data[8]
    civilian_4["story"] = civilian_data[9]
    civilian_4["alibi"] = civilian_data[10]
    civilian_4["pro_line"] = civilian_data[11]
    civilian_4["w_line"] = civilian_data[12]

    game_file = open("data.json", "w")
    json.dump(json_object, game_file)
    game_file.close()


# Same logic as save_player_info function
def save_mafioso_1_info():
    game_file = open("data.json", "r")
    json_object = json.load(game_file)
    game_file.close()

    mafioso_1 = json_object["mafioso_1"]
    mafioso_1["reliability"] = mafioso_data[0]
    mafioso_1["health"] = mafioso_data[1]
    mafioso_1["name"] = mafioso_data[2]
    mafioso_1["role"] = mafioso_data[3]
    mafioso_1["weapon"] = mafioso_data[4]
    mafioso_1["picture"] = mafioso_data[5]
    mafioso_1["hair"] = mafioso_data[6]
    mafioso_1["eyes"] = mafioso_data[7]
    mafioso_1["item"] = mafioso_data[8]
    mafioso_1["real_role"] = mafioso_data[9]
    mafioso_1["story"] = mafioso_data[10]
    mafioso_1["alibi"] = mafioso_data[11]
    mafioso_1["pro_line"] = mafioso_data[12]
    mafioso_1["w_line"] = mafioso_data[13]

    game_file = open("data.json", "w")
    json.dump(json_object, game_file)
    game_file.close()


# Same logic as save_player_info function
def save_mafioso_2_info():
    game_file = open("data.json", "r")
    json_object = json.load(game_file)
    game_file.close()

    mafioso_2 = json_object["mafioso_2"]
    mafioso_2["reliability"] = mafioso_data[0]
    mafioso_2["health"] = mafioso_data[1]
    mafioso_2["name"] = mafioso_data[2]
    mafioso_2["role"] = mafioso_data[3]
    mafioso_2["weapon"] = mafioso_data[4]
    mafioso_2["picture"] = mafioso_data[5]
    mafioso_2["hair"] = mafioso_data[6]
    mafioso_2["eyes"] = mafioso_data[7]
    mafioso_2["item"] = mafioso_data[8]
    mafioso_2["real_role"] = mafioso_data[9]
    mafioso_2["story"] = mafioso_data[10]
    mafioso_2["alibi"] = mafioso_data[11]
    mafioso_2["pro_line"] = mafioso_data[12]
    mafioso_2["w_line"] = mafioso_data[13]

    game_file = open("data.json", "w")
    json.dump(json_object, game_file)
    game_file.close()


# Same logic as save_player_info function
def save_detective_info():
    game_file = open("data.json", "r")
    json_object = json.load(game_file)
    game_file.close()

    detective = json_object["detective"]
    detective["reliability"] = detective_data[0]
    detective["health"] = detective_data[1]
    detective["name"] = detective_data[2]
    detective["role"] = detective_data[3]
    detective["picture"] = detective_data[4]
    detective["hair"] = detective_data[5]
    detective["eyes"] = detective_data[6]
    detective["item"] = detective_data[7]
    detective["story"] = detective_data[8]
    detective["alibi"] = detective_data[9]
    detective["pro_line"] = detective_data[10]
    detective["w_line"] = detective_data[11]

    game_file = open("data.json", "w")
    json.dump(json_object, game_file)
    game_file.close()


# Same logic as save_player_info function
def save_doctor_info():
    game_file = open("data.json", "r")
    json_object = json.load(game_file)
    game_file.close()

    doctor = json_object["doctor"]
    doctor["reliability"] = doctor_data[0]
    doctor["health"] = doctor_data[1]
    doctor["name"] = doctor_data[2]
    doctor["role"] = doctor_data[3]
    doctor["picture"] = doctor_data[4]
    doctor["hair"] = doctor_data[5]
    doctor["eyes"] = doctor_data[6]
    doctor["item"] = doctor_data[7]
    doctor["story"] = doctor_data[8]
    doctor["alibi"] = doctor_data[9]
    doctor["pro_line"] = doctor_data[10]
    doctor["w_line"] = doctor_data[11]

    game_file = open("data.json", "w")
    json.dump(json_object, game_file)
    game_file.close()


# Print the menu in the very beginning
def print_menu():
    # Clear the screen
    os.system('cls' if os.name == 'nt' else 'clear')

    # Print Menu
    print(5 * "\n")
    print("                                +-----------------------------------------+")
    print("                                |        Mafia: The terminal game         |")
    print("                                |                                         |")
    print("                                |         1) Play                         |")
    print("                                |         2) Rules                        |")
    print("                                |         3) Mini games                   |")
    print("                                |         4) Exit                         |")
    print("                                |                                         |")
    print("                                +-----------------------------------------+")


# Call the arkanoid game with this function
# Note: Can be moved and called from an outer file.
# Since it takes one move per frame the speed is either too slow or two fast.
# Note: Rewrite and implement this and the other mini games in Pygame(?)
def spider_game():
    initscr()
    curs_set(1)   # Set to 0 if the game runs alone or 1 to make it responsive with multiple curses windows
    win = newwin(30, 50, 0, 55)
    win.keypad(True)
    win.nodelay(True)
    win.border('|', '|', '-', '-', '+', '+', '+', '+')
    ball = [10, 10]
    x = 20
    dx = dy = 1
    score = 0
    key = KEY_RIGHT
    win.timeout(100)
    for n in range(5):
        win.hline(n + 1, randrange(1, 24, 1), ord('a'), randrange(1, 24, 1))
    while key != 27:
        win.addstr(0, 2, ' Score: ' + str(score) + ' ')
        key = win.getch()
        win.hline(28, x, ord(' '), 6)
        x = (x - 1 if x - 1 > 0 else x) if key == KEY_LEFT else (x + 1 if x + 1 < 44 else x) if key == KEY_RIGHT else x
        win.hline(28, x, ord('X'), 6)
        if ball[0] < 2 or ball[0] > 47:
            dx = dx * -1
        if (ball[1] < 2 or ball[1] >= 29) or chr(win.inch(ball[1] + dy, ball[0] + dx)) in ['X', 'a']:
            if chr(win.inch(ball[1] + dy, ball[0] + dx)) == 'a':
                win.addch(ball[1] + dy, ball[0] + dx, ' ')
                score = score + 1
            dy = dy * -1
        ball[0] = ball[0] + dx
        ball[1] = ball[1] + dy
        win.addch(ball[1] - dy, ball[0] - dx, ' ')
        win.addch(ball[1], ball[0], '0')
        if ball[1] == 29:
            break
    win.clear()  # Clear and then refresh the screen
    win.refresh()

    curses.endwin()


# Call the snake game with this function
# Note: Can be moved and called from an outer file.
def snake():
    # Typical curses variables for correct syntax
    curses.initscr()
    curses.beep()
    curses.beep()
    window = curses.newwin(HEIGHT, WIDTH, 4, 50)
    window.timeout(TIMEOUT)
    # If keypad is set to [0/1] as advised from the curses documentation it sometimes returns a warning but it is
    # correct. Instead of [0/1] [False/True] can do the trick to clear Pycharm warnings
    window.keypad(True)
    curses.noecho()
    curses.curs_set(1)
    window.border(0)

    snake_a = Snake(SNAKE_X, SNAKE_Y, window)
    food = Food(window, '*')

    while True:
        window.clear()
        window.border(0)
        snake_a.render()
        food.render()

        window.addstr(0, 5, snake_a.score)
        event = window.getch()

        # Below set some parameters for the game

        # Event = window.Ketch if == 27 break
        if event == 27:
            break

        # This allows the snake direction. if saved and ran here, snake can change direction, but cannot eat food
        if event in [KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT]:
            snake_a.change_direction(event)

        # With this the snake eats food, and then it resets. [See line 50]
        if snake_a.head.x == food.x and snake_a.head.y == food.y:
            snake_a.eat_food(food)

        if event == 32:
            key = -1
            while key != 32:
                key = window.getch()

        snake_a.update()
        # if snake collides from function on line 60, then break.
        if snake_a.collided:
            break

    window.clear()  # Clear and then refresh the screen
    window.refresh()
    curses.endwin()


# Store the whole tetris game in a function so it can be called fast every time
# It can be move in separate file for decreasing this files length
def tetris():
    # Initialise the curses window
    curses.initscr()
    curses.curs_set(1)  # Set to 0 if the game runs alone or 1 to make it responsive with multiple curses windows
    win = curses.newwin(18, 18, 4, 65)  # Create window and draw border
    win.keypad(True)  # This returns a warning but it is correct based on the curses documentation
    win.nodelay(True)  # Use 0 to enable no-delay & keypad and 1 to disable it
    f = [[0x315, 0x4cd, 0x13f, 0xc47], [0x31d, 0x4cf, 0x137, 0xc45], [0x374, 0x374, 0x374, 0x374],
         [0x741, 0x51c, 0xdc3, 0xf34],
         [0xfc1, 0x73c, 0x543, 0xd14], [0x311, 0x4cc, 0x133, 0xc44], [0xc34, 0x341, 0x41c, 0x1c3]]

    # Detect if there is a collision between shapes or game borders
    def chk_fig(crds, s):
        chk = all([win.inch(c[1], c[0]) & 255 == 32 for c in crds])
        for c in crds:
            win.addch(c[1], c[0], 'X' if s == 1 else 32) if ((chk and s == 1) or s == 0) else None
        return True if s == 0 else chk

    def put_fig(fp, s):  # decode and put figure on the screen
        c = lambda el, n: -1 if (n >> el & 3) == 3 else 1 if (n >> el & 3) == 1 else 0
        pos = [c(i, f[fp[3]][fp[2]]) for i in range(0, 15, 2)[::-1]]
        return chk_fig([list(map(lambda x, y: x + y, fp[0:2] * 4, pos))[i - 2:i] for i in range(2, 9, 2)], s)

    def move_fig(fp, key, d):  # figure moving function
        fp[0] = fp[0] - d if key == curses.KEY_LEFT else fp[0] + d if key == curses.KEY_RIGHT else fp[0]
        fp[1] = fp[1] + d if key in [curses.KEY_DOWN, -1] else fp[1]
        if key == curses.KEY_UP:
            fp[2] = 0 if fp[2] + d > 3 else 3 if fp[2] + d < 0 else fp[2] + d

    # When a line is full then increase users score by one
    def chk_board(score):
        for i in range(17):
            if all([chr(win.inch(i, x)) == 'X' for x in range(1, 17)]):
                win.deleteln()
                win.move(1, 1)
                win.insertln()
                score = score + 1
                if score % 10 == 0:
                    win.timeout(300 - (score * 2))
        return score

    # change the rotation of each shape
    FigPos = [8, 3, 0, randrange(0, 6, 1)]
    score = put_fig(FigPos, 1) ^ 1
    win.timeout(300)
    # Start loop for falling shapes and deleting/adding rows and detecting coalitions
    while 1:
        win.border('|', '|', '-', '-', '+', '+', '+', '+')
        win.addstr(0, 2, ' Score: ' + str(score) + ' ')
        key = win.getch()
        if key == 27:
            break
        put_fig(FigPos, 0)
        move_fig(FigPos, key, 1)
        if not put_fig(FigPos, 1):
            move_fig(FigPos, key, -1)
            put_fig(FigPos, 1)
            if FigPos[1] == 3:
                break
            if key in [curses.KEY_DOWN, -1]:
                score = chk_board(score)
                FigPos = [8, 3, 0, randrange(0, 6, 1)]
                put_fig(FigPos, 1)

    win.clear()  # Clear and then refresh the screen
    win.refresh()
    curses.endwin()  # close the window


def main_menu():
    loop = True

    while loop:  # While loop that allows user to choose something from the menu
        os.system('cls' if os.name == 'nt' else 'clear')
        print_menu()  # Display everything inside print_menu
        key = input("                                 Pick an option [1-4]:")

        # If user presses 1 then break all loops and start the character creation function
        if key == "1":
            os.system('cls' if os.name == 'nt' else 'clear')
            loop = False
        # If user presses 2 then show the rules and objectives
        elif key == "2":
            os.system('cls' if os.name == 'nt' else 'clear')
            print(5 * "\n")
            print("                      +-----------------------------------------+")
            print("                      |        Mafia: The terminal game         |")
            print("                      |                                         |")
            print("                      | Objective: Your objective is to find    |")
            print("                      | the mafioso or Kill all other players   |")
            print("                      | Game Tips: Remember the player names    |")
            print("                      | How to play: Once possible speak with   |")
            print("                      | all players and then vote/kill someone  |")
            print("                      +-----------------------------------------+")
            input("                            Back to menu [Press Enter]:")
        # If user presses 3 then show the mini-games options
        elif key == "3":
            # Secondary loop for letting the player play any game unlimited times until the loop stops.
            looper = True
            while looper:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(5 * "\n")
                print("                             +-----------------------------------------+")
                print("                             |        Mafia: The terminal game         |")
                print("                             |                                         |")
                print("                             |   1) Play snake          [1]            |")
                print("                             |   2) Play Arkanoid       [2]            |")
                print("                             |   3) Play Tetris         [3]            |")
                print("                             |   4) Back to menu        [4]            |")
                print("                             |                                         |")
                print("                             +-----------------------------------------+")
                key = input("                              Pick an option [1-4]:")
                if key == "1":
                    # Start the snake game from the function above
                    # Once done let the secondary loop restart in case the player wants to play again
                    snake()
                elif key == "2":
                    # Start the arkanoid game from the function above
                    # Once done let the secondary loop restart in case the player wants to play again
                    spider_game()
                elif key == "3":
                    # Start the Tetris game from the function above
                    # Once done let the secondary loop restart in case the player wants to play again
                    tetris()
                elif key == "4":
                    looper = False
                else:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(5 * "\n")
                    print("                             +-----------------------------------------+")
                    print("                             |        Mafia: The terminal game         |")
                    print("                             |                                         |")
                    print("                             |     Invalid input please try again!     |")
                    print("                             |                                         |")
                    print("                             |                                         |")
                    print("                             |                                         |")
                    print("                             |                                         |")
                    print("                             +-----------------------------------------+")
                    time.sleep(2)
        # If user presses 4 then end the game with quit()
        elif key == "4":
            os.system('cls' if os.name == 'nt' else 'clear')
            print(5 * "\n")
            print("                         +-----------------------------------------+")
            print("                         |        Mafia: The terminal game         |")
            print("                         |                                         |")
            print("                         |                                         |")
            print("                         |    The program will shortly shutdown!   |")
            print("                         |                                         |")
            print("                         |                                         |")
            print("                         |                                         |")
            print("                         +-----------------------------------------+")
            print("                              The program will shortly shutdown!")
            loop = False  # End the loop
            time.sleep(1)
            quit()


# Call the menu function to start the game
# Note: Could be run directly with if __name__ == "__main__" in the future
main_menu()


active_players = []  # Store the active players here. Use list so its easily access and later change data.

# Get number of elements in the list
# Can be used/is used in the main_game.py to check if the game must go on or end
total_players = len(active_players)

class_data = create_char()  # store the info into a list so its easier to transfer all in the PlayerClass later on
main_player = Player(class_data[0], class_data[1], class_data[2], class_data[3])  # Player object is created
save_player_info()  # Player object is stored within a json dictionary [data.json]

# Check what is the users role and create the appropriate Enemies to play with
if class_data[3] == "Mafioso":
    active_players.append(main_player.role)
    # Generate a doc, a detective, one other mafioso and four civilians
    civilian_data = create_civilians()
    civilian_1 = Civilians(civilian_data[0], civilian_data[1], civilian_data[2], civilian_data[3], civilian_data[4],
                           civilian_data[5], civilian_data[6], civilian_data[7], civilian_data[8], civilian_data[9],
                           civilian_data[10], civilian_data[11], civilian_data[12])
    save_civilian_1_info()
    active_players.append(civilian_1.category)

    civilian_data = create_civilians()
    civilian_2 = Civilians(civilian_data[0], civilian_data[1], civilian_data[2], civilian_data[3], civilian_data[4],
                           civilian_data[5], civilian_data[6], civilian_data[7], civilian_data[8], civilian_data[9],
                           civilian_data[10], civilian_data[11], civilian_data[12])
    save_civilian_2_info()
    active_players.append(civilian_2.category)

    civilian_data = create_civilians()
    civilian_3 = Civilians(civilian_data[0], civilian_data[1], civilian_data[2], civilian_data[3], civilian_data[4],
                           civilian_data[5], civilian_data[6], civilian_data[7], civilian_data[8], civilian_data[9],
                           civilian_data[10], civilian_data[11], civilian_data[12])
    save_civilian_3_info()
    active_players.append(civilian_3.category)

    civilian_data = create_civilians()
    civilian_4 = Civilians(civilian_data[0], civilian_data[1], civilian_data[2], civilian_data[3], civilian_data[4],
                           civilian_data[5], civilian_data[6], civilian_data[7], civilian_data[8], civilian_data[9],
                           civilian_data[10], civilian_data[11], civilian_data[12])
    save_civilian_4_info()
    active_players.append(civilian_4.category)

    mafioso_data = create_mafia()
    mafioso_1 = Mafia(mafioso_data[0], mafioso_data[1], mafioso_data[2], mafioso_data[3], mafioso_data[4],
                      mafioso_data[5], mafioso_data[6], mafioso_data[7], mafioso_data[8], mafioso_data[9],
                      mafioso_data[10], mafioso_data[11], mafioso_data[12], mafioso_data[13])
    save_mafioso_1_info()
    active_players.append(mafioso_1.role)

    detective_data = create_detective()
    detective = Detective(detective_data[0], detective_data[1], detective_data[2], detective_data[3], detective_data[4],
                          detective_data[5], detective_data[6], detective_data[7], detective_data[8], detective_data[9],
                          detective_data[10], detective_data[11])
    save_detective_info()
    active_players.append(detective.role)

    doctor_data = create_doctor()
    doctor = Doctor(doctor_data[0], doctor_data[1], doctor_data[2], doctor_data[3], doctor_data[4], doctor_data[5],
                    doctor_data[6], doctor_data[7], doctor_data[8], doctor_data[9], doctor_data[10], doctor_data[11])
    save_doctor_info()
    active_players.append(doctor.role)
elif class_data[3] == "Doctor":
    active_players.append(main_player.role)
    # Generate a detective, two other mafioso and four civilians

    civilian_data = create_civilians()
    civilian_1 = Civilians(civilian_data[0], civilian_data[1], civilian_data[2], civilian_data[3], civilian_data[4],
                           civilian_data[5], civilian_data[6], civilian_data[7], civilian_data[8], civilian_data[9],
                           civilian_data[10], civilian_data[11], civilian_data[12])
    save_civilian_1_info()
    active_players.append(civilian_1.category)

    civilian_data = create_civilians()
    civilian_2 = Civilians(civilian_data[0], civilian_data[1], civilian_data[2], civilian_data[3], civilian_data[4],
                           civilian_data[5], civilian_data[6], civilian_data[7], civilian_data[8], civilian_data[9],
                           civilian_data[10], civilian_data[11], civilian_data[12])
    save_civilian_2_info()
    active_players.append(civilian_2.category)

    civilian_data = create_civilians()
    civilian_3 = Civilians(civilian_data[0], civilian_data[1], civilian_data[2], civilian_data[3], civilian_data[4],
                           civilian_data[5], civilian_data[6], civilian_data[7], civilian_data[8], civilian_data[9],
                           civilian_data[10], civilian_data[11], civilian_data[12])
    save_civilian_3_info()
    active_players.append(civilian_3.category)

    civilian_data = create_civilians()
    civilian_4 = Civilians(civilian_data[0], civilian_data[1], civilian_data[2], civilian_data[3], civilian_data[4],
                           civilian_data[5], civilian_data[6], civilian_data[7], civilian_data[8], civilian_data[9],
                           civilian_data[10], civilian_data[11], civilian_data[12])
    save_civilian_4_info()
    active_players.append(civilian_4.category)

    mafioso_data = create_mafia()
    mafioso_1 = Mafia(mafioso_data[0], mafioso_data[1], mafioso_data[2], mafioso_data[3], mafioso_data[4],
                      mafioso_data[5], mafioso_data[6], mafioso_data[7], mafioso_data[8], mafioso_data[9],
                      mafioso_data[10], mafioso_data[11], mafioso_data[12], mafioso_data[13])
    save_mafioso_1_info()
    active_players.append(mafioso_1.role)

    mafioso_data = create_mafia()
    mafioso_2 = Mafia(mafioso_data[0], mafioso_data[1], mafioso_data[2], mafioso_data[3], mafioso_data[4],
                      mafioso_data[5], mafioso_data[6], mafioso_data[7], mafioso_data[8], mafioso_data[9],
                      mafioso_data[10], mafioso_data[11], mafioso_data[12], mafioso_data[13])
    save_mafioso_2_info()
    active_players.append(mafioso_2.role)

    detective_data = create_detective()
    detective = Detective(detective_data[0], detective_data[1], detective_data[2], detective_data[3], detective_data[4],
                          detective_data[5], detective_data[6], detective_data[7], detective_data[8], detective_data[9],
                          detective_data[10], detective_data[11])
    save_detective_info()
    active_players.append(detective.role)
elif class_data[3] == "Detective":
    active_players.append(main_player.role)
    # Generate a doc, two other mafioso and four civilians

    civilian_data = create_civilians()
    civilian_1 = Civilians(civilian_data[0], civilian_data[1], civilian_data[2], civilian_data[3], civilian_data[4],
                           civilian_data[5], civilian_data[6], civilian_data[7], civilian_data[8], civilian_data[9],
                           civilian_data[10], civilian_data[11], civilian_data[12])
    save_civilian_1_info()
    active_players.append(civilian_1.category)

    civilian_data = create_civilians()
    civilian_2 = Civilians(civilian_data[0], civilian_data[1], civilian_data[2], civilian_data[3], civilian_data[4],
                           civilian_data[5], civilian_data[6], civilian_data[7], civilian_data[8], civilian_data[9],
                           civilian_data[10], civilian_data[11], civilian_data[12])
    save_civilian_2_info()
    active_players.append(civilian_2.category)

    civilian_data = create_civilians()
    civilian_3 = Civilians(civilian_data[0], civilian_data[1], civilian_data[2], civilian_data[3], civilian_data[4],
                           civilian_data[5], civilian_data[6], civilian_data[7], civilian_data[8], civilian_data[9],
                           civilian_data[10], civilian_data[11], civilian_data[12])
    save_civilian_3_info()
    active_players.append(civilian_3.category)

    civilian_data = create_civilians()
    civilian_4 = Civilians(civilian_data[0], civilian_data[1], civilian_data[2], civilian_data[3], civilian_data[4],
                           civilian_data[5], civilian_data[6], civilian_data[7], civilian_data[8], civilian_data[9],
                           civilian_data[10], civilian_data[11], civilian_data[12])
    save_civilian_4_info()
    active_players.append(civilian_4.category)

    mafioso_data = create_mafia()
    mafioso_1 = Mafia(mafioso_data[0], mafioso_data[1], mafioso_data[2], mafioso_data[3], mafioso_data[4],
                      mafioso_data[5], mafioso_data[6], mafioso_data[7], mafioso_data[8], mafioso_data[9],
                      mafioso_data[10], mafioso_data[11], mafioso_data[11], mafioso_data[13])
    save_mafioso_1_info()
    active_players.append(mafioso_1.role)

    mafioso_data = create_mafia()
    mafioso_2 = Mafia(mafioso_data[0], mafioso_data[1], mafioso_data[2], mafioso_data[3], mafioso_data[4],
                      mafioso_data[5], mafioso_data[6], mafioso_data[7], mafioso_data[8], mafioso_data[9],
                      mafioso_data[10], mafioso_data[11], mafioso_data[11], mafioso_data[13])
    save_mafioso_2_info()
    active_players.append(mafioso_2.role)

    doctor_data = create_doctor()
    doctor = Doctor(doctor_data[0], doctor_data[1], doctor_data[2], doctor_data[3], doctor_data[4], doctor_data[5],
                    doctor_data[6], doctor_data[7], doctor_data[8], doctor_data[9], doctor_data[10], doctor_data[11])
    save_doctor_info()
    active_players.append(doctor.role)
