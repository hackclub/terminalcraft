import curses
import time
import menu
from curses import wrapper
import random
from random import randint
from random import randrange
from curses import initscr, curs_set, newwin, KEY_RIGHT, KEY_LEFT, KEY_DOWN, KEY_UP

# Set most important pictures in variables that will be accessed during the game
# For optimizing the code create a class for [rooms/game_objects/cutscenes] in the future

# Cutscenes
ten_minutes_later = "cutscenes/ten_minutes_later.txt"
officer_one = "cutscenes/officer_one.txt"
one_hour_later = "cutscenes/one_hour_later.txt"
game_over = "cutscenes/game_over.txt"
tv = "cutscenes/tv_news.txt"
store = "cutscenes/store.txt"
mafia_run = "cutscenes/mafia_run.txt"
mafia_run_two = "cutscenes/mafia_run_two.txt"
uncle = "cutscenes/ben.txt"
springfield = "cutscenes/springfield.txt"
bomb = "cutscenes/bomb.txt"
raid = "cutscenes/raid.txt"
hooded_person = "cutscenes/hooded_person.txt"
run = "cutscenes/run.txt"
town_two = "cutscenes/town_two.txt"
later = "cutscenes/later.txt"
ben_two = "cutscenes/ben_two.txt"

# rooms
maf_room = "rooms/maf_room.txt"
kitchen = "rooms/kitchen.txt"
hall = "rooms/hall.txt"
room_1 = "rooms/room_1.txt"
living_room = "rooms/living_room.txt"
room_O = "rooms/room_O.txt"
staff_room = "rooms/staff_room.txt"
b_office = "rooms/b_office.txt"
entrance = "rooms/entrance.txt"
default = "rooms/default.txt"
corridor = "rooms/empty_corridor.txt"
b2r = "rooms/b2r.txt"
base = "rooms/base.txt"
fence = "rooms/fence.txt"
house_out = "rooms/house_outdoor.txt"
house_hall = "rooms/house_hall.txt"
base_room = "rooms/base_room.txt"

# Game objects
maf_gun = "game_objects/maf_gun.txt"
transition = "game_objects/transition.txt"
fireplace = "game_objects/drawer.txt"
painting = "game_objects/painting.txt"
bookshelf = "game_objects/librarry.txt"
safe = "game_objects/safe.txt"
desk = "game_objects/desk.txt"
papper = "game_objects/papper.txt"
arcade = "game_objects/arcade.txt"
s_screen = "game_objects/screen.txt"
security_safe = "game_objects/security_safe.txt"
diary = "game_objects/diary.txt"
transition_two = "game_objects/transition_two.txt"
transition_three = "game_objects/transition_three.txt"
invitation = "game_objects//invitation.txt"
envelope = "game_objects/envelope.txt"

# Ascii files
mafia_the_t_g = "ascii/mafia_the_t_g.txt"
mafia_mode = "ascii/mafia_mode.txt"
house = 'ascii/house.txt'
police = "ascii//police.txt"
old_woman = "ascii/old_woman.txt"
mafioso = "ascii/mafioso.txt"
gun = "ascii/gun.txt"
landscape = 'ascii/landscape.txt'
man_npc = "ascii/man.txt"
town = "ascii//town.txt"
player = 'ascii/player.txt'
male_v = "ascii//male_five.txt"
male_VI = "ascii//male_six.txt"

night = "Night"
day = "Day"

# Last minute change of the name and picture of civilian 4
# Change the variables so they pass better on the script bellow
menu.civilian_4.set_name(new_name="Amanda")
menu.civilian_4.set_picture(new_picture="ascii/female_three.txt")

# Set the variables for the snake game
# At some point the player can play various mini-games
# Capitalize all letters for proper curses syntax
WIDTH = 40
HEIGHT = 16
MAX_X = WIDTH - 2
MAX_Y = HEIGHT - 2
SNAKE_LENGTH = 5
SNAKE_X = SNAKE_LENGTH + 1
SNAKE_Y = 3
TIMEOUT = 100


# Create a snake with info about: Its movement, behavior etc.
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

    def eat_food(self, food):
        food.reset()
        body = Body(self.last_head_coor[0], self.last_head_coor[1])
        self.body_list.insert(-1, body)
        self.hit_score += 1
        if self.hit_score % 3 == 0:
            self.timeout -= 5
            self.window.timeout(self.timeout)

    @property
    def collided(self):
        return any([body.coor == self.head.coor
                    for body in self.body_list[:-1]])

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


# Call the snake game with this function
# Note: Can be moved and called from an outer file.
def snake():
    # Typical curses variables for correct syntax
    curses.initscr()
    curses.beep()
    curses.beep()
    window = curses.newwin(HEIGHT, WIDTH, 4, 50)
    window.timeout(TIMEOUT)
    window.keypad(True)
    curses.noecho()
    curses.curs_set(1)  # Set to 0 if the game runs alone or 1 to make it responsive with multiple curses windows
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


# Call the snake game with this function
# Note: Can be moved and called from an outer file.
# Since it takes one move per frame the movement is either too slow or two fast.
# Note: Rewrite and implement this and the other mini games in Pygame
def spider_game():
    initscr()
    curs_set(1)  # Set to 0 if the game runs alone or 1 to make it responsive with multiple curses windows
    win = newwin(30, 50, 0, 52)
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


def main(stdscr):
    inventory = []
    # Set a variable for the players reliability during the game
    # Depending on the players actions the number will increase and decrease
    pl_rel = menu.main_player.reliability

    # Set a variable for the players health during the game.
    # Depending on the players actions the number will increase and decrease
    pl_hel = menu.main_player.health

    # Opening will be used only once in order to display the invitation to the player.
    # x = Slow print any given text, y = show invitation, z = display Empty name, r = display empty, t = Time
    def opening(x, y, z, r, t):
        # Print a box for the pictures shown in the game
        stdscr.clear()
        stdscr.refresh()
        stdscr.addstr(2, 28, "+--------------------------------------------------------------------------------------+")
        stdscr.addstr(3, 28, "|                                                                                      |")
        stdscr.addstr(4, 28, "|                                                                                      |")
        stdscr.addstr(5, 28, "|                                                                                      |")
        stdscr.addstr(6, 28, "|                                                                                      |")
        stdscr.addstr(7, 28, "|                                                                                      |")
        stdscr.addstr(8, 28, "|                                                                                      |")
        stdscr.addstr(9, 28, "|                                                                                      |")
        stdscr.addstr(10, 28,
                      "|                                                                                      |")
        stdscr.addstr(11, 28,
                      "|                                                                                      |")
        stdscr.addstr(12, 28,
                      "|                                                                                      |")
        stdscr.addstr(13, 28,
                      "|                                                                                      |")
        stdscr.addstr(14, 28,
                      "|                                                                                      |")
        stdscr.addstr(15, 28,
                      "|                                                                                      |")
        stdscr.addstr(16, 28,
                      "|                                                                                      |")
        stdscr.addstr(17, 28,
                      "|                                                                                      |")
        stdscr.addstr(18, 28,
                      "|                                                                                      |")
        stdscr.addstr(19, 28,
                      "|                                                                                      |")
        stdscr.addstr(20, 28,
                      "|                                                                                      |")
        stdscr.addstr(21, 28,
                      "|                                                                                      |")
        stdscr.addstr(22, 28,
                      "+--------------------------------------------------------------------------------------+")

        stdscr.addstr(2, 117, "+----------------------------------------+")
        stdscr.addstr(3, 117, "|               Game info                |")
        stdscr.addstr(4, 117, "|                                        |")
        stdscr.addstr(5, 117, "|                                        |")
        stdscr.addstr(6, 117, "|                                        |")
        stdscr.addstr(7, 117, "|                                        |")
        stdscr.addstr(8, 117, "|                                        |")
        stdscr.addstr(9, 117, "|                                        |")
        stdscr.addstr(10, 117, "|                                        |")
        stdscr.addstr(11, 117, "+----------------------------------------+")

        stdscr.addstr(12, 117, "+----------------------------------------+")
        stdscr.addstr(13, 117, "|               Inventory                |")
        stdscr.addstr(14, 117, "|                                        |")
        stdscr.addstr(15, 117, "|                                        |")
        stdscr.addstr(16, 117, "|                                        |")
        stdscr.addstr(17, 117, "|                                        |")
        stdscr.addstr(18, 117, "|                                        |")
        stdscr.addstr(19, 117, "|                                        |")
        stdscr.addstr(20, 117, "|                                        |")
        stdscr.addstr(21, 117, "|                                        |")
        stdscr.addstr(22, 117, "+----------------------------------------+")

        # Show the name of the NPC that speaks
        stdscr.addstr(23, 29, f"Talking with:  {z}               Reliability:  {r}", curses.A_BOLD)
        stdscr.refresh()

        # Print the dialogue box
        stdscr.addstr(24, 28,
                      "+--------------------------------------------------------------------------------------+",
                      curses.A_BOLD)
        stdscr.addstr(25, 28,
                      "|                                                                                      |",
                      curses.A_BOLD)
        stdscr.addstr(26, 28,
                      "|                                                                                      |",
                      curses.A_BOLD)
        stdscr.addstr(27, 28,
                      "|                                                                                      |",
                      curses.A_BOLD)
        stdscr.addstr(28, 28,
                      "|                                                                                      |",
                      curses.A_BOLD)
        stdscr.addstr(29, 28,
                      "+--------------------------------------------------------------------------------------+",
                      curses.A_BOLD)
        stdscr.refresh()

        # Create the window and set (text rows, character limit, y,x coordinates for the window)
        pic_win = curses.newwin(19, 77, 3, 29)
        z = open(f"{y}", "r")
        pic_win.addstr(z.read())
        pic_win.refresh()
        z.close()

        # in this window the user can see the current health and reliability
        op_win = curses.newwin(5, 30, 4, 119)
        op_win.addstr(
            f"\nPlayers Reliability: {pl_rel}\nPlayers health: {pl_hel}"
            f"\nTime:{t}")
        op_win.refresh()

        # Create the special window that will display the name of the user inside an ascii picture early on the game
        op_win = curses.newwin(1, 20, 6, 45)
        op_win.addstr(f"{menu.main_player.name}")
        op_win.refresh()

        # Create the window and set (text rows, character limit, y,x coordinates for the window)
        text_win = curses.newwin(4, 60, 25, 30)

        # Take a given sentence and print all letters within it one by one.
        for i in x:
            text_win.addstr(f"{i}", curses.A_BOLD)
            text_win.refresh()
            time.sleep(0.07)

        # Ask for any input and clear the box
        stdscr.addstr(28, 88, f"Press any key to continue!", curses.A_BOLD)
        stdscr.getch()

    # Function activates only if the player a) Meets with Veronica and b) took the mysterious paper from the Ben's house
    def reveal(x, y, z, r, t):
        # Print a box for the pictures shown in the game
        stdscr.clear()
        stdscr.refresh()
        stdscr.addstr(2, 28, "+--------------------------------------------------------------------------------------+")
        stdscr.addstr(3, 28, "|                                                                                      |")
        stdscr.addstr(4, 28, "|                                                                                      |")
        stdscr.addstr(5, 28, "|                                                                                      |")
        stdscr.addstr(6, 28, "|                                                                                      |")
        stdscr.addstr(7, 28, "|                                                                                      |")
        stdscr.addstr(8, 28, "|                                                                                      |")
        stdscr.addstr(9, 28, "|                                                                                      |")
        stdscr.addstr(10, 28,
                      "|                                                                                      |")
        stdscr.addstr(11, 28,
                      "|                                                                                      |")
        stdscr.addstr(12, 28,
                      "|                                                                                      |")
        stdscr.addstr(13, 28,
                      "|                                                                                      |")
        stdscr.addstr(14, 28,
                      "|                                                                                      |")
        stdscr.addstr(15, 28,
                      "|                                                                                      |")
        stdscr.addstr(16, 28,
                      "|                                                                                      |")
        stdscr.addstr(17, 28,
                      "|                                                                                      |")
        stdscr.addstr(18, 28,
                      "|                                                                                      |")
        stdscr.addstr(19, 28,
                      "|                                                                                      |")
        stdscr.addstr(20, 28,
                      "|                                                                                      |")
        stdscr.addstr(21, 28,
                      "|                                                                                      |")
        stdscr.addstr(22, 28,
                      "+--------------------------------------------------------------------------------------+")

        stdscr.addstr(2, 117, "+----------------------------------------+")
        stdscr.addstr(3, 117, "|               Game info                |")
        stdscr.addstr(4, 117, "|                                        |")
        stdscr.addstr(5, 117, "|                                        |")
        stdscr.addstr(6, 117, "|                                        |")
        stdscr.addstr(7, 117, "|                                        |")
        stdscr.addstr(8, 117, "|                                        |")
        stdscr.addstr(9, 117, "|                                        |")
        stdscr.addstr(10, 117, "|                                        |")
        stdscr.addstr(11, 117, "+----------------------------------------+")

        stdscr.addstr(12, 117, "+----------------------------------------+")
        stdscr.addstr(13, 117, "|               Inventory                |")
        stdscr.addstr(14, 117, "|                                        |")
        stdscr.addstr(15, 117, "|                                        |")
        stdscr.addstr(16, 117, "|                                        |")
        stdscr.addstr(17, 117, "|                                        |")
        stdscr.addstr(18, 117, "|                                        |")
        stdscr.addstr(19, 117, "|                                        |")
        stdscr.addstr(20, 117, "|                                        |")
        stdscr.addstr(21, 117, "|                                        |")
        stdscr.addstr(22, 117, "+----------------------------------------+")

        # Show the name of the NPC that speaks
        stdscr.addstr(23, 29, f"Talking with:  {z}               Reliability:  {r}", curses.A_BOLD)
        stdscr.refresh()

        # Print the dialogue box
        stdscr.addstr(24, 28,
                      "+--------------------------------------------------------------------------------------+",
                      curses.A_BOLD)
        stdscr.addstr(25, 28,
                      "|                                                                                      |",
                      curses.A_BOLD)
        stdscr.addstr(26, 28,
                      "|                                                                                      |",
                      curses.A_BOLD)
        stdscr.addstr(27, 28,
                      "|                                                                                      |",
                      curses.A_BOLD)
        stdscr.addstr(28, 28,
                      "|                                                                                      |",
                      curses.A_BOLD)
        stdscr.addstr(29, 28,
                      "+--------------------------------------------------------------------------------------+",
                      curses.A_BOLD)
        stdscr.refresh()

        # Create the window and set (text rows, character limit, y,x coordinates for the window)
        pic_win = curses.newwin(19, 77, 3, 29)
        z = open(f"{y}", "r")
        pic_win.addstr(z.read())
        pic_win.refresh()
        z.close()

        op_win = curses.newwin(5, 30, 4, 119)
        op_win.addstr(
            f"\nPlayers Reliability: {menu.main_player.reliability}\nPlayers health: {menu.main_player.health}"
            f"\nTime:{t}")
        op_win.refresh()

        op_win = curses.newwin(2, 20, 10, 39)
        op_win.addstr(f"{menu.mafioso_1.name} is a ")
        op_win.addstr(f"mafioso....")
        op_win.refresh()

        # Create the window and set (text rows, character limit, y,x coordinates for the window)
        text_win = curses.newwin(4, 60, 25, 30)

        # Take a given sentence and print all letters within it one by one.
        for i in x:
            text_win.addstr(f"{i}", curses.A_BOLD)
            text_win.refresh()
            time.sleep(0.07)

        # Ask for any input and clear the box
        stdscr.addstr(28, 88, f"Press any key to continue!", curses.A_BOLD)
        stdscr.getch()

    # UI takes care of the games screen and stats
    # x = Slow print any given text, y = show picture, z = display NPCs' name, r = NPC reliability, t = Time
    def ui(x, y, z, r, t, i):
        # Print a box for the pictures shown in the game
        stdscr.clear()
        stdscr.refresh()
        stdscr.addstr(2, 28, "+--------------------------------------------------------------------------------------+")
        stdscr.addstr(3, 28, "|                                                                                      |")
        stdscr.addstr(4, 28, "|                                                                                      |")
        stdscr.addstr(5, 28, "|                                                                                      |")
        stdscr.addstr(6, 28, "|                                                                                      |")
        stdscr.addstr(7, 28, "|                                                                                      |")
        stdscr.addstr(8, 28, "|                                                                                      |")
        stdscr.addstr(9, 28, "|                                                                                      |")
        stdscr.addstr(10, 28,
                      "|                                                                                      |")
        stdscr.addstr(11, 28,
                      "|                                                                                      |")
        stdscr.addstr(12, 28,
                      "|                                                                                      |")
        stdscr.addstr(13, 28,
                      "|                                                                                      |")
        stdscr.addstr(14, 28,
                      "|                                                                                      |")
        stdscr.addstr(15, 28,
                      "|                                                                                      |")
        stdscr.addstr(16, 28,
                      "|                                                                                      |")
        stdscr.addstr(17, 28,
                      "|                                                                                      |")
        stdscr.addstr(18, 28,
                      "|                                                                                      |")
        stdscr.addstr(19, 28,
                      "|                                                                                      |")
        stdscr.addstr(20, 28,
                      "|                                                                                      |")
        stdscr.addstr(21, 28,
                      "|                                                                                      |")
        stdscr.addstr(22, 28,
                      "+--------------------------------------------------------------------------------------+")

        stdscr.addstr(2, 117, "+----------------------------------------+")
        stdscr.addstr(3, 117, "|               Game info                |")
        stdscr.addstr(4, 117, "|                                        |")
        stdscr.addstr(5, 117, "|                                        |")
        stdscr.addstr(6, 117, "|                                        |")
        stdscr.addstr(7, 117, "|                                        |")
        stdscr.addstr(8, 117, "|                                        |")
        stdscr.addstr(9, 117, "|                                        |")
        stdscr.addstr(10, 117, "|                                        |")
        stdscr.addstr(11, 117, "+----------------------------------------+")

        stdscr.addstr(12, 117, "+----------------------------------------+")
        stdscr.addstr(13, 117, "|               Inventory                |")
        stdscr.addstr(14, 117, "|                                        |")
        stdscr.addstr(15, 117, "|                                        |")
        stdscr.addstr(16, 117, "|                                        |")
        stdscr.addstr(17, 117, "|                                        |")
        stdscr.addstr(18, 117, "|                                        |")
        stdscr.addstr(19, 117, "|                                        |")
        stdscr.addstr(20, 117, "|                                        |")
        stdscr.addstr(21, 117, "|                                        |")
        stdscr.addstr(22, 117, "+----------------------------------------+")

        # Show the name of the NPC that speaks
        stdscr.addstr(23, 29, f"Talking with:  {z}               Reliability:  {r}", curses.A_BOLD)
        stdscr.refresh()

        # Print the dialogue box
        stdscr.addstr(24, 28,
                      "+--------------------------------------------------------------------------------------+",
                      curses.A_BOLD)
        stdscr.addstr(25, 28,
                      "|                                                                                      |",
                      curses.A_BOLD)
        stdscr.addstr(26, 28,
                      "|                                                                                      |",
                      curses.A_BOLD)
        stdscr.addstr(27, 28,
                      "|                                                                                      |",
                      curses.A_BOLD)
        stdscr.addstr(28, 28,
                      "|                                                                                      |",
                      curses.A_BOLD)
        stdscr.addstr(29, 28,
                      "+--------------------------------------------------------------------------------------+",
                      curses.A_BOLD)
        stdscr.refresh()

        # Create the window and set (text rows, character limit, y,x coordinates for the window)
        picture_win = curses.newwin(19, 85, 3, 29)
        z = open(f"{y}", "r")
        picture_win.addstr(z.read())
        picture_win.refresh()
        z.close()

        # Create a new window that displays the players health and reliability
        op_win = curses.newwin(5, 30, 4, 119)
        op_win.addstr(
            f"\nPlayers Reliability: {pl_rel}\nPlayers health: {pl_hel}"
            f"\nTime:{t}")
        op_win.refresh()

        # Create another window that will show the items collected during the game
        inventory_win = curses.newwin(8, 30, 14, 119)
        inventory_win.addstr(f"You have:\n{i}")
        inventory_win.refresh()

        # Create the window and set (text rows, character limit, y,x coordinates for the window)
        text_win = curses.newwin(4, 74, 25, 30)
        # Take a given sentence and print all letters within it one by one.
        for i in x:
            text_win.addstr(f"{i}", curses.A_BOLD)
            text_win.refresh()
            time.sleep(0.07)

        # Ask for any input and clear the box
        stdscr.addstr(28, 88, f"Press any key to continue!", curses.A_BOLD)
        stdscr.getch()

    # Function that will allow player to interrogate each individual
    # a = chosen player, b = x characters excuse c = x characters relationship
    def interrogations(a):
        ui(f"~ Hello there, my name is {menu.main_player.name}.", player, a.name, a.reliability, night,
           '\n'.join(inventory))
        ui(f"~ Hello {menu.main_player.name} my name is {a.name}. How can I help you?", a.picture, a.name,
           a.reliability, night, '\n'.join(inventory))
        loop_af = True
        while loop_af:
            int_win = curses.newwin(4, 85, 25, 30)

            int_win.addstr(f" Ask about: [a] The assassin  [b] Uncle Ben  [c] Profession"
                           f"\n[d] The night of the murder  [e] 'I have to go...'\n \nType [a-e] : ", curses.A_BOLD)
            int_win.refresh()

            aq = int_win.getkey()
            if aq == "a":
                ui(f"~ So did you see or hear anything weird the day of the assassination?", player, a.name,
                   a.reliability, night, '\n'.join(inventory))
                ui(f"~ You mean anything related to the assassin?", a.picture, a.name, a.reliability, night,
                   '\n'.join(inventory))
                ui(f"~ At this point anything could be helpful to be honest.", player, a.name,
                   a.reliability, night, '\n'.join(inventory))
                ui(f"~{a.w_line}", a.picture, a.name, a.reliability, night, '\n'.join(inventory))
                ui(f"~ Hmm...I see. This could be something helpful", player, a.name,
                   a.reliability, night, '\n'.join(inventory))
            elif aq == "b":
                ui(f"~ Hey do you mind if I ask something about Ben?", player, a.name, a.reliability, night,
                   '\n'.join(inventory))
                ui(f"~ No, not att all. Ask anything.", a.picture, a.name, a.reliability, night,
                   '\n'.join(inventory))
                ui(f"~ Do you mind telling me how did you get to know my uncle?", player, a.name, a.reliability, night,
                   '\n'.join(inventory))
                ui(f"~ {a.story}", a.picture, a.name, a.reliability, night,
                   '\n'.join(inventory))
                ui(f"~ That's pretty much all you need to know.", a.picture, a.name, a.reliability, night,
                   '\n'.join(inventory))
                ui(f"~ Thanks that's more than enough for me", player, a.name, a.reliability, night,
                   '\n'.join(inventory))
            elif aq == "c":
                ui(f"~ So what do you do for work? If you don't mind me asking.", player,
                   a.name, a.reliability, night, '\n'.join(inventory))
                ui(f"~I don't mind at all. I am a {a.role}! {a.pro_line}", a.picture, a.name, a.reliability, night,
                   '\n'.join(inventory))
                ui(f"~ Cool. That sounds nice.", player, a.name, a.reliability, night, '\n'.join(inventory))
            elif aq == "d":
                ui(f"~ This may be a weird question but...where were you when the assassination took place?", player,
                   a.name, a.reliability, night, '\n'.join(inventory))
                ui(f"~{a.alibi}", a.picture, a.name, a.reliability, night, '\n'.join(inventory))
                ui(f"~ I see.\n* That could be something worth keeping in mind *", player, a.name, a.reliability, night,
                   '\n'.join(inventory))
            elif aq == "e":
                ui(f"~ Ok I have to go for now", player, a.name, a.reliability, night, '\n'.join(inventory))
                ui(f"~ See you around {menu.main_player.name}", a.picture, a.name, a.reliability, night,
                   '\n'.join(inventory))
                loop_af = False
            else:
                ui(f"* That was not a valid choice! Try again! *", default, "-----", "-----",
                   night, '\n'.join(inventory))

    # Function that will allow player to interrogate each individual
    # a = chosen player, b = x characters excuse c = x characters relationship
    def maf_interrogations(a):
        # Set a variable for the players reliability during the game
        # Depending on the players actions the number will increase and decrease
        pl_rel = menu.main_player.reliability

        ui(f"~ Hello there, my name is {menu.main_player.name}.", player, a.name, a.reliability, night,
           '\n'.join(inventory))
        ui(f"~ Hello {menu.main_player.name}, my name is {a.name}. How can I help you?", a.picture, a.name,
           a.reliability, night, '\n'.join(inventory))
        loop_af = True
        while loop_af:
            int_win = curses.newwin(4, 85, 25, 30)

            int_win.addstr(f" Ask about: [a] The assassin  [b] Ben  [c] Profession"
                           f"\n[d] Clues about the murder  [e] 'I have to go...'\n \nType [a-e] : ", curses.A_BOLD)
            int_win.refresh()

            aq = int_win.getkey()
            if aq == "a":
                ui(f"~ So did you see or hear anything weird the day of the assassination?", player, a.name,
                   a.reliability, night, '\n'.join(inventory))
                ui(f"~ You mean anything related to the assassin?", a.picture, a.name, a.reliability, night,
                   '\n'.join(inventory))
                ui(f"~ Yeah do you know anything? ", player, a.name, a.reliability, night, '\n'.join(inventory))
                ui(f"~ Well yesterday was Ben's 69th birthday and he invited many people to his birthday party ",
                   a.picture, a.name, a.reliability, night, '\n'.join(inventory))
                ui(f"~ So where were you when the murder happened?", player, a.name, a.reliability, night,
                   '\n'.join(inventory))
                ui(f"~{a.w_line}", a.picture, a.name, a.reliability, night, '\n'.join(inventory))
                ui(f"~ Hmm...I see. This could be something helpful", player, a.name, a.reliability,
                   night, '\n'.join(inventory))
                pl_rel += 5
            elif aq == "b":
                ui(f"~ Hey do you mind if I ask something about Benjamin Smith?", player, a.name, a.reliability, night,
                   '\n'.join(inventory))
                ui(f"~ No, not att all. Ask anything.", a.picture, a.name, a.reliability, night,
                   '\n'.join(inventory))
                ui(f"~ Do you mind telling me how did you get to know Benjamin?", player, a.name, a.reliability, night,
                   '\n'.join(inventory))
                ui(f"~ {a.story}", a.picture, a.name, a.reliability, night,
                   '\n'.join(inventory))
                ui(f"~ That's pretty much all you need to know.", a.picture, a.name, a.reliability, night,
                   '\n'.join(inventory))
                ui(f"~ Thanks that's more than enough for me", player, a.name, a.reliability, night,
                   '\n'.join(inventory))
                ui(f"~ By the way, I would like to ask you the same question. How did you get to know Ben?", a.picture,
                   a.name, a.reliability, night, '\n'.join(inventory))

                loop_oh = True
                while loop_oh:
                    in_win = curses.newwin(4, 85, 25, 30)

                    in_win.addstr(f" I will: [a] Pretend that I know Benjamin  [b] Tell the truth "
                                  f"\n \nType [a-e] : ", curses.A_BOLD)
                    in_win.refresh()

                    oq = in_win.getkey()
                    if oq == "a":
                        ui(f"~ I met with Ben a few years ago while I was working as an accountant. I used to take care"
                           f" of his taxes for a long time. He was a good guy and always paid me in time ", player,
                           a.name, a.reliability, night, '\n'.join(inventory))
                        ui(f"~ Ok that's cool", a.picture, a.name, a.reliability, night, '\n'.join(inventory))
                        pl_rel -= 5
                        loop_oh = False
                    elif oq == "b":
                        ui(f"~ Well to be honest with you I have no idea why I am here. I don't know this huy, Benjamin"
                           f" Smith. The police just came to my house and apparently I was one of the suspects", player,
                           a.name, a.reliability, night, '\n'.join(inventory))
                        ui(f"~ Oh ok I understand", a.picture, a.name, a.reliability, night, '\n'.join(inventory))
                        pl_rel -= 17
                        loop_oh = False
                    else:
                        ui(f"~ Invalid input please try again! ", default, " ", " ", night, '\n'.join(inventory))
            elif aq == "c":
                ui(f"~ So what do you do for work? If you don't mind me asking.", player, a.name, a.reliability,
                   night, '\n'.join(inventory))
                ui(f"~I don't mind at all. I am a {a.role}! {a.pro_line}", a.picture, a.name, a.reliability, night,
                   '\n'.join(inventory))
                ui(f"~ Cool. That sounds nice.", player, a.name, a.reliability, night, '\n'.join(inventory))
                ui(f"~ What about you {menu.main_player.name}, what do you do for work?", a.picture, a.name,
                   a.reliability, night, '\n'.join(inventory))
                ui(f"~ Well I am working as a programmer. It's an honest work with an even more honest "
                   f"pay. Besides that I find it a relaxing profession", a.picture, a.name, a.reliability, night,
                   '\n'.join(inventory))
                pl_rel += 5
            elif aq == "d":
                ui(f"~ This may be a weird question but...where were you when the assassination took place?", player,
                   a.name, a.reliability, night, '\n'.join(inventory))
                ui(f"~ Well yesterday most of us were invited at Ben's birthday party and had a lot of fun and all "
                   f"and...", a.picture, a.name, a.reliability, night, '\n'.join(inventory))
                ui(f"~{a.alibi}", a.picture, a.name, a.reliability, night, '\n'.join(inventory))
                ui(f"~ I see.\n* That could be something worth keeping in mind *", player, a.name, a.reliability, night,
                   '\n'.join(inventory))
                ui(f"~ What about you though? Did you also attend the party, because I don't remember seeing you there",
                   a.picture, a.name, a.reliability, night, '\n'.join(inventory))

                loop_eh = True
                while loop_eh:
                    in_win = curses.newwin(4, 85, 25, 30)

                    in_win.addstr(f" I will tell that: [a] I was at the party yesterday  [b] Tell the truth "
                                  f"\n \nType [a-e] : ", curses.A_BOLD)
                    in_win.refresh()

                    oq = in_win.getkey()
                    if oq == "a":
                        ui(f"~ I actually came in the party but then left immediately because I felt really sick",
                           player, a.name, a.reliability, night, '\n'.join(inventory))
                        ui(f"~ Oh, are you feeling any better today?", a.picture, a.name, a.reliability, night,
                           '\n'.join(inventory))
                        ui(f"~ Yeah, it wasn't anything serious or anything. I probably ate something that upset my "
                           f"stomach", player, a.name, a.reliability, night, '\n'.join(inventory))
                        ui(f"~ Cool, good to hear that you are well", a.picture, a.name, a.reliability, night,
                           '\n'.join(inventory))
                        pl_rel -= 5
                        loop_eh = False
                    elif oq == "b":
                        ui(f"~ I wasn't at the party yesterday. I received an invitation but I could not attend the "
                           f"party", player, a.name, a.reliability, night, '\n'.join(inventory))
                        ui(f"~ Well that's probably for the best that you weren't there. What seemed to be a fun "
                           f"evening ended up being a stressful night", a.picture, a.name, a.reliability, night,
                           '\n'.join(inventory))
                        ui(f"~ Yeah I am sorry to her that...", player, a.name, a.reliability, night,
                           '\n'.join(inventory))
                        pl_rel -= 17
                        loop_eh = False
                    else:
                        ui(f"~ Invalid input please try again! ", default, " ", " ", night, '\n'.join(inventory))
            elif aq == "e":
                ui(f"~ Well I have to go now!", player, a.name, a.reliability, night, '\n'.join(inventory))
                ui(f"~ See you around {menu.main_player.name}", a.picture, a.name, a.reliability, night,
                   '\n'.join(inventory))
                loop_af = False
            else:
                ui(f"* That was not a valid choice! Try again! *", default, "-----", "-----",
                   night, '\n'.join(inventory))

    # A function dedicated to voting players out if the player is a doctor.
    def vote_as_a_doctor(x, y):
        ui(f"Because you are a {menu.main_player.role}, you can protect one player", default, "-----",
           "-----", "Day", '\n'.join(inventory))

        loop_en = True
        while loop_en:
            vd_win = curses.newwin(4, 84, 25, 30)
            # Show all active players to user
            vd_win.addstr(f"Active players: {', '.join(x)}\n\n\nType the name of the player you want to "
                          f"protect: ", curses.A_BOLD)
            vd_win.refresh()
            curses.echo()

            # Let user type the name of the person that will be protected
            # The .decode is used in order to turn the str into UTF-8. Curses originally has a bug here and turns the
            # given input into bits instead of the native UTF-8
            ys = vd_win.getstr().decode()

            # Depending on the name written it will either be accepted or denied
            # Then remove temporarily the protected name from the active players list.
            # If everything is correct break the loop
            if ys == f"{menu.civilian_1.name}":
                protect = menu.civilian_1.name
                x.remove(protect)
                loop_en = False
            elif ys == f"{menu.civilian_2.name}":
                protect = menu.civilian_2.name
                x.remove(protect)
                loop_en = False
            elif ys == f"{menu.civilian_3.name}":
                protect = menu.civilian_3.name
                x.remove(protect)
                loop_en = False
            elif ys == f"{menu.civilian_4.name}":
                protect = menu.civilian_4.name
                x.remove(protect)
                loop_en = False
            elif ys == f"{menu.mafioso_1.name}":
                protect = menu.mafioso_1.name
                x.remove(protect)
                loop_en = False
            elif ys == f"{menu.mafioso_2.name}":
                protect = menu.mafioso_2.name
                x.remove(protect)
                loop_en = False
            elif ys == f"{menu.detective.name}":
                protect = menu.detective.name
                x.remove(protect)
                loop_en = False
            else:
                ui(f"* Player doesn't exist. Please try again and type the name exactly as shown in the screen*",
                   default, "-----", "-----", night, '\n'.join(inventory))

        # At this point the "other players" will choose one person that they think is the murderer.
        # This could be done in the future with a complex algorithm but for simplicity
        # the suspect will be chosen randomly
        z = random.choice(x)
        ui(f"* The voting process started.... *", default, "-----",
           "-----", "Day", '\n'.join(inventory))
        ui(f"* It takes some time but the majority thinks that {z}, is a mafia member! *", mafia_the_t_g, "-----",
           "-----", "Day", '\n'.join(inventory))
        ui(f"* Since you are the MC of this game you decide who will get kicked out! *", player, "-----", "-----",
           "Day", '\n'.join(inventory))

        loop_en = True
        while loop_en:
            vd_win = curses.newwin(4, 84, 25, 30)
            # Show the updated list of all active players to user
            vd_win.addstr(f"Active players: {', '.join(x)}\n\n\nType the name of the player you want to "
                          f"vote out: ", curses.A_BOLD)
            counter_win.refresh()
            curses.echo()

            # Let user type the name of the person that will be protected
            # The .decode is used in order to turn the str into UTF-8. Curses originally has a bug here and turns the
            # given input into bits instead of the native UTF-8
            us = vd_win.getstr().decode()

            # Remove the player that the user voted out and append back the protected player that was chosen above.
            # If everything is correct break the loop
            if us == f"{menu.civilian_1.name}":
                x.remove(menu.civilian_1.name)
                y.remove(menu.civilian_1.category)
                x.append(protect)
                loop_en = False
            elif us == f"{menu.civilian_2.name}":
                x.remove(menu.civilian_2.name)
                y.remove(menu.civilian_2.category)
                x.append(protect)
                loop_en = False
            elif us == f"{menu.civilian_3.name}":
                x.remove(menu.civilian_3.name)
                y.remove(menu.civilian_3.category)
                x.append(protect)
                loop_en = False
            elif us == f"{menu.civilian_4.name}":
                x.remove(menu.civilian_4.name)
                y.remove(menu.civilian_4.category)
                x.append(protect)
                loop_en = False
            elif us == f"{menu.mafioso_1.name}":
                x.remove(menu.mafioso_1.name)
                y.remove(menu.mafioso_1.real_role)
                x.append(protect)
                loop_en = False
            elif us == f"{menu.mafioso_2.name}":
                x.remove(menu.mafioso_2.name)
                y.remove(menu.mafioso_2.real_role)
                x.append(protect)
                loop_en = False
            elif us == f"{menu.detective.name}":
                x.remove(menu.detective.name)
                y.remove(menu.detective.role)
                x.append(protect)
                loop_en = False
            else:
                ui(f"* Player doesn't exist. Please try again *", default, "-----", "-----", night,
                   '\n'.join(inventory))

    # A function dedicated to voting players out if the player is a doctor.
    def vote_as_a_detective(x, y):
        ui(f"Because you are a {menu.main_player.role}, you can protect one player", default, "-----",
           "-----", "Day", '\n'.join(inventory))

        loop_es = True
        while loop_es:
            vd_win = curses.newwin(4, 84, 25, 30)
            # Show all active players to user
            vd_win.addstr(f"Active players: {', '.join(x)}\n\n\nType the name of the player you want to "
                          f"protect: ", curses.A_BOLD)
            vd_win.refresh()
            curses.echo()

            # Let user type the name of the person that will be protected
            # The .decode is used in order to turn the str into UTF-8. Curses originally has a bug here and turns the
            # given input into bits instead of the native UTF-8
            ys = vd_win.getstr().decode()

            # Depending on the name written it will either be accepted or denied
            # Then remove temporarily the protected name from the active players list.
            # If everything is correct break the loop
            if ys == f"{menu.civilian_1.name}":
                protect = menu.civilian_1.name
                x.remove(protect)
                loop_es = False
            elif ys == f"{menu.civilian_2.name}":
                protect = menu.civilian_2.name
                x.remove(protect)
                loop_es = False
            elif ys == f"{menu.civilian_3.name}":
                protect = menu.civilian_3.name
                x.remove(protect)
                loop_es = False
            elif ys == f"{menu.civilian_4.name}":
                protect = menu.civilian_4.name
                x.remove(protect)
                loop_es = False
            elif ys == f"{menu.mafioso_1.name}":
                protect = menu.mafioso_1.name
                x.remove(protect)
                loop_es = False
            elif ys == f"{menu.mafioso_2.name}":
                protect = menu.mafioso_2.name
                x.remove(protect)
                loop_es = False
            elif ys == f"{menu.detective.name}":
                protect = menu.detective.name
                x.remove(protect)
                loop_es = False
            else:
                ui(f"* Player doesn't exist. Please try again and type the name exactly as shown in the screen*",
                   default, "-----", "-----", night, '\n'.join(inventory))

        # At this point the "other players" will choose one person that they think is the murderer.
        # This could be done in the future with a complex algorithm but for simplicity
        # the suspect will be chosen randomly
        z = random.choice(x)
        ui(f"* The voting process started.... *", default, "-----", "-----", night, '\n'.join(inventory))
        ui(f"* It takes some time but the majority thinks that {z}, is a mafia member! *", mafia_the_t_g, "-----",
           "-----", "Day", '\n'.join(inventory))
        ui(f"* Since you are the MC of this game you decide who will get kicked out! *", player, "-----", "-----",
           "Day", '\n'.join(inventory))

        loop_es = True
        while loop_es:
            vd_win = curses.newwin(4, 84, 25, 30)
            # Show the updated list of all active players to user
            vd_win.addstr(f"Active players: {', '.join(x)}\n\n\nType the name of the player you want to "
                          f"vote out: ", curses.A_BOLD)
            vd_win.refresh()
            curses.echo()

            # Let user type the name of the person that will be protected
            # The .decode is used in order to turn the str into UTF-8. Curses originally has a bug here and turns the
            # given input into bits instead of the native UTF-8
            us = vd_win.getstr().decode()

            # Remove the player that the user voted out and append back the protected player that was chosen above.
            # If everything is correct break the loop
            if us == f"{menu.civilian_1.name}":
                x.remove(menu.civilian_1.name)
                y.remove(menu.civilian_1.category)
                x.append(protect)   # protect calls a warning but it actually works without any problems
                loop_es = False
            elif us == f"{menu.civilian_2.name}":
                x.remove(menu.civilian_2.name)
                y.remove(menu.civilian_2.category)
                x.append(protect)
                loop_es = False
            elif us == f"{menu.civilian_3.name}":
                x.remove(menu.civilian_3.name)
                y.remove(menu.civilian_3.category)
                x.append(protect)
                loop_es = False
            elif us == f"{menu.civilian_4.name}":
                x.remove(menu.civilian_4.name)
                y.remove(menu.civilian_4.category)
                x.append(protect)
                loop_es = False
            elif us == f"{menu.mafioso_1.name}":
                x.remove(menu.mafioso_1.name)
                y.remove(menu.mafioso_1.real_role)
                x.append(protect)
                loop_es = False
            elif us == f"{menu.mafioso_2.name}":
                x.remove(menu.mafioso_2.name)
                y.remove(menu.mafioso_2.real_role)
                x.append(protect)
                loop_es = False
            elif us == f"{menu.detective.name}":
                x.remove(menu.detective.name)
                y.remove(menu.detective.role)
                x.append(protect)
                loop_es = False
            else:
                ui(f"* Player doesn't exist. Please try again *", default, "-----", "-----", night,
                   '\n'.join(inventory))

    # A function dedicated to voting players out if the player is a doctor.
    def vote_as_a_mafioso(x, y):

        loop_mv = True
        while loop_mv:
            va_win = curses.newwin(4, 84, 25, 30)
            # Show the updated list of all active players to user
            va_win.addstr(f"Active players: {', '.join(x)}\n\n\nType the name of the player you want to "
                          f"vote out: ", curses.A_BOLD)
            counter_win.refresh()
            curses.echo()

            # Let user type the name of the person that will be protected
            # The .decode is used in order to turn the str into UTF-8. Curses originally has a bug here and turns the
            # given input into bits instead of the native UTF-8
            us = va_win.getstr().decode()

            # Remove the player that the user voted out and append back the protected player that was chosen above.
            # If everything is correct break the loop
            if us == f"{menu.civilian_1.name}":
                x.remove(menu.civilian_1.name)
                y.remove(menu.civilian_1.category)
                loop_mv = False
            elif us == f"{menu.civilian_2.name}":
                x.remove(menu.civilian_2.name)
                y.remove(menu.civilian_2.category)
                loop_mv = False
            elif us == f"{menu.civilian_3.name}":
                x.remove(menu.civilian_3.name)
                y.remove(menu.civilian_3.category)
                loop_mv = False
            elif us == f"{menu.civilian_4.name}":
                x.remove(menu.civilian_4.name)
                y.remove(menu.civilian_4.category)
                loop_mv = False
            elif us == f"{menu.mafioso_1.name}":
                x.remove(menu.mafioso_1.name)
                y.remove(menu.mafioso_1.real_role)
                loop_mv = False
            elif us == f"{menu.detective.name}":
                x.remove(menu.detective.name)
                y.remove(menu.detective.role)
                loop_mv = False
            elif us == f"{menu.doctor.name}":
                x.remove(menu.doctor.name)
                y.remove(menu.doctor.role)
                loop_mv = False
            else:
                ui(f"* Player doesn't exist. Please try again *", default, "-----", "-----", "Day",
                   '\n'.join(inventory))

        # At this point the "other players" will choose one person that they think is the murderer.
        # This could be done in the future with a complex algorithm but for simplicity the suspect
        # will be chosen randomly
        z = random.choice(x)
        ui(f"* The voting process started.... *", default, "-----",
           "-----", "Day", '\n'.join(inventory))
        ui(f"* It takes some time but the majority thinks that {z}, is a mafia member! *", mafia_the_t_g, "-----",
           "-----", "Day", '\n'.join(inventory))
        ui(f"* Since you are the MC of this game you decide who will get kicked out! *", player, "-----", "-----",
           "Day", '\n'.join(inventory))

        loop_mv = True
        while loop_mv:
            va_win = curses.newwin(4, 84, 25, 30)
            # Show the updated list of all active players to user
            va_win.addstr(f"Active players: {', '.join(x)}\n\n\nType the name of the player you want to "
                          f"vote out: ", curses.A_BOLD)
            counter_win.refresh()
            curses.echo()

            # Let user type the name of the person that will be protected
            # The .decode is used in order to turn the str into UTF-8. Curses originally has a bug here and turns the
            # given input into bits instead of the native UTF-8
            us = va_win.getstr().decode()

            # Remove the player that the user voted out and append back the protected player that was chosen above.
            # If everything is correct break the loop
            if us == f"{menu.civilian_1.name}":
                x.remove(menu.civilian_1.name)
                y.remove(menu.civilian_1.category)
                loop_mv = False
            elif us == f"{menu.civilian_2.name}":
                x.remove(menu.civilian_2.name)
                y.remove(menu.civilian_2.category)
                loop_mv = False
            elif us == f"{menu.civilian_3.name}":
                x.remove(menu.civilian_3.name)
                y.remove(menu.civilian_3.category)
                loop_mv = False
            elif us == f"{menu.civilian_4.name}":
                x.remove(menu.civilian_4.name)
                y.remove(menu.civilian_4.category)
                loop_mv = False
            elif us == f"{menu.mafioso_1.name}":
                x.remove(menu.mafioso_1.name)
                y.remove(menu.mafioso_1.real_role)
                loop_mv = False
            elif us == f"{menu.detective.name}":
                x.remove(menu.detective.name)
                y.remove(menu.detective.role)
                loop_mv = False
            elif us == f"{menu.doctor.name}":
                x.remove(menu.doctor.name)
                y.remove(menu.doctor.role)
                loop_mv = False
            else:
                ui(f"* Player doesn't exist. Please try again *", default, "-----", "-----", night,
                   '\n'.join(inventory))

    # Check if the game should end or not
    def check(v):
        # From the list of roles given as (v) open and check how many times is the word Mafioso in
        o = v.count("Mafioso")

        # From the list of roles given as (v) open and count how many times are the words Civilian, Doctor, Detective in
        m = v.count("Civilian") + v.count("Doctor") + v.count("Detective")

        if o == 0:
            ui(f"* After hours of investigations and voting mafia got finally exposed. The last mafioso was "
               f"{menu.mafioso_1.name} *\n* {menu.mafioso_1.name} even admitted that {menu.mafioso_2.name} was involved"
               f" in Ben's assassination *", default, "-----", "-----", night, '\n'.join(inventory))
            ui(f"* A month later since the police arrested the mafia members and Springfield looks better than ever *",
               transition_three, "-----", "-----", night, '\n'.join(inventory))
            ui(f"* The crime rates dropped by 50% and people feel safe thanks to you ! *", springfield, "-----",
               "-----", night, '\n'.join(inventory))
            ui(f"* Congratulations {menu.main_player.name}! You won the game! *", game_over, "-----", "-----", night,
               '\n'.join(inventory))
            quit()
        elif o >= 1 and m == 2:
            ui(f"* The police arrested everyone that was involved with the murder and now it is time to relax. *\n* All"
               f" mafia members were found and~ *", default, "-----", "-----", night, '\n'.join(inventory))
            ui(f"* Wait a minute..... *", bomb, "-----", "-----", night, '\n'.join(inventory))
            ui(f"* They arrested the wrong people... *", player, "-----", "-----", night, '\n'.join(inventory))
            ui(f"* Bad luck {menu.main_player.name} you failed to identify who was the mafioso within the group *",
               game_over, "-----", "-----", night, '\n'.join(inventory))
            quit()
        else:
            ui(f"* The mafia members are hiding very well. The police still can't find them *",
               default, "-----", "-----", night, '\n'.join(inventory))

    # Check if the game should end or not only if the player is a mafioso
    def maf_check(v):
        # From the list of roles given as (v) open and check how many times is the word Mafioso in
        o = v.count("Mafioso")

        # From the list of roles given as (v) open and count how many times are the words Civilian, Doctor, Detective in
        m = v.count("Civilian") + v.count("Doctor") + v.count("Detective")

        if o >= 1 and m <= 2:
            ui(f"* It was a close call but it seems the police is satisfied with the results *", player, " ", " ",
               night, '\n'.join(inventory))
            ui(f"* The police arrested everyone that was 'supposedly' involved with the murder and they never found "
               f"about you *\n* You successfully tricked everyone and now it's time to relax *",
               mafia_the_t_g, " ", " ", night, '\n'.join(inventory))
            ui(f"* Congratulations {menu.main_player.name} you won the game! *\n * Feel free to play again and explore"
               f" the other paths available *", game_over, " ", " ", night, '\n'.join(inventory))
            quit()
        elif o == 0 and m >= 2:
            ui(f"* After hours of investigations and voting the civilians found out about me and {menu.mafioso_1.name}."
               f"\n* {menu.mafioso_1.name} even told the police whose the head of the mafia and the others that were"
               f" involved in Ben's assassination *", mafia_the_t_g, " ", " ", night, '\n'.join(inventory))
            ui(f"* A month later since the police arrested all mafia members and Springfield looks better than ever *",
               transition_three, " ", " ", night, '\n'.join(inventory))
            ui(f"* The crime rates dropped by 50% and people feel safe without you and the rest of the mafia being"
               f" around *", springfield, " ", " ", night, '\n'.join(inventory))
            ui(f"* Unfortunately you lost {menu.main_player.name}! Feel free to try again and check the other paths *",
               game_over, " ", " ", night, '\n'.join(inventory))
            quit()
        elif o >= 1 and m == 0:
            ui(f"* The police arrested everyone that was supposedly involved with the murder and they never found about"
               f" you *\n* You successfully tricked everyone and now it's time to relax *",
               mafia_the_t_g, " ", " ", night, '\n'.join(inventory))
            ui(f"* Congratulations {menu.main_player.name} you won the game! *\n * Feel free to play again and explore"
               f" the other paths available *", game_over, " ", " ", night, '\n'.join(inventory))
            quit()
        else:
            ui(f"* The game must continue! There are still many players from both sides in! *",
               default, " ", " ", night, '\n'.join(inventory))

    # Create a list that will be the players main inventory
    inventory = []

    # Set a simple boolean that will change depending on the players decisions on the game
    veronica_meet = False
    # If the player discovers the secrete diary turn this on and activate later the secret ending.
    # the diary is in the safe at uncle Ben's office. The code is "1974"
    secret_diary = False

    # If the player chose to be a mafioso start path 1
    if menu.main_player.role == "Mafioso":
        ui(f" Welcome to Mafia: The terminal game!\nThe mafia mode is not completed yet but in future "
           f"updates there will be a complete story mode.", mafia_the_t_g, " ", " ", day, '\n'.join(inventory))
        ui(f"Your goal as the mafioso is to kill as many people as you can before you get voted out ", mafia_mode,
           " ", " ", day, '\n'.join(inventory))
        ui(f" Let us begin", default, " ", " ", day, '\n'.join(inventory))
        ui(f" Meet {menu.doctor.name} a doctor with passion for music", menu.doctor.picture, " ", " ", day,
           '\n'.join(inventory))
        ui(f" Meet {menu.detective.name} the best detective in town", menu.detective.picture, " ", " ", day,
           '\n'.join(inventory))
        ui(f" Meet {menu.civilian_1.name} a {menu.civilian_1.role} and art enthusiast", menu.civilian_1.picture, " ",
           " ", day, '\n'.join(inventory))
        ui(f" Meet {menu.civilian_2.name} a {menu.civilian_2.role} and coffee expert", menu.civilian_2.picture, " ",
           " ", day, '\n'.join(inventory))
        ui(f" Meet {menu.civilian_3.name} a {menu.civilian_3.role}", menu.civilian_3.picture, " ",
           " ", day, '\n'.join(inventory))
        ui(f" Meet {menu.civilian_4.name} a {menu.civilian_4.role}", menu.civilian_4.picture, " ",
           " ", day, '\n'.join(inventory))
        ui(f" Last but not least meet {menu.mafioso_1.name} a {menu.mafioso_1.role} whose actually a Mafioso like you",
           menu.mafioso_1.picture, " ", " ", day, '\n'.join(inventory))
        ui(f" You wake up early in the morning and you hear a knock on the door", maf_room, " ", " ", day,
           '\n'.join(inventory))
        ui(f"* While you get up, you see your pistol and keys on the table *", default, " ", " ", day,
           '\n'.join(inventory))
        ui(f"* Maybe you should pick up your gun and keys from the table *", maf_gun, " ", " ", day,
           '\n'.join(inventory))

        # Two simple variables containing the players gun and keys
        pistol = "Pistol"
        keys = "House Keys"

        loop = True
        while loop:
            g_win = curses.newwin(4, 84, 25, 30)

            g_win.addstr("I will: [a] Take my gun and keys. [b] Leave them on the table \n \nType [a] or [b]: ")
            g_win.refresh()

            cq = g_win.getkey()
            if cq == "a":
                inventory.append(pistol)
                inventory.append(keys)
                ui(f"* You pick up your pistol and keys and head to the main door *", default, " ", " ", day,
                   '\n'.join(inventory))
                loop = False
            elif cq == "b":
                ui(f"* Although you are a mafioso you decide to leave your gun as it is and head strait to open the"
                   f" door*", default, " ", " ", day, '\n'.join(inventory))
                loop = False
            else:
                ui(f"* Invalid input please try again! *", default, " ", " ", day, '\n'.join(inventory))

        ui(f"* At once you open the door and you see a police officer *", police, " ", " ", day, '\n'.join(inventory))
        ui(f"~ Hello officer how can I help you?", player, " ", " ", day, '\n'.join(inventory))
        ui(f"~ Are you {menu.main_player.name}? ", police, " ", " ", day, '\n'.join(inventory))
        ui(f"~ Yes\n~ Is everything alright? ", player, " ", " ", day, '\n'.join(inventory))
        ui(f"~ Unfortunately not. You are accused of murdering Benjamin  Smith. I have a warrant for your arrest please"
           f" follow me ", police, " ", " ", day, '\n'.join(inventory))
        ui(f"*  *", one_hour_later, " ", " ", day,
           '\n'.join(inventory))
        ui(f"* The police gathers a lot of people in one room and within those people you see a coworker of yours "
           f"{menu.mafioso_1.name} *", default, " ", " ", day, '\n'.join(inventory))
        ui(f"* You decide to go and speak with {menu.mafioso_1.name} since he probably killed the man named Ben *",
           default, " ", " ", day, '\n'.join(inventory))
        ui(f"* Hello {menu.mafioso_1.name}, did you...you know did the thing...?*", player, menu.mafioso_1.name,
           menu.mafioso_1.reliability, day, '\n'.join(inventory))
        ui(f"~ I don't know what you are talking about {menu.main_player.name}. I haven't done anything",
           menu.mafioso_1.picture, menu.mafioso_1.name, menu.mafioso_1.reliability, day, '\n'.join(inventory))
        ui(f"* It was definitely {menu.mafioso_1.name} *", default, menu.mafioso_1.name,
           menu.mafioso_1.reliability, day, '\n'.join(inventory))
        ui(f"~ So..Do you know why did they gather all of us here at once?", player, menu.mafioso_1.name,
           menu.mafioso_1.reliability, day, '\n'.join(inventory))
        ui(f"~ From what I understand they will use a new method for identifying who is the murderer. ",
           menu.mafioso_1.picture, menu.mafioso_1.name, menu.mafioso_1.reliability, day, '\n'.join(inventory))
        ui(f"~ What kind of method?", player, menu.mafioso_1.name, menu.mafioso_1.reliability, day,
           '\n'.join(inventory))
        ui(f"~ They will keep us all here and let us investigate each other in order to try and find out who is the "
           f"murderer. Once we are done we will vote one out and that person will be imprisoned temporarily",
           menu.mafioso_1.picture, menu.mafioso_1.name, menu.mafioso_1.reliability, day, '\n'.join(inventory))
        ui(f"~ Are you kidding me? That doesn't make any sense and it is almost certainly illegal", player,
           menu.mafioso_1.name, menu.mafioso_1.reliability, day, '\n'.join(inventory))
        ui(f"~ You are not wrong but these are the game's rules for plot convenience.", menu.mafioso_1.picture,
           menu.mafioso_1.name, menu.mafioso_1.reliability, day, '\n'.join(inventory))
        ui(f"~ I don't know what that even means but I am in.", player, menu.mafioso_1.name, menu.mafioso_1.reliability,
           day, '\n'.join(inventory))
        ui(f"~ Great we can now start killing more people now because we are assassins and that makes sense",
           menu.mafioso_1.picture, menu.mafioso_1.name, menu.mafioso_1.reliability, day, '\n'.join(inventory))
        ui(f"~ I will not even question this kind of logic at all. Lets move on with our mission", player,
           menu.mafioso_1.name, menu.mafioso_1.reliability, day, '\n'.join(inventory))
        ui(f"* Time to kill someone *", default, menu.mafioso_1.name, menu.mafioso_1.reliability, day,
           '\n'.join(inventory))
        ui(f"* The people in the room are: {menu.civilian_1.name}, {menu.civilian_2.name}, {menu.civilian_3.name}, "
           f"{menu.civilian_4.name}, {menu.mafioso_1.name}, {menu.detective.name}, {menu.doctor.name}* \n ", default,
           "-----", "-----", "Afternoon", '\n'.join(inventory))

        # Start a loop for the interrogation phase.
        # Let the player can talk with the others without any limit on time
        # Rerun this piece of code until the end phase of the game
        loop = True
        while loop:
            counter_win = curses.newwin(4, 84, 25, 30)

            counter_win.addstr(f" Talk with: [a] {menu.civilian_1.name} [b] {menu.civilian_2.name}, "
                               f"[c] {menu.civilian_3.name}, [d] {menu.civilian_4.name}, [e] {menu.mafioso_1.name}, "
                               f"[f] {menu.doctor.name}, [g] {menu.detective.name}, [h] Start the voting possess\n"
                               f" Type [a-h]: ", curses.A_BOLD)
            counter_win.refresh()
            active_players = ["a", "b", "c", "d", "e", "f", "g"]
            cf = counter_win.getkey()

            # Search for the picked character within the active players list
            # Based on the input [a-g] specify witch character from counter_win is chosen
            # Note: Fix this so you don't need two have two active lists in the future
            if cf in active_players and cf == "a":
                person = menu.civilian_1
                maf_interrogations(person)
            elif cf in active_players and cf == "b":
                person = menu.civilian_2
                maf_interrogations(person)
            elif cf in active_players and cf == "c":
                person = menu.civilian_3
                maf_interrogations(person)
            elif cf in active_players and cf == "d":
                person = menu.civilian_4
                maf_interrogations(person)
            elif cf in active_players and cf == "e":
                person = menu.mafioso_1
                maf_interrogations(person)
            elif cf in active_players and cf == "f":
                person = menu.mafioso_2
                maf_interrogations(person)
            elif cf in active_players and cf == "g":
                person = menu.detective
                maf_interrogations(person)
            elif cf == "h":
                looper = True
                while looper:
                    counter_win = curses.newwin(4, 84, 25, 30)
                    curses.echo()
                    counter_win.addstr(f" After this point you wont be able to speak with the other characters again!\n"
                                       f" Are you sure you are done? [Y/N]: ", curses.A_BOLD)
                    counter_win.refresh()
                    ce = counter_win.getstr().decode().lower()
                    if ce == "y" or ce == "yes":
                        ui(f"* Time to vote someone out then! *", default, "-----", "-----", night,
                           '\n'.join(inventory))
                        looper = False
                        loop = False
                    elif ce == "n" or ce == "no":
                        ui(f"* OK! Sending you back now *", default, "-----", "-----", night, '\n'.join(inventory))
                        looper = False
                    else:
                        ui(f"* Invalid choice! Please type [Y/N] or [YES/NO]*", default, "-----", "-----", night,
                           '\n'.join(inventory))
            else:
                ui(f"* Player doesn't exist. Please try again *", default, "-----", "-----", night,
                   '\n'.join(inventory))

        # Create a list with all the active players in the game.
        # This list is used only if the player is a doctor
        maf_active_roles = [f"{menu.civilian_1.category}", f"{menu.civilian_2.category}", f"{menu.civilian_3.category}",
                            f"{menu.civilian_4.category}", f"{menu.mafioso_1.real_role}", f"{menu.detective.role}",
                            f"{menu.doctor.role}", f"{menu.main_player.role}"]

        # Create a third list with all the active players in the game.
        # This list is used only if the player is a mafioso
        maf_active_players = [f"{menu.civilian_1.name}", f"{menu.civilian_2.name}", f"{menu.civilian_3.name}",
                              f"{menu.civilian_4.name}", f"{menu.mafioso_1.name}", f"{menu.detective.name}",
                              f"{menu.doctor.name}"]

        # Start a the voting/killing process and then check which players are left
        vote_as_a_mafioso(maf_active_players, maf_active_roles)
        maf_check(maf_active_roles)

        ui(f"* One person is voted out and one is secretly killed *", default, " ", " ", day, '\n'.join(inventory))
        ui(f"* Suddenly an officer comes towards you *", default, " ", " ", day, '\n'.join(inventory))
        ui(f"~ You there! We found this down on the floor\n* The officer shows you a {menu.mafioso_1.item} *\n~ Is that"
           f" yours?", officer_one, "Officer", "80", day, '\n'.join(inventory))
        ui(f"* This one looks like {menu.mafioso_1.name}'s {menu.mafioso_1.item}*\n* Maybe I should take it and give"
           f" it back *", default, "Officer", "80", day, '\n'.join(inventory))

        # Start a loop for giving the user a chance to take a secrete item or not
        # In future updates this item will change the entire course of the game
        loop = True
        while loop:
            item_win = curses.newwin(4, 84, 25, 30)

            item_win.addstr(f" The {menu.mafioso_1.item} is: [a] Mine  [b]  Not mine", curses.A_BOLD)
            item_win.refresh()

            cz = item_win.getkey()
            if cz == "a":
                ui(f"~ Yes that's mine officer thank you. ", player, "Officer", "80", day, '\n'.join(inventory))
                ui(f"~ Not a problem. Just be careful with you stuff", officer_one, "Officer", "80", day,
                   '\n'.join(inventory))
                inventory.append(menu.mafioso_1.item)
                ui(f"* You take the {menu.mafioso_1.item} and you go to speak with {menu.mafioso_1.name} *",
                   default, " ", " ", day, '\n'.join(inventory))
                ui(f" ", ten_minutes_later, " ", " ", day, '\n'.join(inventory))
                ui(f"~ Hello {menu.main_player.name}. Whats up?", menu.mafioso_1.picture, menu.mafioso_1.name,
                   menu.mafioso_1.reliability, day, '\n'.join(inventory))
                ui(f"~ What is up is that you dropped your {menu.mafioso_1.item} accidentally and the police was "
                   f"searching for its owner", player, " ", " ", day, '\n'.join(inventory))
                ui(f"* You return the {menu.mafioso_1.item} to {menu.mafioso_1.name} *", default, " ", " ", day,
                   '\n'.join(inventory))
                inventory.remove(menu.mafioso_1.item)
                ui(f"~ Oh thanks! I thought that I lost that.", menu.mafioso_1.picture, menu.mafioso_1.name,
                   menu.mafioso_1.reliability, day, '\n'.join(inventory))
                ui(f"~ Just be careful because with something like that they can find about you and this case",
                   player, " ", " ", day, '\n'.join(inventory))
                ui(f"~ ok ok relax. Let us continue with our mission", menu.mafioso_1.picture, menu.mafioso_1.name,
                   menu.mafioso_1.reliability, day, '\n'.join(inventory))
                loop = False
            elif cz == "b":
                ui(f"~ Well no that's not mine officer. ", player, "Officer", "80", day, '\n'.join(inventory))
                ui(f"~ ok good to know. I will ask the others also", officer_one, "Officer", "80", day,
                   '\n'.join(inventory))
                ui(f" ", ten_minutes_later, " ", " ", day, '\n'.join(inventory))
                ui(f"~ Hey {menu.main_player.name}. Have you seen any {menu.mafioso_1.item} around?",
                   menu.mafioso_1.picture, menu.mafioso_1.name, menu.mafioso_1.reliability, day, '\n'.join(inventory))
                ui(f"~ Yes, I have. An officer had it and asked me if it was mine. Was it yours?", player, " ", " ",
                   day, '\n'.join(inventory))
                ui(f"~ The {menu.mafioso_1.item} is mine and I left one identical {menu.mafioso_1.item} on the old"
                   f" man's house yesterday", menu.mafioso_1.picture, menu.mafioso_1.name, menu.mafioso_1.reliability,
                   day, '\n'.join(inventory))
                ui(f"~ Lets hope that we manage to kill everyone here before they find about it then", player, " ", " ",
                   day, '\n'.join(inventory))
                loop = False
            else:
                ui(f"* Invalid input please try again *", default, " ", " ", day, '\n'.join(inventory))

        # Set a min, max number
        min_num = 1
        max_num = 6
        f = random.randint(min_num, max_num)
        # If the number is 2 then the other players found out about the user being a mafioso
        if f == "2":
            ui(f"* While you were waiting for the next voting phase the police investigated privately "
               f"{menu.mafioso_1.name} *", mafia_the_t_g, " ", " ", day, '\n'.join(inventory))
            ui(f"* They found out some fingerprints in Benjamin Smith's house and those fingerprints belong to "
               f"{menu.mafioso_1.name}*", default, " ", " ", day, '\n'.join(inventory))
            ui(f"* In order to get a mild sentence {menu.mafioso_1.name} snitches and gives the names of all mafia "
               f"members*", mafia_the_t_g, " ", " ", day, '\n'.join(inventory))
            if pistol in inventory:
                ui(f"* At first you are given the chance for a fair trial but they search you and they find the pistol"
                   f" that you took this morning*", mafia_the_t_g, " ", " ", day, '\n'.join(inventory))
                ui(f"* Your sentence is five years in prison and two years for illegal possession of guns*", game_over,
                   " ", " ", day, '\n'.join(inventory))
                quit()
            else:
                ui(f"* Unfortunately they arrest you and your sentence is five years in prison *", game_over,
                   " ", " ", day, '\n'.join(inventory))
                quit()
        # If the number is anything else but 2 then they failed to find who the user is and the game continues
        else:
            ui(f"* Some of the characters tried to convince the police to arrest you but they failed *",
               default, " ", " ", day, '\n'.join(inventory))

        ui(f"* Time to repay the favour! *", mafia_the_t_g, " ", " ", day, '\n'.join(inventory))
        vote_as_a_mafioso(maf_active_players, maf_active_roles)
        maf_check(maf_active_roles)

        f = random.randint(min_num, max_num)
        # If the number is 2 then the other players found out about the user being a mafioso
        if f == "2":
            ui(f"* While you were waiting for the next voting phase the police investigated privately "
               f"{menu.mafioso_1.name} *", mafia_the_t_g, " ", " ", day, '\n'.join(inventory))
            ui(f"* They found out some fingerprints in Benjamin Smith's house and those fingerprints belong to "
               f"{menu.mafioso_1.name}*", default, " ", " ", day, '\n'.join(inventory))
            ui(f"* In order to get a mild sentence {menu.mafioso_1.name} snitches and gives the names of all mafia "
               f"members*", mafia_the_t_g, " ", " ", day, '\n'.join(inventory))
            if pistol in inventory:
                ui(f"* At first you are given the chance for a fair trial but they search you and they find the pistol"
                   f" that you took this morning*", mafia_the_t_g, " ", " ", day, '\n'.join(inventory))
                ui(f"* Your sentence is five years in prison and two years for illegal possession of guns*", game_over,
                   " ", " ", day, '\n'.join(inventory))
                quit()
            else:
                ui(f"* Unfortunately they arrest you and your sentence is five years in prison *", game_over,
                   " ", " ", day, '\n'.join(inventory))
                quit()
        # If the number is anything else but 2 then they failed to find who the user is and the game continues
        else:
            ui(f"* Some of the characters tried to convince the police to arrest you but they failed *",
               default, " ", " ", day, '\n'.join(inventory))

        ui(f"* One more vote like this nad they will certainly find your identity *\n* It's payback time *",
           mafia_the_t_g, " ", " ", day, '\n'.join(inventory))
        vote_as_a_mafioso(maf_active_players, maf_active_roles)
        maf_check(maf_active_roles)

        # In case of a bug the next two lines ensure that the active_players list will be emptied
        ui(f"* For some reason you have to vote again! *", default, " ", " ", day, '\n'.join(inventory))
        vote_as_a_mafioso(maf_active_players, maf_active_roles)
        maf_check(maf_active_roles)
# If the player chose to be a Doctor then start path 2
    elif menu.main_player.role == "Doctor":

        # Call the dialogue function. Pass (text),(picture),(name of the character or place that will be shown)
        ui(f"Congratulations {menu.main_player.name}. The game is ready to start", mafia_the_t_g, "-----", "-----",
           "Afternoon", '\n'.join(inventory))
        ui(f"You are at your home, relaxing after a long day at work", default, "-----", "-----", "Afternoon",
           '\n'.join(inventory))
        ui(f"Suddenly you hear a knock from the front door", hall, "-----", "-----", "Afternoon", '\n'.join(inventory))
        ui(f"* As you walk towards the door you notice an envelope on the floor and it seems like it's a letter *"
           f" from uncle Ben.", entrance, "-----", "-----", "Afternoon", '\n'.join(inventory))
        ui(f"It has been a while since you had news from uncle Ben and therefore you sit down, open the letter and "
           f"read it with curiosity.", envelope, "-----", "-----", "Afternoon", '\n'.join(inventory))
        opening(f"*You read the letter*", invitation, "-----", "-----", '\n'.join(inventory))
        opening(f"Although I have a lot of work next week I should be able to free some time for uncles' birthday",
                invitation, "-----", "-----", '\n'.join(inventory))
        ui(f" ", transition, "-----", "-----", "-----", '\n'.join(inventory))
        ui(f"*You are in front of uncle Ben's house and notice that all lights are lit.*", house, "-----", "-----",
           night, '\n'.join(inventory))
        ui(f"~I hope I am not too late.", fence, "-----", "-----", night, '\n'.join(inventory))
        ui(f"*While you get closer to the entrance you can hear music and people talking*", house_out, "-----", "-----",
           night, '\n'.join(inventory))
        ui(f"~Well it seems uncle called quite a few people for his birthday. I should better go and greet him.",
           house_hall, "-----", "-----", night, '\n'.join(inventory))
        ui(f"*You spend some time searching but you can't find uncle Ben. He is probably upstairs att his office.*",
           default, "-----", "-----", night, '\n'.join(inventory))
        ui(f"*It is way more quiet upstairs, you think*", base_room, "-----", "-----", night, '\n'.join(inventory))
        ui(f"*Once you arrive just outside of the office, you can hear people talking the other side. Although impolite"
           f", you decide to eavesdrop before entering.*", base, "-----", "-----", night, '\n'.join(inventory))
        ui(f"[Voice 1]~ We know everything about your plans.\n I hope you understand though it's nothing personal to "
           f"me.I am just following orders here", default, "-----", "-----", night, '\n'.join(inventory))
        ui(f"[Voice 2]~ You must be mistaken. I am not the one that you are looking for. I am a simple businessman!",
           default, "-----", "-----", night, '\n'.join(inventory))
        ui(f"[Voice 1]~ I am sorry old man, but my orders are clear. You made angry some very powerful people and now "
           f"its time to pay.", default, "-----", "-----", night, '\n'.join(inventory))
        ui(f"*BAM*\nYou hear the sound of a gun and you immediately rush in the room!", base, "-----", "-----",
           night, '\n'.join(inventory))

        ui(f"~UNCLE BEN!\n*Someone shot uncle ben*\n* You see a masked person taking the door on your left in order "
           f"to escape *", room_1, "-----", "-----", night, '\n'.join(inventory))

        # Create the window and set (text rows, character limit, y,x coordinates for the window)
        loop = True
        while loop:
            counter_win = curses.newwin(4, 84, 25, 30)

            counter_win.addstr("I will: [a] Run after the assassin. [b] Check uncle Ben."
                               "\n \nType [a] or [b]: ")
            counter_win.refresh()

            c = counter_win.getkey()
            if c == "a":
                ui(f"* At once you try to catch the person before he manages to escape *", mafia_run,
                   "-----", "-----", night, '\n'.join(inventory))
                ui(f"* You run as fast as you can and are just a few meters behind the assassin *", mafia_run_two,
                   "-----", "-----", night, '\n'.join(inventory))
                ui(f"* Suddenly the assassin throws towards you a big chinese vase from the corridor "
                   f"and you fall down *", default, "-----", "-----", night, '\n'.join(inventory))
                ui(f"* It takes only a few seconds to get up but the masked assassin is far from gone *", corridor,
                   "-----", "-----", night, '\n'.join(inventory))
                ui(f"* At this point you decide to run back in uncle Ben's office, and hope that is not too late *",
                   b2r, "-----", "-----", night, '\n'.join(inventory))
                loop = False
            elif c == "b":
                ui(f"* You ignore the person escaping and you immediately run to help uncle Ben *", mafia_run, "-----",
                   "-----",
                   night, '\n'.join(inventory))
                loop = False
            else:
                ui(f"* Wrong input try again! Uncle Ben is dying! *", room_1, "-----", "-----", night,
                   '\n'.join(inventory))

        ui(f"* You grab him carefully and he tries to tell you something *", default, "-----", "-----",
           night, '\n'.join(inventory))
        ui(f"~ Listen {menu.main_player.name}...\nWith great power, comes great responsibility! ",
           ben_two, "Uncle Ben", "75", night, '\n'.join(inventory))
        ui(f"~ Don't let them destroy my life's work. \n Don't let them escape!",
           ben_two, "Uncle Ben", "75", night, '\n'.join(inventory))
        ui(f"~ 'The key is in the stars'.....", ben_two, "Uncle Ben", "75",
           night, '\n'.join(inventory))
        ui(f"* Uncle Ben falls unconscious and you can hear footsteps from the corridor *", uncle, "Uncle Ben", "75",
           night, '\n'.join(inventory))

        ui(f"* You turn your back and you see a police officer standing on the door *", default, "Officer Greg",
           "80", night, '\n'.join(inventory))
        ui(f"Officer: You there!", police, "Officer Greg", "85", night, '\n'.join(inventory))

        loop = True
        while loop:
            counter_win = curses.newwin(4, 84, 25, 30)

            counter_win.addstr(" [a] Tell the officer about the assassin\n [b] 'I am innocent' \n [c] Say nothing "
                               "\n Type [a], [b] or [c]: ", curses.A_BOLD)
            counter_win.refresh()

            c = counter_win.getkey().lower()
            if c == "a":
                ui(f"~ I was looking for my uncle and I heard a gunshot from inside the office."
                   f"\n  I entered in the room and I saw a masked person with a gun", player, "Officer Greg", "82",
                   night, '\n'.join(inventory))
                ui(f"~ I was not able to catch the assassin nor help my uncle.", player, "Officer Greg", "82", night,
                   '\n'.join(inventory))
                loop = False
            elif c == "b":
                ui(f"* At the sight of the officer you panic and immediately prepare to tell the truth *", default,
                   "Officer Greg", "82", night, '\n'.join(inventory))
                ui(f"~ I am innocent * You shout panicked * \n~ An assassin killed my uncle, you must find him!",
                   player, "officer Greg", "83", night, '\n'.join(inventory))
                ui(f"* The officer looks att you and seems a bit confused with your reaction *\n Officer: Relax you are"
                   f" not under arrest", police, "officer Greg", "83", night, '\n'.join(inventory))
                loop = False
            elif c == "c":
                ui(f"* For a moment there you freeze and try to process what is going on *", default, "Officer Greg",
                   "82", night, '\n'.join(inventory))
                ui(f"* You decide to not say a word *\n* The officer looks at you and says *", police, "Officer Greg",
                   "85", night, '\n'.join(inventory))
                loop = False
            else:
                ui(f"* That was not a valid choice! Try again!  *", default, "-----", "-----", night,
                   '\n'.join(inventory))

        ui(f"Officer: We received an anonymous phone call about a murder from this house about half an hour ago."
           f"\nWas that you? ", police, "Officer Greg", "85", night, '\n'.join(inventory))
        ui(f"~ Half an hour ago? That's not possible. The murder happened just a few minutes ago!"
           f"\nThere is no way the phone call was made half an hour ago unless.... ", player, "Officer Greg", "85",
           night, '\n'.join(inventory))
        ui(f"Officer: Unless there is an 'impostor amongst us'. "
           f"\n I am afraid that someone within the house is involved in this case.\n We'll need access to the guest "
           f"list to start interrogating everyone", police, "Officer Greg", "89", night, '\n'.join(inventory))
        ui(f"* The police has surrounded the house and conducts one on one interrogations with everyone *"
           f"\n* While you wait for your turn you can talk with the other guests *", transition_two, "-----", "-----",
           night, '\n'.join(inventory))

        ui(f"* The police surrounded the house and conducts one on one interrogations *"
           f"\n* While you wait for your turn you can talk with the other guests *", transition_two, "-----", "-----",
           night, '\n'.join(inventory))

        loop = True
        while loop:
            counter_win = curses.newwin(4, 84, 25, 30)

            counter_win.addstr(f" [a] Talk with a person nearby [b] Wait for your turn"
                               "\n Type [a] or [b]: ", curses.A_BOLD)
            counter_win.refresh()

            c = counter_win.getkey()
            if c == "a":
                ui(f"~ Hello there, my name is {menu.main_player.name}.", player, "-----", "-----", night,
                   '\n'.join(inventory))
                ui(f"~ Hy my name is {menu.civilian_1.name}. How can I help you?", menu.civilian_1.picture,
                   f"{menu.civilian_1.name}", f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                looper = True
                while looper:
                    counter_win = curses.newwin(4, 85, 25, 30)

                    counter_win.addstr(f" [a] Ask about the assassin [b] Ask about uncle Ben [c] Ask about "
                                       f"{menu.civilian_1.name}s' " f"occupation\n [d] 'I have to go...'\n \nType [a], "
                                       f"[b], [c], [d] : ", curses.A_BOLD)
                    counter_win.refresh()

                    q = counter_win.getkey()
                    if q == "a":
                        ui(f"~ So did you see or hear anything weird tonight?", player, f"{menu.civilian_1.name}",
                           f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        ui(f"~ You mean anything related to the assassin?\n Well...I heard that Ben was involved with "
                           f"mafia business and they wanted him dead.", menu.civilian_1.picture,
                           f"{menu.civilian_1.name}", f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        ui(f"~ What makes you say that? Who told you about this story?", player,
                           f"{menu.civilian_1.name}", f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        ui(f"~ Look I would say its more like a rumor rather than the truth.\nIn any case "
                           f"{menu.civilian_2.name} told me about these rumors.", menu.civilian_1.picture,
                           f"{menu.civilian_1.name}", f"{menu.civilian_1.reliability}",
                           night, '\n'.join(inventory))
                        ui(f"~ If you want more details go and ask {menu.civilian_2.name} yourself!\nit's that person "
                           f"there with the {menu.civilian_2.hair} hair and the {menu.civilian_2.eyes} eyes.",
                           menu.civilian_1.picture, f"{menu.civilian_1.name}", f"{menu.civilian_1.reliability}",
                           night, '\n'.join(inventory))
                        ui(f"~ Thanks for your time!", player, f"{menu.civilian_1.name}",
                           f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                    elif q == "b":
                        ui(f"~ Hey did you know Ben?", player, f"{menu.civilian_1.name}",
                           f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        ui(f"~ I first met Ben a few years ago. Back then I was working on a non-profit organisation "
                           f"and we were in need of some money. Ben learned about our cause and immediately donated a"
                           f" large amount of money", menu.civilian_1.picture, f"{menu.civilian_1.name}",
                           f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        ui(f"~ If I may ask, what was the cause of your organisation?", player,
                           f"{menu.civilian_1.name}", f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        ui(f"~ We were mostly developing new technologies for agricultural use. We tried to find new "
                           f"techniques for growing plants, increase production and minimize the cost of farming in "
                           f"general.", menu.civilian_1.picture, f"{menu.civilian_1.name}",
                           f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        ui(f"~ I never thought that Ben was interested in science ", player, f"{menu.civilian_1.name}",
                           f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        ui(f"~ If you want to know more about this you should go and speak with {menu.civilian_2.name}"
                           f"\nit's that person there with the {menu.civilian_2.hair} hair and the "
                           f"{menu.civilian_2.eyes} eyes.", menu.civilian_1.picture, f"{menu.civilian_1.name}",
                           f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        ui(f"~ Thanks for the information", player, f"{menu.civilian_1.name}",
                           f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                    elif q == "c":
                        ui(f"~ So what do you do for work? Are you also a psychiatrist like Ben?", player,
                           f"{menu.civilian_1.name}", f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        ui(f"~ I used to work as a secretary in a non-profit organisation but for the last 3 years I "
                           f"work as a {menu.civilian_1.role}", menu.civilian_1.picture, f"{menu.civilian_1.name}",
                           f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        ui(f"~ That sounds interesting!", player, f"{menu.civilian_1.name}",
                           f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                    elif q == "d":
                        ui(f"~I have to go now", player, f"{menu.civilian_1.name}", f"{menu.civilian_1.reliability}",
                           night, '\n'.join(inventory))
                        ui(f"~ Ok goodbye", menu.civilian_1.picture, f"{menu.civilian_1.name}",
                           f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        looper = False
                    else:
                        ui(f"* That was not a valid choice! Try again! *", default, "-----", "-----",
                           night, '\n'.join(inventory))

                ui(f"* Once you are done speaking with {menu.civilian_1.name} you decide to go and talk with "
                   f"{menu.civilian_2.name} *", default, "-----", "-----", night, '\n'.join(inventory))
                ui(f"~ Hi! My name's {menu.main_player.name} I was talking with {menu.civilian_1.name} about Ben and "
                   f"she told me that you knew him *", player, f"{menu.civilian_2.name}",
                   f"{menu.civilian_2.reliability}", night, '\n'.join(inventory))
                ui(f" Yes I knew Benny quite well. And you must be his nephew am I right?",
                   f"{menu.civilian_2.picture}",
                   f"{menu.civilian_2.name}", f"{menu.civilian_2.reliability}", night, '\n'.join(inventory))
                ui(f"~ Yes that's right.\nI wanted to ask you about these rumors about my uncle.\nDid he really had "
                   f"troubles with the local mafia?", player, f"{menu.civilian_2.name}",
                   f"{menu.civilian_2.reliability}", night, '\n'.join(inventory))
                ui(f" Listen kid, no matter what your uncle told you stay out of this business.\nThere is much you "
                   f"don't know and that is for the best", f"{menu.civilian_2.picture}", f"{menu.civilian_2.name}",
                   f"{menu.civilian_2.reliability - 5}", night, '\n'.join(inventory))
                ui(f" I am really sorry for your uncle but it's best if you forget what happened here today.",
                   f"{menu.civilian_2.picture}", f"{menu.civilian_2.name}", f"{menu.civilian_2.reliability - 10}",
                   night, '\n'.join(inventory))
                loop = False
            elif c == "b":
                loop = False
            else:
                ui(f"* That was not a valid choice! Try again! *", default, "-----", "-----", night,
                   '\n'.join(inventory))

        ui(f"* Suddenly the police comes forward with important information *", default, f"{menu.civilian_2.name}",
           f"{menu.civilian_2.reliability - 10}", night, '\n'.join(inventory))
        ui(f"Officer: Ladies and gentlemen I would like to inform you that we found who was the assassin. ", police,
           "-----", "-----", night, '\n'.join(inventory))
        ui(f"The assassin is {menu.civilian_4.name} Smith. While searching her bag we found a loaded gun and ammunition"
           f" matching the one that was used against Ben Steward\nFurthermore we have evidence that make us believe "
           f"that she has ties with the mafia.", police, "-----", "-----", night, '\n'.join(inventory))
        ui(f" ~ I am innocent, this is a big mistake!\nPlease I am not the assassin\nThis was all a setup!",
           f"{menu.civilian_4.picture}", "-----", "-----", night, '\n'.join(inventory))
        ui(f"* It's late and this was a horrible night *\n* There are many things that don't actually make sense but "
           f"you should probably just move on * ", default, "-----", "-----", night, '\n'.join(inventory))
        ui(f"* You wake up in the morning and you open the TV. *", transition_three, "-----", "-----",
           day, '\n'.join(inventory))
        ui(f"* A new mafia attack on Springfield, similar to the one on uncle Ben's house *\n* On that moment you can "
           f"hear vividly uncle Ben's last words *", tv, "-----", "-----", day, '\n'.join(inventory))
        ui(f"~ Don't let them destroy my life's work. \n Don't let them escape!", ben_two,
           "Uncle Ben", "75", day, '\n'.join(inventory))
        ui(f"~ 'The key is in the stars'.....", uncle, "Uncle Ben", "75", day, '\n'.join(inventory))
        ui(f"~ I wander if there is any clue on uncle Ben's house. There must be something left there to explain what"
           f" happened", default, "-----", "-----", day, '\n'.join(inventory))
        ui(f"* On your way to uncle Ben's house you see a convenience store *\n* Just outside of the store there is an "
           f"old woman asking for help *", store, "-----", "-----", day, '\n'.join(inventory))

        # Start a loop and let the player decide what to do once he sees the old woman/Veronica
        loop = True
        while loop:
            counter_win = curses.newwin(4, 84, 25, 30)

            counter_win.addstr(" [a] Help her [b] Ignore the old woman "
                               "\n \nType [a] or [b]: ")
            counter_win.refresh()

            c = counter_win.getkey()
            if c == "a":
                veronica_meet = True
                ui(f"* you walk towards the convenience store and offer your help *", default,
                   "-----", "-----", day, '\n'.join(inventory))
                ui(f"~ My cat, someone please help my cat!", old_woman, "-----", "-----", day, '\n'.join(inventory))
                ui(f"~ What's going on?", player, "-----", "-----", day, '\n'.join(inventory))
                ui(f"~ My cat fluffy climbed up on the tree and now he can't come down! Please help me!  ", old_woman,
                   "-----", "-----", day, '\n'.join(inventory))
                ui(f"~ I will help you, don't worry!", player, "-----", "-----", day, '\n'.join(inventory))
                looper = True
                while looper:
                    counter_win = curses.newwin(4, 84, 25, 30)

                    counter_win.addstr(" [a] Search for anything that can help you get the cat [b] Climb on the tree"
                                       "\n \nType [a] or [b]: ")
                    counter_win.refresh()

                    f = counter_win.getkey()
                    if f == "a":
                        ui(f"* You look around the place for a while until you see an old ladder *\n* Although a bit "
                           f"unsafe you decide to use it and save the cat *", default, "-----", "-----",
                           day, '\n'.join(inventory))
                        ui(f"* Once you have fluffy in your arms, you safely get down and hand him to his owner *",
                           default, "-----", "-----", day, '\n'.join(inventory))
                        ui(f"~ MY CAT! * shouts the old woman *", default, "-----", "-----", day, '\n'.join(inventory))
                        looper = False
                    elif f == "b":
                        ui(f"* Without thinking about it you decide to try and climb on the tree without any help *",
                           default, "-----", "-----", day, '\n'.join(inventory))
                        ui(f"* Once you have the cat in your arms, you attempt to get down of the tree but you slip "
                           f"and end up on the ground *", default, "-----", "-----", day, '\n'.join(inventory))
                        pl_hel -= 20
                        ui(f"~ MY CAT!\n* shouts the old woman *\n* You are not severely injured but with that fall you"
                           f" could easily break a leg or arm *", default, "-----", "-----", day, '\n'.join(inventory))
                        looper = False
                    else:
                        ui(f"* That was not a valid choice! Try again! *", default, "-----", "-----",
                           day, '\n'.join(inventory))

                ui(f"~ How can I ever repay you for this favour? ", old_woman, "-----", "-----", day,
                   '\n'.join(inventory))
                ui(f"~ It was nothing really.", player, "-----", "-----", day, '\n'.join(inventory))
                ui(f"~ Please come inside the store and get some fruits as a gift from me. \nIt's not much but they are"
                   f" fresh and they taste great!", old_woman, "-----", "-----", day, '\n'.join(inventory))
                ui(f"~ Well I wouldn't say no to some fruits\n~ By the way my name is {menu.main_player.name}", player,
                   "-----", "-----", day, '\n'.join(inventory))
                ui(f"Nice to meet you {menu.main_player.name}! My name is Veronica", old_woman, "Veronica", "85",
                   day, '\n'.join(inventory))
                ui(f"* While you wait in the store you see an old arcade machine *", arcade, "-----", "-----", day,
                   '\n'.join(inventory))
                ui(f"~ Is it ok if I play a few games? ", player, "Veronica", "85", day, '\n'.join(inventory))
                ui(f"~ Yes feel free to play as much as you want.", old_woman, "Veronica", "85", day,
                   '\n'.join(inventory))
                ui(f"~ Ok then lets see what games are available! ", s_screen, "-----", "-----",
                   day, '\n'.join(inventory))
                loop_ah = True
                while loop_ah:
                    arcade_win = curses.newwin(4, 84, 25, 30)

                    arcade_win.addstr(" [a] Play Snake      [b] Play Arakanoid\n [c] Play tetris       "
                                      "[d] 'I don't want to play!'\n \nType [a-d]: ")
                    arcade_win.refresh()

                    q = arcade_win.getkey()
                    if q == "a":
                        snake()
                        ui(f" ", s_screen, "-----", "-----", day, '\n'.join(inventory))
                    elif q == "b":
                        spider_game()
                        ui(f" ", s_screen, "-----", "-----", day, '\n'.join(inventory))
                    elif q == "c":
                        tetris()
                        ui(f" ", s_screen, "-----", "-----", day, '\n'.join(inventory))
                    elif q == "d":
                        loop_ah = False
                    else:
                        arcade_win.addstr("* Wrong input! Please try again! *")
                        arcade_win.refresh()
                        time.sleep(2)

                ui(f"~ Alright! Here is a bag full with fresh and tasty fruits ", old_woman, "Veronica", "90", day,
                   '\n'.join(inventory))
                inventory.append("Fruits")
                ui(f"~ Thanks a lot for this! ", player, "Veronica", "90", day, '\n'.join(inventory))
                ui(f"~ It's the least I could do since you helped me get fluffy down of the tree! You are welcome here "
                   f"any time!", old_woman, "Veronica", "90", day, '\n'.join(inventory))
                ui(f"* After this short break, it's time to focus on today's main goal! *", default, "-----", "-----",
                   day, '\n'.join(inventory))
                loop = False
            elif c == "b":
                ui(f"* You decide to ignore the old woman.*\n * After all why waste your time when you have other more "
                   f"important things to do *", default, "-----", "-----", day, '\n'.join(inventory))
                ui(f"* On your way you find a 10 dollar bill and you pick it up  *",
                   fence, "-----", "-----", "Afternoon", '\n'.join(inventory))
                inventory.append("10 dollar bill")
                loop = False
            else:
                ui(f"* Wrong input try again!  *", store, "-----", "-----", day,
                   '\n'.join(inventory))

        # Go to store to take the keys for uncles house
        # Play video games + add them on main menu
        # Go to the house get clues
        ui(f"* It takes some time but you finally arrive att uncle Ben's house *", mafia_the_t_g, "-----", "-----",
           "Afternoon", '\n'.join(inventory))
        ui(f"* A month later and it all still seems unreal. *\n~ I must find out why the mafia targeted my uncle",
           default, "-----", "-----", "Afternoon", '\n'.join(inventory))
        ui(f"* The house is emptier than ever but at least that makes the investigation easier *", mafia_the_t_g,
           " ", " ", "Afternoon", '\n'.join(inventory))

        # Set a big loop and let the player explore the house
        # Here the player will find the clues needed to progress the story or the assassin will show and kill the player
        loop = True
        while loop:
            # Create an empty list to store the necessary items to progress the game
            # In total there are 6 items that can be added to the list but only 4 can be acquired for progression.
            needed_items = []

            counter_win = curses.newwin(4, 84, 25, 30)
            # Give the player choices for the places where clues may be hidden
            counter_win.addstr("I will: [a] Search the office upstairs. [b] Search the living room.\n      "
                               " [c] Search the kitchen. [d] Search staffroom\n \nType [a-d]: ")
            counter_win.refresh()

            c = counter_win.getkey()
            # Start a branch for going upstairs and search the office
            if c == "a":
                # Get the number of items from the list
                total_needed_items = len(inventory)
                # If the inventory is full start the next act
                if total_needed_items >= 7:
                    loop = False
                else:
                    # Let the user to go upstairs and explore
                    ui(f"* While you go upstairs to uncle Ben's office, the last of his words come in mind *\n'~The key"
                       f" is in the stars'", base_room, "-----", "-----", "Afternoon", '\n'.join(inventory))
                    ui(f"* You arrive out of the office and open the door *", base, "-----", "-----", "Afternoon",
                       '\n'.join(inventory))
                    ui(f"~ Of course uncle Ben had set a second fireplaces in his house.... \n~ In any case lets start "
                       f"looking for any clues", b_office, "-----", "-----", "Afternoon", '\n'.join(inventory))
                    looper = True
                    while looper:
                        office_win = curses.newwin(4, 84, 25, 30)
                        # Give the player choices for the places where clues may be hidden
                        office_win.addstr("I will: [a] Search the bookcase. [b] Search uncles desk.\n      "
                                          " [c] Search the safe. [d] I want to go somewhere else\n \nType [a-d]: ")
                        office_win.refresh()

                        c = office_win.getkey()
                        # Search the bookcases
                        if c == "a":
                            ui(f"* There are plenty books in this bookcase *", default, "-----", "-----", "Afternoon",
                               '\n'.join(inventory))
                            # Set the morse code book as an str that can be equipped in the inventory
                            # The book is essential for decoding the painting code found in the living room
                            morse_code_book = "Morse code book"
                            # Control if the player entered the room before and if the player took the morse code book
                            # If player enters for first time/returned to pick the book then spawn it in the bookshelf
                            if morse_code_book not in inventory:
                                ui(f"* You search one by one the books and find one that's quite bizarre. It's a book "
                                   f"about morse code *\n~ I didn't know that uncle was interested in morse code. "
                                   f"That's interesting.", bookshelf, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                                loop_ah = True
                                while loop_ah:
                                    book_win = curses.newwin(4, 84, 25, 30)

                                    book_win.addstr("Take the Morse code book?: [a] Yes. [b] No.\n \nType [a-b]: ")
                                    book_win.refresh()

                                    c = book_win.getkey()
                                    if c == "a":
                                        needed_items.append("Morse code book")
                                        inventory.append("Morse code book")
                                        loop_ah = False
                                    elif c == "b":
                                        loop_ah = False
                                    else:
                                        ui(f" Invalid choice! Please try again! ", default, "-----", "-----",
                                           "Afternoon", '\n'.join(inventory))
                                ui(f"¨~~Lets see what else I can find here", b_office, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                            # If the player enters the room x times and at some point took the lighter then show
                            # an empty drawer
                            elif morse_code_book in inventory:
                                ui(f"* Just random books nothing to see here *", bookshelf, "-----", "-----",
                                   "Afternoon", '\n'.join(inventory))
                                ui(f"~ ok I think I am done with this part of the room ", player, "-----", "-----",
                                   "Afternoon",
                                   '\n'.join(inventory))
                        # Search the desk
                        elif c == "b":
                            ui(f"~ Without a doubt there must be something important here", desk, "-----", "-----",
                               "Afternoon", '\n'.join(inventory))
                            # Set the paper as an str object that can be append in the players inventory
                            # If the player got the lighter from the living room then it could be possible to reveal the
                            # hidden names written in the paper
                            paper = "Paper"
                            # Control if the player entered the room before and if the player took the secrete paper
                            # If player enters for first time/returned to pick the paper, show the paper on the shelf
                            if paper not in inventory:
                                ui(f"* You search for a while and find a mysterious piece of paper *", papper, "-----",
                                   "-----", "Afternoon", '\n'.join(inventory))
                                loop_ah = True
                                while loop_ah:
                                    paper_win = curses.newwin(4, 84, 25, 30)

                                    paper_win.addstr("Take the mystery paper?: [a] Yes. [b] No.\n \nType [a-b]: ")
                                    paper_win.refresh()

                                    c = paper_win.getkey()
                                    if c == "a":
                                        needed_items.append("Paper")
                                        inventory.append("Paper")
                                        loop_ah = False
                                    elif c == "b":
                                        loop_ah = False
                                    else:
                                        ui(f" Invalid choice! Please try again! ", default, "-----", "-----",
                                           "Afternoon", '\n'.join(inventory))
                                ui(f" ~ Let's check if there is anything else left to find! ", desk, "-----", "-----",
                                   "Afternoon", '\n'.join(inventory))
                            # If the player enters the room x times and already took the secrete paper then show
                            # an empty desk
                            elif paper in inventory:
                                ui(f"* There are only random papers and tax books on this desk. Nothing interesting to "
                                   f"see! *", desk, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                ui(f"~ ok I think I am done with this part of the room ", default, "-----", "-----",
                                   "Afternoon", '\n'.join(inventory))
                        # Let the player try and open the safe
                        elif c == "c":
                            ui(f"~ Well that's a big safe...", safe, "-----", "-----", "Afternoon",
                               '\n'.join(inventory))
                            ui(f"~ I wonder what's inside there...", security_safe, "-----",
                               "-----", "Afternoon", '\n'.join(inventory))
                            loop_ah = True
                            while loop_ah:
                                safe_win = curses.newwin(4, 84, 25, 30)

                                safe_win.addstr(
                                    "The combinations seem endless but there is only one that will open the safe."
                                    "\n[Type quit to leave the safe] The code is : ")
                                safe_win.refresh()
                                curses.echo()
                            # .decode() is used because originally the [c = safe_win.gets()] returns the input in bits
                            # Ex. Input= Hello, without decoding returns b'Hello' and thous doesnt work in the if/elif
                                c = safe_win.getstr().decode()
                            # If the user find the code by chance or from the painting then open the safe
                                if c == "1974":
                                    # Set the diary as true and let the player read about the mafia
                                    secret_diary = True
                                    ui(f"* Inside the safe you find uncle Ben's diary and a lot of cash *.\n ~ I wonder"
                                       f" if there is information here that will help me find the reason for uncles "
                                       f"assassination...", safe, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                    ui(f"* You read many pages until you find the last entry *", diary, "-----",
                                       "-----", "Afternoon", '\n'.join(inventory))
                                    ui(f" ' This is my last entry on this diary. I believe that they will soon get me.",
                                       diary, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                    ui(f"'Many, years ago I made a deal with the local mafia and I allowed them to use "
                                       f"one of my stores as a storage for hiding drugs in return for a large sum of"
                                       f" money  '", diary, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                    ui(f"' What I did was wrong and that's why I decided last month to stop this "
                                       f"contract of ours. The head of the mafia Don Emilio, was not pleased with my "
                                       f"decision and threatened me.' ", diary, "-----", "-----", "Afternoon",
                                       '\n'.join(inventory))
                                    ui(f"' I tried to negotiate and even threaten them back, claiming that I will speak"
                                       f" with the police but I am afraid that made them even more angry. ", diary,
                                       "-----", "-----", "Afternoon", '\n'.join(inventory))
                                    ui(f"' Over the last weeks they sent two of their trusted mafioso's to follow me "
                                       f"and record every single move that I make' ", diary, "-----", "-----",
                                       "Afternoon", '\n'.join(inventory))
                                    ui(f"' Last night, a loud noise woke me up. I got up and looked out of the window "
                                       f"and I am sure that I saw someone hiding in the woods' ", diary, "-----",
                                       "-----", "Afternoon", '\n'.join(inventory))
                                    ui(f"' In case that someone finds this diary and I am dead, please sent this people"
                                       f" in prison' ", diary, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                    ui(f"* In the very last page of the diary you read the names: {menu.mafioso_1.name}"
                                       f" Smith, Don Emilio Bianchi, Marco Marconi, Christina Colombo, Petro Rossi *",
                                       diary, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                    ui(f"* These are the names of the richest and most powerful families in the entire "
                                       f"city! *",
                                       default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                    ui(f"~ If what Uncle wrote here is true then that explains why these families are "
                                       f"some of the wealthiest in the entire country.\n I should talk with the "
                                       f"police!", player, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                    loop_ah = False
                                    looper = False
                                    loop = False
                            # If player has no clue about the code then let them break the loop and do something else
                                elif c == "quit":
                                    loop_ah = False
                                # Generic frustration when the safe code is not correct.
                                else:
                                    ui(f"* Damn it! Wrong pass *", player, "-----", "-----", "Afternoon",
                                       '\n'.join(inventory))
                        elif c == "d":
                            looper = False
                        else:
                            ui(f"* Invalid choice! Please try again!  *", default, "-----", "-----", "Afternoon",
                               '\n'.join(inventory))
            # Start a branch for searching the living room
            elif c == "b":
                # Get the number of items from the list if the inventory is full the start act 3
                total_needed_items = len(inventory)
                if total_needed_items >= 7:
                    loop = False
                else:
                    ui(f"* The living room is a place were you could hide a lot of things. *\n* There might be "
                       f"something interesting here *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                    ui(f"~ There must be a clue somewhere around here", living_room, "-----", "-----", "Afternoon",
                       '\n'.join(inventory))
                    looper = True
                    while looper:
                        sub_win = curses.newwin(4, 84, 25, 30)

                        sub_win.addstr("I will: [a] Search near the fireplace. [b] Just look around.\n      "
                                       " [c] I want to look for clues somewhere else \nType [a-c]: ")
                        sub_win.refresh()

                        c = sub_win.getkey()
                        # Search for clues around the fireplace
                        if c == "a":
                            ui(f"* The fireplace is somewhere were you could hide a lot of things *\n* There might be "
                               f"something good here *", fireplace, "-----", "-----", "Afternoon", '\n'.join(inventory))
                            # Set the lighter object as a str
                            lighter = "Lighter"
                            # Check if the player entered the room before and if the player took the lighter If player
                            # enters for first time or returned to pick the lighter then show lighter in the drawer
                            if lighter not in inventory:
                                ui(f"* Near the fireplace you find a small drawer. You open it and inside you find"
                                   f" only a lighter *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                loop_ah = True
                                while loop_ah:
                                    lighter_win = curses.newwin(4, 84, 25, 30)

                                    lighter_win.addstr("Take the lighter?: [a] Yes. [b] No.\n \nType [a-b]: ")
                                    lighter_win.refresh()

                                    c = lighter_win.getkey()
                                    if c == "a":
                                        needed_items.append("Lighter")
                                        inventory.append("Lighter")
                                        loop_ah = False
                                    elif c == "b":
                                        loop_ah = False
                                    else:
                                        ui(f" Invalid choice! Please try again! ", default, "-----", "-----",
                                           "Afternoon", '\n'.join(inventory))
                            # If the player enters the room x times and at some point took the lighter then
                            # show an empty drawer
                            elif lighter in inventory:
                                ui(f"* You open a small drawer but there is nothing important in there. *", default,
                                   "-----", "-----", "Afternoon", '\n'.join(inventory))
                                ui(f"~ ok I think I am done with this room ", player, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                        elif c == "b":
                            ui(f"* Just by looking around the massive room you notice the artwork on the walls *",
                               living_room,
                               "-----", "-----", "Afternoon", '\n'.join(inventory))
                            ui(f"* At some point you notice a weird painting on the wall *", room_O,
                               "-----", "-----", "Afternoon", '\n'.join(inventory))
                            # Set the key object as a str
                            key_one = "Key"
                            # Control if the player entered the room before and if the player took the key
                            # If player enters for first time or returned to pick the key then show key on the painting
                            if key_one not in inventory:
                                ui(f"* The painting seems to represent the stars in the sky and on it you find a start "
                                   f"shaped key * "f"\n~ Someone hid the key on the painting....", painting, "-----",
                                   "-----", "Afternoon", '\n'.join(inventory))
                                loop_ah = True
                                while loop_ah:
                                    key_win = curses.newwin(4, 84, 25, 30)

                                    key_win.addstr("Take the key?: [a] Yes. [b] No.\n \nType [a-b]: ")
                                    key_win.refresh()

                                    c = key_win.getkey()
                                    if c == "a":
                                        # Append the key in the needed items to progress the game
                                        needed_items.append("Key")
                                        # Add the key in the inventory
                                        inventory.append("Key")
                                        loop_ah = False
                                    elif c == "b":
                                        loop_ah = False
                                    else:
                                        ui(f" Invalid choice! Please try again! ", default, "-----", "-----",
                                           "Afternoon", '\n'.join(inventory))
                            # If the player enters the room x times and at some point took the lighter then show
                            # an empty drawer
                            elif key_one in inventory:
                                ui(f"* It's just an weird painting. Nothing to see here *", painting, "-----", "-----",
                                   "Afternoon", '\n'.join(inventory))
                                ui(f"~ ok I think I am done with this room ", player, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                        elif c == "c":
                            looper = False
                        else:
                            ui(f" Invalid choice! Please try again! ", default, "-----", "-----", "Afternoon",
                               '\n'.join(inventory))
            # Start a branch for searching the kitchen
            elif c == "c":
                # Get the number of items from the list
                total_needed_items = len(inventory)
                if total_needed_items >= 7:
                    loop = False
                else:
                    # Let the player explore the kitchen
                    ui(f"* The kitchen is always a good place to visit *", default, "-----", "-----", "Afternoon",
                       '\n'.join(inventory))
                    mafioso_item = f"{menu.mafioso_1.item}"
                    # Check if the player found the item linked to the mafioso and depending on that either show
                    # nothing within the kitchen or let the user enter and grab the item
                    if mafioso_item not in inventory:
                        ui(f"* While there is not much here, you find out a {menu.mafioso_1.item} in the ground *",
                           kitchen, "-----", "-----", "Afternoon", '\n'.join(inventory))
                        loop_ah = True
                        while loop_ah:
                            item_win = curses.newwin(4, 84, 25, 30)
                            # Give the player choices for the places where clues may be hidden
                            item_win.addstr(f"Take {menu.mafioso_1.item}?: [a] Yes,  [b] No \nType [a-b]: ")
                            counter_win.refresh()

                            c = item_win.getkey()

                            if c == "a":
                                # Set clue on the needed items for the progression of the game
                                needed_items.append("maf_item")
                                inventory.append(f"{menu.mafioso_1.item}")
                                loop_ah = False
                            elif c == "b":
                                loop_ah = False
                            else:
                                ui(f"* Invalid choice! Please try again!  *", default, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                        ui(f"~ Lets keep searching!", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                    elif mafioso_item in inventory:
                        ui(f"~ Unfortunately there is nothing to do here\nMaybe I should drop by the convenience "
                           f"store later and grab something to eat!", player, "-----", "-----", "Afternoon",
                           '\n'.join(inventory))
            # Start a branch for searching the staffroom
            elif c == "d":
                # Get the number of items from the list
                total_needed_items = len(inventory)
                if total_needed_items >= 7:
                    loop = False
                else:
                    # Set a clue [assassins hair] in an str and then give ability to store it in the inventory
                    mafioso_hair = "A strand of black hair"
                    # If the player enter for the first time give them the ability to choose if they want a clue
                    if mafioso_hair not in inventory:
                        ui(f"~ Uncle Ben trusted a lot his staff. Maybe I shouldn't search here.", default, "-----",
                           "-----", "Afternoon", '\n'.join(inventory))
                        ui(f"* While you walk around the room you find out a {menu.mafioso_1.hair} strand of hair in "
                           f"the ground *", staff_room, "-----", "-----", "Afternoon", '\n'.join(inventory))
                        loop_ah = True
                        while loop_ah:
                            hair_win = curses.newwin(4, 84, 25, 30)
                            # Give the player choices for the places where clues may be hidden
                            hair_win.addstr(f"Take black strand of hair?: [a] Yes,  [b] No \nType [a-b]: ")
                            hair_win.refresh()

                            c = hair_win.getkey()

                            if c == "a":
                                # Add item to needed items list to progress the game
                                needed_items.append("hair")
                                inventory.append(f"A strand of {menu.mafioso_1.hair} hair")
                                loop_ah = False
                            elif c == "b":
                                loop_ah = False
                            else:
                                ui(f"* Invalid choice! Please try again!  *", default, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                        ui(f"~ Lets see what else is around in this house!", default, "-----", "-----", "Afternoon",
                           '\n'.join(inventory))
                    # If the player has been here and has taken the hair send him to the other rooms
                    elif mafioso_hair in inventory:
                        ui(f"~ The staff room seems nice but there is nothing for me here!", player, "-----", "-----",
                           "Afternoon", '\n'.join(inventory))
            else:
                ui(f"* Invalid choice! Please try again!  *", default, "-----", "-----", "Afternoon",
                   '\n'.join(inventory))

        ui(f"* While you are still looking around the house for clues you hear a window breaking *", default, "-----",
           "-----", "Afternoon", '\n'.join(inventory))
        ui(f"~ Did someone break in the house? \n~ What should I do now?", player, "-----", "-----", "Afternoon",
           '\n'.join(inventory))
        # Start a loop for the 3rd act of the game
        # Here the player chooses how to respond to the house intruder.
        # Based on the choice the player may 1) run-hide-escape 2)Hide-Fight-Die 3)Instantly die
        loop = True
        while loop:
            counter_win = curses.newwin(4, 84, 25, 30)
            # Give the player choices for the places where clues may be hidden
            counter_win.addstr("I will: [a] Try to get out of the house [b] Hide.\n [c] Do nothing.\n \nType [a-d]: ")
            counter_win.refresh()

            c = counter_win.getkey()
            # Players tries to escape from the house unnoticed
            # Eventually ends up out of the house
            # If meanwhile the player finds the code for the safe he can instantly end the game
            if c == "a":
                ui(f"~ I should better run and get out of the house! ", player, "-----", "-----", "Afternoon",
                   '\n'.join(inventory))
                ui(f"* While you try to escape you hear footsteps from the next room *", default, "-----", "-----",
                   "Night", '\n'.join(inventory))
                # Let the player choose a place to hide
                looper = True
                while looper:
                    run_win = curses.newwin(4, 84, 25, 30)
                    # Give the player choices for the places where clues may be hidden
                    run_win.addstr("I will: [a] Hide in the Staff room. [b] Hide in the kitchen.\n [c] Hide in the "
                                   "living room.\n \nType [a-c]: ")
                    run_win.refresh()

                    q = run_win.getkey()
                    # Hide in the staff room
                    if q == "a":
                        ui(f"* Without even thinking about it you quickly hide in a closet in the staff room *",
                           default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                        ui(f"~ Ok I m probably safe here. Now what though... ", player, "-----", "-----", "Afternoon",
                           '\n'.join(inventory))
                        # Simple while loop for the last decision of the player
                        # Call the police or run towards the front door
                        loop_ah = True
                        while loop_ah:
                            r_win = curses.newwin(4, 84, 25, 30)
                            # Display the choices to the player
                            r_win.addstr(
                                "I should: [a] Stay hidden and call the police. [b] Run towards the front door"
                                "\n \nType [a-b]: ")
                            r_win.refresh()

                            f = r_win.getkey()
                            # Let the player call the police and wait for them
                            if f == "a":
                                ui(f"* At once you pick up your cellphone and call 911 *", default, "-----", "-----",
                                   "Afternoon", '\n'.join(inventory))
                                ui(f"* The police tells you to wait were you are until they sent help *",
                                   default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                ui(f"* While you wait hidden in the closet you see the intruder enter the room *",
                                   mafioso, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                ui(f"* He seems to be searching for something in this room *", mafioso, "-----",
                                   "-----", "Afternoon", '\n'.join(inventory))
                                re_loop = True
                                while re_loop:
                                    re_win = curses.newwin(4, 84, 25, 30)
                                    # Display the choices to the player
                                    re_win.addstr(
                                        "I should: [a] Stay hidden and hope for the best. [b] Try to sneak out of the "
                                        "room in a Metal gear solid fashion\n \nType [a-b]: ")
                                    re_win.refresh()

                                    f = r_win.getkey()
                                    if f == "a":
                                        ui(f"* The man is searching all over the room and and he sounds frustrated. *"
                                           f"\n* Suddenly he makes a turn and looks in the closet where you are hiding "
                                           f"*", mafia_the_t_g, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"* With one quick move he opens the closet's door and sees you *",
                                           mafioso, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"~ I was looking for you all this time! You shouldn't have come back in "
                                           f"this house", mafioso, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"~ You will never get away with this. Neither you nor the others that hired"
                                           f" you", player, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"* Within a second the man takes his gun and shoots you three times *\n "
                                           f"* You are now dead *", gun, "-----", "-----", "Afternoon",
                                           '\n'.join(inventory))
                                        ui(f"* Bad luck {menu.main_player.name}! Feel free to try again or even choose"
                                           f" a different path *", game_over, "-----", "-----", "Afternoon",
                                           '\n'.join(inventory))
                                        quit()
                                    elif f == "b":
                                        ui(f"* You wait for a while hidden in the closet and you decide to secretly get"
                                           f" out *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"* It may be dangerous but no matter the odds you decide to run towards the"
                                           f" main entrance and get out of the house *", default, "-----", "-----",
                                           "Afternoon", '\n'.join(inventory))
                                        ui(f"* Without making any noise at all you get to the entrance and slowly open "
                                           f"the door and get out *", default, "-----", "-----", "Afternoon",
                                           '\n'.join(inventory))
                                        re_loop = False
                                        loop = False
                                        loop_ah = False
                                    else:
                                        ui(f"* Invalid input please try again *", default, "-----", "-----",
                                           "Afternoon", '\n'.join(inventory))
                            # Let the player try and run to the main door
                            elif f == "b":
                                ui(f"* You wait for a while hidden in a closet and there are no signs of intruders in"
                                   f" the house *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                ui(f"* It may be dangerous but no matter the odds you decide to run towards the main "
                                   f"entrance and get out of the house *", default, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                                ui(f"* Without making any noise at all you get to the entrance and slowly open the "
                                   f"door and get out *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                loop_ah = False
                                loop = False
                            else:
                                ui(f"* Invalid input please try again! *", default, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                        looper = False
                    elif q == "b":
                        ui(f"* Without even thinking about it you quickly hide in a closet in the kitchen *",
                           default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                        ui(f"~ Ok I m probably safe here. Now what though... ", player, "-----", "-----", "Afternoon",
                           '\n'.join(inventory))
                        # Simple while loop for the last decision of the player
                        # Call the police or run towards the front door
                        loop_ah = True
                        while loop_ah:
                            r_win = curses.newwin(4, 84, 25, 30)
                            # Display the choices to the player
                            r_win.addstr(
                                "I should: [a] Stay hidden and call the police. [b] Run towards the front door"
                                "\n \nType [a-b]: ")
                            r_win.refresh()

                            f = r_win.getkey()
                            # Let the player call the police and wait for them
                            if f == "a":
                                ui(f"* At once you pick up your cellphone and call 911 *", default, "-----", "-----",
                                   "Afternoon", '\n'.join(inventory))
                                ui(f"* The police tells you to wait were you are until they sent help *",
                                   default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                ui(f"* While you wait hidden in the closet you see the intruder enter the room *",
                                   mafioso, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                ui(f"* He seems to be searching for something in this room *", mafioso, "-----",
                                   "-----", "Afternoon", '\n'.join(inventory))
                                re_loop = True
                                while re_loop:
                                    re_win = curses.newwin(4, 84, 25, 30)
                                    # Display the choices to the player
                                    re_win.addstr(
                                        "I should: [a] Stay hidden and hope for the best. [b] Try to sneak out of the "
                                        "room in a Metal gear solid fashion\n \nType [a-b]: ")
                                    re_win.refresh()

                                    f = r_win.getkey()
                                    if f == "a":
                                        ui(f"* The man is searching all over the room and and he sounds frustrated. *"
                                           f"\n* Suddenly he makes a turn and looks in the closet where you are hiding "
                                           f"*", mafia_the_t_g, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"* With one quick move he opens the closet's door and sees you *",
                                           mafioso, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"~ I was looking for you all this time! You shouldn't have come back in "
                                           f"this house", mafioso, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"~ You will never get away with this. Neither you nor the others that hired"
                                           f" you", player, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"* Within a second the man takes his gun and shoots you three times *\n "
                                           f"* You are now dead *", gun, "-----", "-----", "Afternoon",
                                           '\n'.join(inventory))
                                        ui(f"* Bad luck {menu.main_player.name}! Feel free to try again or even choose"
                                           f" a different path *", game_over, "-----", "-----", "Afternoon",
                                           '\n'.join(inventory))
                                        quit()
                                    elif f == "b":
                                        ui(f"* You wait for a while hidden in the closet and you decide to secretly get"
                                           f" out *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"* It may be dangerous but no matter the odds you decide to run towards the"
                                           f" main entrance and get out of the house *", default, "-----", "-----",
                                           "Afternoon", '\n'.join(inventory))
                                        ui(f"* Without making any noise at all you get to the entrance and slowly open "
                                           f"the door and get out *", default, "-----", "-----", "Afternoon",
                                           '\n'.join(inventory))
                                        re_loop = False
                                        loop = False
                                        loop_ah = False
                                    else:
                                        ui(f"* Invalid input please try again *", default, "-----", "-----",
                                           "Afternoon", '\n'.join(inventory))
                            # Let the player try and run to the main door
                            elif f == "b":
                                ui(f"* You wait for a while hidden in a closet and there are no signs of intruders in"
                                   f" the house *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                ui(f"* It may be dangerous but no matter the odds you decide to run towards the main "
                                   f"entrance and get out of the house *", default, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                                ui(f"* Without making any noise at all you get to the entrance and slowly open the "
                                   f"door and get out *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                loop_ah = False
                                loop = False
                            else:
                                ui(f"* Invalid input please try again! *", default, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                        looper = False
                    # Player hides in the living room
                    elif q == "c":
                        ui(f"* Without even thinking about it you quickly hide in a closet in the living room *",
                           default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                        ui(f"~ Ok I m probably safe here. Now what though... ", player, "-----", "-----", "Afternoon",
                           '\n'.join(inventory))
                        # Simple while loop for the last decision of the player
                        # Call the police or run towards the front door
                        loop_ah = True
                        while loop_ah:
                            r_win = curses.newwin(4, 84, 25, 30)
                            # Display the choices to the player
                            r_win.addstr(
                                "I should: [a] Stay hidden and call the police. [b] Run towards the front door"
                                "\n \nType [a-b]: ")
                            r_win.refresh()

                            f = r_win.getkey()
                            # Let the player call the police and wait for them
                            if f == "a":
                                ui(f"* At once you pick up your cellphone and call 911 *", default, "-----", "-----",
                                   "Afternoon", '\n'.join(inventory))
                                ui(f"* The police tells you to wait were you are until they sent help *",
                                   default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                ui(f"* While you wait hidden in the closet you see the intruder enter the room *",
                                   mafioso, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                ui(f"* He seems to be searching for something in this room *", mafioso, "-----",
                                   "-----", "Afternoon", '\n'.join(inventory))
                                re_loop = True
                                while re_loop:
                                    re_win = curses.newwin(4, 84, 25, 30)
                                    # Display the choices to the player
                                    re_win.addstr(
                                        "I should: [a] Stay hidden and hope for the best. [b] Try to sneak out of the "
                                        "room in a Metal gear solid fashion\n \nType [a-b]: ")
                                    re_win.refresh()

                                    f = r_win.getkey()
                                    if f == "a":
                                        ui(f"* The man is searching all over the room and and he sounds frustrated. *"
                                           f"\n* Suddenly he makes a turn and looks in the closet where you are hiding "
                                           f"*", mafia_the_t_g, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"* With one quick move he opens the closet's door and sees you *",
                                           mafioso, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"~ I was looking for you all this time! You shouldn't have come back in "
                                           f"this house", mafioso, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"~ You will never get away with this. Neither you nor the others that hired"
                                           f" you", player, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"* Within a second the man takes his gun and shoots you three times *\n "
                                           f"* You are now dead *", gun, "-----", "-----", "Afternoon",
                                           '\n'.join(inventory))
                                        ui(f"* Bad luck {menu.main_player.name}! Feel free to try again or even choose"
                                           f" a different path *", game_over, "-----", "-----", "Afternoon",
                                           '\n'.join(inventory))
                                        quit()
                                    elif f == "b":
                                        ui(f"* You wait for a while hidden in the closet and you decide to secretly get"
                                           f" out *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"* It may be dangerous but no matter the odds you decide to run towards the"
                                           f" main entrance and get out of the house *", default, "-----", "-----",
                                           "Afternoon", '\n'.join(inventory))
                                        ui(f"* Without making any noise at all you get to the entrance and slowly open "
                                           f"the door and get out *", default, "-----", "-----", "Afternoon",
                                           '\n'.join(inventory))
                                        re_loop = False
                                        loop = False
                                        loop_ah = False
                                    else:
                                        ui(f"* Invalid input please try again *", default, "-----", "-----",
                                           "Afternoon", '\n'.join(inventory))
                            # Let the player try and run to the main door
                            elif f == "b":
                                ui(f"* You wait for a while hidden in a closet and there are no signs of intruders in"
                                   f" the house *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                ui(f"* It may be dangerous but no matter the odds you decide to run towards the main "
                                   f"entrance and get out of the house *", default, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                                ui(f"* Without making any noise at all you get to the entrance and slowly open the "
                                   f"door and get out *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                loop_ah = False
                                loop = False
                            else:
                                ui(f"* Invalid input please try again! *", default, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                        looper = False
            # The player hides and then takes a series of decisions that either kill him or save him.
            # If the player survives the he ends up out of the house with the police
            # If meanwhile the player finds the code for the safe he can instantly end the game
            elif c == "b":
                ui(f"* The best thing to do is to quickly hide in the closet and see what is going on *", default,
                   "-----", "-----", "Afternoon", '\n'.join(inventory))
                ui(f"* The time passes and suddenly someone enters the room and is searching for either you or "
                   f"something completely else *\n* Unfortunately its too dark and you can't really see the person nor"
                   f" what exactly is happening*", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                loop_ah = True
                while loop_ah:
                    r_win = curses.newwin(4, 84, 25, 30)
                    # Give the player choices for the places where clues may be hidden
                    r_win.addstr(
                        "I should: [a] Stay hidden and try to call the police when possible. [b] Try to fight the"
                        " intruder without any weapons\n \nType [a-b]: ")
                    r_win.refresh()

                    f = r_win.getkey()
                    if f == "a":
                        ui(f"* You wait and wait and after a while you pick up your cellphone and call 911 *", default,
                           "-----", "-----", "Afternoon", '\n'.join(inventory))
                        ui(f"* The police informs you to wait were you are and wait until they sent you help *",
                           default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                        ui(f"* You wait for a while hidden in a closet and there are no signs of intruders in the"
                           f" house *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                        ui(f"* It may be dangerous but no matter the odds you decide to run towards the main "
                           f"entrance and get out of the house *", default, "-----", "-----", "Afternoon",
                           '\n'.join(inventory))
                        ui(f"* Without making any noise at all you get in the entrance and slowly open the door and get"
                           f" outside *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                        loop_ah = False
                        loop = False
                    elif f == "b":
                        ui(f"* Without hesitation you get out of the closets safety and rush out *", default, "-----",
                           "-----", "Afternoon", '\n'.join(inventory))
                        ui(f"* The once mysterious figure in the room can now be easily seen *"
                           f"\n[Mysterious man]: You must be {menu.main_player.name} I assume....\n You know, if you "
                           f"had stayed hidden I would have left you alone. Now you give me no other choice", mafioso,
                           "-----", "-----", "Afternoon", '\n'.join(inventory))
                        ui(f"* You hit the man as hard as you can but it's pointless! *\n* After all you are just a "
                           f"simple {menu.main_player.role} not a fighter *", player, "-----", "-----", "Afternoon",
                           '\n'.join(inventory))
                        ui(f"* In the very end you try to land a few more hits but it's late. *\n The assassin takes"
                           f" his gun and shoots you two times ", gun, "-----", "-----", "Afternoon",
                           '\n'.join(inventory))
                        ui(f"* Bad luck {menu.main_player.name} you lost! Feel free to try again or even choose"
                           f" a different path *", game_over, "-----", "-----", "Afternoon", '\n'.join(inventory))
                        quit()
                    else:
                        ui(f"~ Invalid input please try again!", default, "-----", "-----", "Afternoon",
                           '\n'.join(inventory))
            # The player does nothing and dies
            elif c == "c":
                ui(f"* For some reason you decided to do nothing..... *", player, "-----", "-----", "Afternoon",
                   '\n'.join(inventory))
                ui(f"* You are completely frozen and can't escape at this point *", default, "-----", "-----",
                   "Afternoon", '\n'.join(inventory))
                ui(f"* Suddenly you see a tall figure coming out of the other room *", default, "-----", "-----",
                   "Afternoon", '\n'.join(inventory))
                ui(f" [Mysterious man]: You made a big mistake by coming here friend ", mafioso, "-----", "-----",
                   "Afternoon", '\n'.join(inventory))
                ui(f"~ Oh please don't!\n* BAM *\n You got shot two times ", mafia_the_t_g, "-----", "-----",
                   "Afternoon", '\n'.join(inventory))
                ui(f"* Thanks for playing 'Mafia: The terminal game' *\n* Feel free to play again and try the other "
                   f"choices or just play the mini-games from the main menu*", game_over, "-----", "-----", "Afternoon",
                   '\n'.join(inventory))
                quit()
            else:
                ui(f"~ Invalid input please try again!", default, "-----", "-----", "Afternoon", '\n'.join(inventory))

        ui(f" ~ You there! What are you doing here? Why are you sneaking out of your uncles house"
           f" like that?\n* Its officer Greg *", police, "Officer Greg", "80", "Afternoon",
           '\n'.join(inventory))
        ui(f"- I came in order to collect some books that I left here a few months ago but someone"
           f" broke in the house!. You have to stop him!", player, "Officer Greg", "80",
           "Afternoon", '\n'.join(inventory))
        ui(f"~ One of the neighbors saw a strange man entering the house with a gun and called us."
           f" I assume they were right ", police, "-----", "-----",
           "Afternoon", '\n'.join(inventory))
        ui(f"* Officer Greg and another officer enter the house while you wait outside *", default,
           "-----", "-----", "Afternoon", '\n'.join(inventory))

        # show clues to police, gather all back and vote one out
        ui(f"* Suddenly you hear a gunshot from inside the house * \n ", default, "-----", "-----", "Afternoon",
           '\n'.join(inventory))
        ui(f"* Officer Greg gets out of the house and run directly to his car in order to call for backup * \n ",
           default, "-----", "-----", "Afternoon", '\n'.join(inventory))
        ui(f" At this point the story went too far and the author got extremely bored to the point were we had to hire "
           f"a new one. Here's a quick summary of what happened later on", mafia_the_t_g, "-----", "-----", "Afternoon",
           '\n'.join(inventory))
        ui(f"* The mafioso that tried to kill you shot officer Greg on his shoulder. once officer greg was out he asked"
           f" for backup and soon after a huge police chase started. The mafioso was eventually shot and was sent to "
           f"jail * \n ", mafioso, "-----", "-----", "Afternoon", '\n'.join(inventory))
        ui(f"* The police interrogated the mafioso but he didn't want to to betray the mafia. Because of that the"
           f" police gathered all suspects in the police station and now it's you time to shine * \n ", mafia_the_t_g,
           "-----", "-----", "Afternoon", '\n'.join(inventory))
        ui(f"* All suspects are gathered in a secrete location and you must use the clues you gathered in order to find"
           f" the rest mafia members * \n ", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
        ui(f"~ I should better get to know the others before we start the voting process \n ", player, "-----",
           "-----", "Afternoon", '\n'.join(inventory))
        # Start talking with people and add staff on your inventory in order to help find who might be mafia
        # Depending on the players role generate the rest of the players
        ui(f"* The people in the room are: {menu.civilian_1.name}, {menu.civilian_2.name}, {menu.civilian_3.name}, "
           f"{menu.civilian_4.name}, {menu.mafioso_1.name}, {menu.detective.name}, {menu.mafioso_2.name}* \n ", default,
           "-----", "-----", "Afternoon", '\n'.join(inventory))

        # Start a loop for the interrogation phase.
        # Let the player talk with the others without any limit on time
        # Rerun this piece of code until the end of the game
        loop = True
        while loop:
            counter_win = curses.newwin(4, 84, 25, 30)

            counter_win.addstr(f" Talk with: [a] {menu.civilian_1.name} [b] {menu.civilian_2.name}, "
                               f"[c] {menu.civilian_3.name}, [d] {menu.civilian_4.name}, [e] {menu.mafioso_1.name}, "
                               f"[f] {menu.mafioso_2.name}, [g] {menu.detective.name}, [h] Start the voting possess\n"
                               f" Type [a-h]: ", curses.A_BOLD)
            counter_win.refresh()
            active_players = ["a", "b", "c", "d", "e", "f", "g"]
            c = counter_win.getkey()

            # Search for the picked character within the active players list
            # Based on the input [a-g] specify witch character from counter_win is chosen
            # Note: Fix this so you don't need two have two active lists in the future
            if c in active_players and c == "a":
                person = menu.civilian_1
                interrogations(person)
            elif c in active_players and c == "b":
                person = menu.civilian_2
                interrogations(person)
            elif c in active_players and c == "c":
                person = menu.civilian_3
                interrogations(person)
            elif c in active_players and c == "d":
                person = menu.civilian_4
                interrogations(person)
            elif c in active_players and c == "e":
                person = menu.mafioso_1
                interrogations(person)
            elif c in active_players and c == "f":
                person = menu.mafioso_2
                interrogations(person)
            elif c in active_players and c == "g":
                person = menu.detective
                interrogations(person)
            elif c == "h":
                looper = True
                while looper:
                    counter_win = curses.newwin(4, 84, 25, 30)
                    curses.echo()
                    counter_win.addstr(f" After this point you wont be able to speak with the other characters again!\n"
                                       f" Are you sure you are done? [Y/N]: ", curses.A_BOLD)
                    counter_win.refresh()
                    c = counter_win.getstr().decode().lower()
                    if c == "y" or c == "yes":
                        ui(f"* Time to vote someone out then! *", default, "-----", "-----", night,
                           '\n'.join(inventory))
                        looper = False
                        loop = False
                    elif c == "n" or c == "no":
                        ui(f"* OK! Sending you back now *", default, "-----", "-----", night, '\n'.join(inventory))
                        looper = False
                    else:
                        ui(f"* Invalid choice! Please type [Y/N] or [YES/NO]*", default, "-----", "-----", night,
                           '\n'.join(inventory))
            else:
                ui(f"* Player doesn't exist. Please try again *", default, "-----", "-----", night,
                   '\n'.join(inventory))

        # Create a list with all the active players in the game.
        # This list is used only if the player is a doctor
        doc_active_players = [f"{menu.civilian_1.name}", f"{menu.civilian_2.name}", f"{menu.civilian_3.name}",
                              f"{menu.civilian_4.name}", f"{menu.mafioso_1.name}", f"{menu.mafioso_2.name}",
                              f"{menu.detective.name}"]

        doc_active_roles = [f"{menu.civilian_1.category}", f"{menu.civilian_2.category}", f"{menu.civilian_3.category}",
                            f"{menu.civilian_4.category}", f"{menu.mafioso_1.real_role}", f"{menu.mafioso_2.real_role}",
                            f"{menu.detective.role}", f"{menu.main_player.role}"]

        ui(f" It is finally time for the voting process. It is important to choose carefully in order to avoid any "
           f"unexpected result", default, "-----", "-----", night, '\n'.join(inventory))
        vote_as_a_doctor(doc_active_players, doc_active_roles)
        check(doc_active_roles)

        ui(f" ~ OK that wasn't easy to be honest....", player, " ", " ", night, '\n'.join(inventory))
        ui(f"* From a distance you see an officer approaching *", default, " ", " ", night, '\n'.join(inventory))
        ui(f"~ It is late everyone. We should better continue tomorrow. We will wait for you here at the same place in"
           f" the morning ", officer_one, " ", " ", night, '\n'.join(inventory))
        ui(f"* Now it is time to go *", mafia_the_t_g, " ", " ", night, '\n'.join(inventory))
        ui(f"* This is an important part of the game. Choose carefully were you will go next*", mafia_the_t_g, " ",
           " ", night, '\n'.join(inventory))

        # Let the players go and hide/wait somewhere else until its time for the very last part of the game
        loop = True
        while loop:
            hide_win = curses.newwin(4, 84, 25, 30)

            hide_win.addstr(f" Go to : [a] Home, [b] Hotel, [c] The convenience store", curses.A_BOLD)
            hide_win.refresh()
            c = hide_win.getkey()

            if c == "a":
                ui(f"~ The night is cold and you can't hear anything as you walk downtown *", player, "-----",
                   "-----", night, '\n'.join(inventory))
                ui(f"* Suddenly you see a hooded person coming towards you *", hooded_person, "-----",
                   "-----", night, '\n'.join(inventory))
                looper = True
                while looper:
                    run_win = curses.newwin(4, 84, 25, 30)

                    run_win.addstr(f" You should: [a] Run, [b] Keep walking, [c] Do nothing", curses.A_BOLD)
                    run_win.refresh()
                    c = run_win.getkey()

                    if c == "a":
                        ui(f"* Without even thinking about it you start running faster than Forrest Gump himself *",
                           run, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* The hooded person doesn't bother to run towards you for some reason but that is a "
                           f"good thing *", default, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* You enter you house and lock the doors and windows *\n* Maybe it was nothing...Or "
                           f"that person was a mafioso *", hall, "-----", "-----", night, '\n'.join(inventory))
                        looper = False
                        loop = False
                    elif c == "b":
                        ui(f"* You decide to keep walking down the street although the hooded person seems very sus *",
                           hooded_person, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* The hooded person seems to be walking directly towards you. Something is certainly not "
                           f"right. You have to act carefully *", default, "-----", "-----", night,
                           '\n'.join(inventory))
                        loop_ah = True
                        while loop_ah:
                            run_win = curses.newwin(4, 84, 25, 30)

                            run_win.addstr(f" You should: [a] Run, [b] Keep walking, [c] Do nothing", curses.A_BOLD)
                            run_win.refresh()
                            c = run_win.getkey()

                            if c == "a":
                                ui(f"* Without even thinking about it you start running faster than Forrest Gump "
                                   f"himself *", run, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* The hooded person doesn't bother to run towards you for some reason but that is"
                                   f" a good thing *", default, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* You enter you house and lock the doors and windows *\n~ Maybe it was nothing..."
                                   f"Or that person was a mafioso who wanted to kill me*", hall, "-----", "-----",
                                   night, '\n'.join(inventory))
                                looper = False
                                loop_ah = False
                                loop = False
                            elif c == "b":
                                ui(f"* You see a suspicious hooded person and for some reason you think that the best "
                                   f"thing to do is to simply keep walking towards him him *", hooded_person, "-----",
                                   "-----", night, '\n'.join(inventory))
                                ui(f"* The hooded person comes nearer and nearer and eventually pulls a gun out *",
                                   default, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"~You got in the middle of mafias business..I hope you understand its nothing "
                                   f"personal", menu.mafioso_2.picture, menu.mafioso_2.name, "15", night,
                                   '\n'.join(inventory))
                                ui(f"* BAM *\n", gun, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* Unfortunately you lost {menu.main_player.name} *\n  Thanks for playing Mafia: "
                                   f"The terminal game! Feel free to start over and take a different path", game_over,
                                   "-----", "-----", night, '\n'.join(inventory))
                                quit()
                            elif c == "c":
                                ui(f"* You see a suspicious hooded person and for some reason you decide to not even "
                                   f"try to avoid him *", default, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* The hooded person comes nearer and nearer and eventually pulls a gun out *",
                                   default, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"~You got in the middle of mafias business..I hope you understand its nothing "
                                   f"personal", menu.mafioso_2.picture, menu.mafioso_2.name, "15", night,
                                   '\n'.join(inventory))
                                ui(f"* BAM *\n", gun, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* Unfortunately you lost {menu.main_player.name} *\n  Thanks for playing Mafia: "
                                   f"The terminal game! Feel free to start over and take a different path", game_over,
                                   "-----", "-----", night, '\n'.join(inventory))
                                quit()
                            else:
                                ui(f"* Invalid input! Please try again! *", default, "-----", "-----", night,
                                   '\n'.join(inventory))
                    elif c == "c":
                        ui(f"* You see a suspicious hooded person and for some reason you decide to not even try to "
                           f"avoid him *", default, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* The hooded person comes nearer and nearer and eventually pulls a gun out *", default,
                           "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* You got in the middle of mafias business....I hope you understand its nothing personal"
                           f" *", menu.mafioso_2.picture, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* BAM *\n", game_over, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* Unfortunately you lost {menu.main_player.name} *\n  Thanks for playing Mafia: The "
                           f"terminal game! Feel free to start over and take a different path", game_over, "-----",
                           "-----", night, '\n'.join(inventory))
                        quit()

                    else:
                        ui(f"* Invalid input! Please try again! *", default, "-----", "-----", night,
                           '\n'.join(inventory))
            elif c == "b":
                ui(f"* Today someone tried to kill you and your house is quite far away *\n~ The best thing is to go to"
                   f" the nearest hotel and stay there for the night. Last thing that I want is a surprise attack in my"
                   f" own house", player, "-----", "-----", night, '\n'.join(inventory))
                ui(f"~ Springfield is beautiful even at night when you can't really see anything", town_two, "-----",
                   "-----", night, '\n'.join(inventory))
                ui(f"* Suddenly though you see a hooded person coming towards you *", hooded_person, "-----",
                   "-----", night, '\n'.join(inventory))
                looper = True
                while looper:
                    run_win = curses.newwin(4, 84, 25, 30)

                    run_win.addstr(f" You should: [a] Run, [b] Keep walking, [c] Do nothing", curses.A_BOLD)
                    run_win.refresh()
                    c = run_win.getkey()

                    if c == "a":
                        ui(f"* Without even thinking about it you start running faster than Forrest Gump himself *",
                           run, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* The hooded person doesn't bother to run towards you for some reason but that is a "
                           f"good thing *", default, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* You enter you house and lock the doors and windows *\n* Maybe it was nothing...Or "
                           f"that person was a mafioso *", hall, "-----", "-----", night, '\n'.join(inventory))
                        looper = False
                        loop = False
                    elif c == "b":
                        ui(f"* You decide to keep walking down the street although the hooded person seems very sus *",
                           hooded_person, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* The hooded person seems to be walking directly towards you. Something is certainly not "
                           f"right. You have to act carefully *", default, "-----", "-----", night,
                           '\n'.join(inventory))
                        loop_ah = True
                        while loop_ah:
                            run_win = curses.newwin(4, 84, 25, 30)

                            run_win.addstr(f" You should: [a] Run, [b] Keep walking, [c] Do nothing", curses.A_BOLD)
                            run_win.refresh()
                            c = run_win.getkey()

                            if c == "a":
                                ui(f"* Without even thinking about it you start running faster than Forrest Gump "
                                   f"himself *", run, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* The hooded person doesn't bother to run towards you for some reason but that is "
                                   f"a good thing *", default, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* You enter you house and lock the doors and windows *\n* Maybe it was nothing..."
                                   f"Or that person was a mafioso *", hall, "-----", "-----", night,
                                   '\n'.join(inventory))
                                looper = False
                                loop_ah = False
                                loop = False
                            elif c == "b":
                                ui(f"* You see a suspicious hooded person and for some reason you think that the best "
                                   f"thing to do is to simply keep walking towards him him *", hooded_person, "-----",
                                   "-----", night, '\n'.join(inventory))
                                ui(f"* The hooded person comes nearer and nearer and eventually pulls a gun out *",
                                   default, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"~You got in the middle of mafias business..I hope you understand its nothing "
                                   f"personal", menu.mafioso_2.picture, menu.mafioso_2.name, "15", night,
                                   '\n'.join(inventory))
                                ui(f"* BAM *\n", gun, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* Unfortunately you lost {menu.main_player.name} *\n  Thanks for playing Mafia: "
                                   f"The terminal game! Feel free to start over and take a different path", game_over,
                                   "-----", "-----", night, '\n'.join(inventory))
                                quit()
                            elif c == "c":
                                ui(f"* You see a suspicious hooded person and for some reason you decide to not even "
                                   f"try to avoid him *", default, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* The hooded person comes nearer and nearer and eventually pulls a gun out *",
                                   default, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"~You got in the middle of mafias business..I hope you understand its nothing "
                                   f"personal", menu.mafioso_2.picture, menu.mafioso_2.name, "15", night,
                                   '\n'.join(inventory))
                                ui(f"* BAM *\n", gun, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* Unfortunately you lost {menu.main_player.name} *\n  Thanks for playing Mafia: "
                                   f"The terminal game! Feel free to start over and take a different path", game_over,
                                   "-----", "-----", night, '\n'.join(inventory))
                                quit()
                            else:
                                ui(f"* Invalid input! Please try again! *", default, "-----", "-----", night,
                                   '\n'.join(inventory))
                    elif c == "c":
                        ui(f"* You see a suspicious hooded person and for some reason you decide to not even try to"
                           f" avoid him *", default, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* The hooded person comes nearer and nearer and eventually pulls a gun out *", default,
                           "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* You got in the middle of mafias business....I hope you understand its nothing personal "
                           f"*", menu.mafioso_2.picture, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* BAM *\n", game_over, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* Unfortunately you lost {menu.main_player.name} *\n  Thanks for playing Mafia: The "
                           f"terminal game! Feel free to start over and take a different path", game_over, "-----",
                           "-----", night, '\n'.join(inventory))
                        quit()

                    else:
                        ui(f"* Invalid input! Please try again! *", default, "-----", "-----", night,
                           '\n'.join(inventory))
            elif c == "c":
                if veronica_meet:
                    ui(f"* Its been a long day so you decide to go home *\n * In your way there you decide to stop by"
                       f" the convenience store *", store, "-----", "-----", night, '\n'.join(inventory))
                    ui(f"* You enter and inside you meet Veronica, the old woman that you helped before *", default,
                       "Veronica", "87", night, '\n'.join(inventory))
                    ui(f"* Welcome back {menu.main_player.name}! How can I help you? *", old_woman, "Veronica", "87",
                       night, '\n'.join(inventory))
                    looper = True
                    while looper:
                        o_win = curses.newwin(4, 84, 25, 30)

                        o_win.addstr(f" I want to: [a] Use the arcade , [b] Ask about mysterious paper, [c] Ask about"
                                     f" the local mafia, [d] 'Actually I have to go' \nType [a-d]", curses.A_BOLD)
                        o_win.refresh()
                        c = o_win.getkey()
                        if c == "a":
                            ui(f"~ I would like to play some games on the arcade is that ok? ", player, "Veronica",
                               "87", night, '\n'.join(inventory))
                            ui(f"~ No problem at all play as much as you like! ", old_woman, "Veronica", "87", night,
                               '\n'.join(inventory))
                            ui(f"~ Lets see what games are available", s_screen, " ", " ", night,
                               '\n'.join(inventory))
                        # Start a loop for letting the player play the mini games until the letter [d] is given as input
                            loop_ah = True
                            while loop_ah:
                                arcade_win = curses.newwin(4, 84, 25, 30)

                                arcade_win.addstr(
                                    " [a] Play Snake      [b] Play Arakanoid\n [c] Play tetris       [d] 'I don't want"
                                    " to play!'\n \nType [a-d]: ")
                                arcade_win.refresh()

                                q = arcade_win.getkey()
                                if q == "a":
                                    snake()
                                    ui(f" ", s_screen, "-----", "-----", day, '\n'.join(inventory))
                                elif q == "b":
                                    spider_game()
                                    ui(f" ", s_screen, "-----", "-----", day, '\n'.join(inventory))
                                elif q == "c":
                                    tetris()
                                    ui(f" ", s_screen, "-----", "-----", day, '\n'.join(inventory))
                                elif q == "d":
                                    loop_ah = False
                                else:
                                    arcade_win.addstr("* Wrong input! Please try again! *")
                                    arcade_win.refresh()
                                    time.sleep(2)
                        elif c == "b":
                            ui(f"~ I found this mysterious piece of paper. Do you have any idea what it may be?",
                               player, "Veronica", "87", night, '\n'.join(inventory))
                            ui(f"~ Well let me see.", papper, "Veronica", "87", night, '\n'.join(inventory))
                            ui(f"~ There is obviously a hidden message on this piece of paper. You see when I was a "
                               f"child we used to take some lemon juice and use it as ink in order to write secrete "
                               f"messages!", old_woman, "Veronica", "87", night, '\n'.join(inventory))
                            ui(f"~ I don't understand....", player, "Veronica", "87", night, '\n'.join(inventory))
                            ui(f"~ When you use lemon juice to write on paper there is not much to be seen obviously "
                               f"but if you heat the paper the lemon will turn grey nad you will be able to read",
                               old_woman, "Veronica", "87", night, '\n'.join(inventory))
                            ui(f"~ Oh I see. Then we need something to heat the paper!", player, "Veronica", "87",
                               night, '\n'.join(inventory))
                            if lighter in inventory:
                                ui(f"Do you have a lighter a candle or anything that could help us?", old_woman,
                                   "Veronica", "87", night, '\n'.join(inventory))
                                ui(f"~ I have a lighter\n* You give the lighter to Veronica *", player, "Veronica",
                                   "87", night, '\n'.join(inventory))
                                inventory.remove(lighter)
                                ui(f"* You wait a bit while Veronica heats the paper *", default, "Veronica",
                                   "87", night, '\n'.join(inventory))
                                ui(f"~ {menu.main_player.name}, you have to come and read this", old_woman, "Veronica",
                                   "87", night, '\n'.join(inventory))
                                reveal(f"*  Read the letter *", papper, "Veronica", "87", night)
                                ui(f"~That's it. We found  a mafia member! I have to go to the police ", player,
                                   "Veronica", "87", night, '\n'.join(inventory))
                                ui(f"~ Run {menu.main_player.name} and be careful", old_woman, "Veronica",
                                   "87", night, '\n'.join(inventory))
                                ui(f"* You stand up and run towards the police to tell them what happened *", default,
                                   "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* Before we continue here is a short message from our sponsor *", default, "-----",
                                   "-----", night, '\n'.join(inventory))
                                ui(f"* Use the promo code: Mafia2022 and claim 10 000 gold and a VIP status for"
                                   f" 30 days *", raid, "-----", "-----", night, '\n'.join(inventory))
                                looper = False
                                loop = False
                            else:
                                ui(f"Do you have a lighter a candle or anything that could help us?", old_woman,
                                   "Veronica", "87", night, '\n'.join(inventory))
                                ui(f"* You check inside you pockets but nothing *\n~ No i don't have anything...",
                                   player, "Veronica", "87", night, '\n'.join(inventory))
                                ui(f"~ Don't worry I have a small lighter around here that could help us!", old_woman,
                                   "Veronica", "87", night, '\n'.join(inventory))
                                ui(f"* You wait a bit while Veronica grabs a lighter and heats the paper *", default,
                                   "Veronica", "87", night, '\n'.join(inventory))
                                ui(f"~ {menu.main_player.name}, you have to come and read this", old_woman, "Veronica",
                                   "87", night, '\n'.join(inventory))
                                reveal(f"*  Read the letter *", papper, "Veronica", "87", night)
                                ui(f"~That's it. We found  a mafia member! I have to go to the police ", player,
                                   "Veronica", "87", night, '\n'.join(inventory))
                                ui(f"~ Run {menu.main_player.name} and be careful", old_woman, "Veronica",
                                   "87", night, '\n'.join(inventory))
                                ui(f"* You stand up and run towards the police to tell them what happened *", default,
                                   "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* Before we continue here is a short message from our sponsor *", default, "-----",
                                   "-----", night, '\n'.join(inventory))
                                ui(f"* Use the promo code: Mafia2022 and claim 69.420 gold and a VIP status for 69"
                                   f" days *", raid, "-----", "-----", night, '\n'.join(inventory))
                                looper = False
                                loop = False
                        elif c == "c":
                            ui(f"~ It's probably a weird question but do you know anything about the towns mafia?",
                               player, "Veronica", "87", night, '\n'.join(inventory))
                            ui(f"~ I don't know much to be honest {menu.main_player.name}. They are very secretive and "
                               f"usually stay away from us, the ordinary civilians.", old_woman, "Veronica",
                               "87", night, '\n'.join(inventory))
                            ui(f"~ Do you know who may be involved behind them? Like is any of the locals around here"
                               f" helping them?", player, "Veronica", "87", night, '\n'.join(inventory))
                            ui(f"~ I don't really know. As I said they are very secretive and keep a low profile. There"
                               f" are rumors though that {menu.mafioso_2.name} the {menu.mafioso_2.role} is working "
                               f"with them", old_woman, "Veronica", "87", night, '\n'.join(inventory))
                            ui(f"~ That's very interesting. Thank you Veronica!", player,
                               "Veronica", "87", night, '\n'.join(inventory))
                            ui(f"~ Don't even mention it {menu.main_player.name}", old_woman, "Veronica", "90", night,
                               '\n'.join(inventory))
                            ui(f"~ I should better be going now it's late", player, "Veronica", "87", night,
                               '\n'.join(inventory))
                            ui(f"~ Goodbye, take care!", old_woman, "Veronica", "90", night, '\n'.join(inventory))
                            looper = False
                            loop = False
                        elif c == "d":
                            ui(f"* I actually came here just to say hi! I have to go now! *", player, "Veronica", "87",
                               night, '\n'.join(inventory))
                            ui(f"~ Oh thank you {menu.main_player.name}! You better go home and get some rest now. See"
                               f" you next time*", old_woman, "Veronica", "87", night, '\n'.join(inventory))
                            looper = False
                            loop = False
                        else:
                            ui(f"* Invalid input! Please try again! *", default, "-----", "-----", night,
                               '\n'.join(inventory))
                else:
                    ui(f"* Its been a long day so you decide to go home *\n * In your way there you decide to stop by "
                       f"the convenience store *", store, "-----", "-----", night, '\n'.join(inventory))
                    ui(f"* You enter and inside you meet an old woman. *", default, "-----", "-----", night,
                       '\n'.join(inventory))
                    ui(f"~ Excuse sir but we are closed ", old_woman, "-----", "-----", night,
                       '\n'.join(inventory))
                    ui(f"~ Oh I am sorry I thought the store was open. Could I please buy some rice and milk? ", player,
                       "-----", "-----", night, '\n'.join(inventory))
                    ui(f"~ Well I would be willing to help you but once I needed help you ignored me *", old_woman,
                       "-----", "-----", night, '\n'.join(inventory))
                    ui(f"* Well well well..... I should have helped the old woman back then *\n~ Once again I am very "
                       f"sorry", player, "-----", "-----", night, '\n'.join(inventory))
                    ui(f"* As you turn towards the door the old woman stops you *", default, "-----", "-----", night,
                       '\n'.join(inventory))
                    ui(f"~ You were very rude for not helping me but here take these\n* The old woman hands you some "
                       f"rice and a packet of milk *", old_woman, "-----", "-----", night, '\n'.join(inventory))
                    ui(f"~ Thank you very much, you are very kind!\n* You take your things and head home *", player,
                       "-----", "-----", night, '\n'.join(inventory))
                    loop = False
            else:
                ui(f"* Invalid input! Please try again! *", default, "-----", "-----", night, '\n'.join(inventory))
        # If the player has not the secrete diary then proceed in the game and voting process
        if secret_diary is False:
            ui(f"* The next morning you return to the same place as before and get yourself ready for the voting"
               f" process*", default, "-----", "-----", day, '\n'.join(inventory))
            ui(f"~ OK everyone take a place it's time for you to vote who is the mafioso but first a word from our "
               f"sponsor...", officer_one, "-----", "-----", day, '\n'.join(inventory))
            ui(f"* Raid Shadow Legends. The entire police department is sponsored from Raid Shadow legends so please "
               f"download the game and use the promo code Police2022*", raid, " ", " ", day, '\n'.join(inventory))
            ui(f"~ Now Let the voting begin!.", officer_one, "-----", "-----", day, '\n'.join(inventory))
            vote_as_a_doctor(doc_active_players, doc_active_roles)
            check(doc_active_roles)
            ui(f"~ Now that you picked one out we will interrogate that individual and tell you what we found",
               officer_one, "-----", "-----", day, '\n'.join(inventory))
            ui(f"* Its been an hour since the last suspect was send in prison and the police/game-master made no "
               f"statements regarding the state of the case *", mafia_the_t_g, " ", " ", day, '\n'.join(inventory))
            ui(f"* While you wait you can feel the tension on the room rising *", default, "-----", "-----", day,
               '\n'.join(inventory))
            ui(f"~ Ok everyone time to gather up once more and tell us who do you think is the assassin among us",
               police, "Officer Greg", "90", day, '\n'.join(inventory))
            ui(f"~ We think the mafia is still among you people so lets get over with it",
               officer_one, "Officer Mark", "87", day, '\n'.join(inventory))
            vote_as_a_doctor(doc_active_players, doc_active_roles)
            check(doc_active_roles)
            ui(f"* For once more you voted one out but still the police has not identified the assassin *",
               default, "Officer Greg", "90", day, '\n'.join(inventory))
            ui(f"~ Come everyone we have to do this one more time, the mafia members are still here we know it", police,
               "Officer Greg", "90", day, '\n'.join(inventory))
            ui(f"~ How many more times are we going to do this officer Greg? ", player, "Officer Greg",
               "90", day, '\n'.join(inventory))
            ui(f"~ Look {menu.main_player.name} I am not the one making the rules here. Lets just get over with this",
               police, "Officer Greg", "90", day, '\n'.join(inventory))
            ui(f"* Although most of the people in the room look frustrated, they gather in order to vote one out *",
               default, " ", " ", day, '\n'.join(inventory))
            vote_as_a_doctor(doc_active_players, doc_active_roles)
            check(doc_active_roles)
            ui(f"* Apparently the mafia is hiding very VERY well. *\n* You have to try a bit harder to find who is the"
               f" impostor *", later, " ", " ", day, '\n'.join(inventory))
            ui(f"* At least this time there are not many left so it will be soon over*", mafia_the_t_g, " ", " ",
               day, '\n'.join(inventory))
            vote_as_a_doctor(doc_active_players, doc_active_roles)
            check(doc_active_roles)
            ui(f"~ At this point there are not many options so it will be easy to find the one who is sus",
               later, "Officer Greg", "90", day, '\n'.join(inventory))
            ui(f"* You are at the end of the game. At this point you either win epically or loose and try all over "
               f"again*", later, "Officer Greg", "90", day, '\n'.join(inventory))
            vote_as_a_doctor(doc_active_players, doc_active_roles)
            check(doc_active_roles)
        # If the user found the secrete diary then finish the game
        else:
            ui(f"* You Showed the diary to the police and they with it's contents they found out everything about the "
               f"mafia*", mafia_the_t_g, "  ", " ", day, '\n'.join(inventory))
            ui(f"* Finally the mafia got exposed. The last mafioso was {menu.mafioso_1.name} *\n* {menu.mafioso_1.name}"
               f" even admitted that {menu.mafioso_2.name} was involved in Ben's assassination *", day, "-----",
               "-----", day, '\n'.join(inventory))
            ui(f"* A month later since the police arrested the mafia members and Springfield looks better than ever *",
               transition_three, "-----", "-----", day, '\n'.join(inventory))
            ui(f"* The crime rates dropped by 50% and people feel safe thanks to you ! *", springfield, "-----",
               "-----", day, '\n'.join(inventory))
            ui(f"* Congratulations {menu.main_player.name}! You won the game! *", game_over, "-----", "-----", day,
               '\n'.join(inventory))
# If the player chose to be a Detective then start path 3
    else:
        # Call the dialogue function. Pass (text),(picture),(name of the character or place that will be shown)
        ui(f"Congratulations {menu.main_player.name}. The game is ready to start", mafia_the_t_g, "-----", "-----",
           "Afternoon", '\n'.join(inventory))
        ui(f"You are at your home, relaxing after a long day at work", default, "-----", "-----", "Afternoon",
           '\n'.join(inventory))
        ui(f"Suddenly you hear a knock from the front door", hall, "-----", "-----", "Afternoon", '\n'.join(inventory))
        ui(f"* As you walk towards the door you notice an envelope on the floor and it seems like it's a letter *"
           f" from uncle Ben.", entrance, "-----", "-----", "Afternoon", '\n'.join(inventory))
        ui(f"It has been a while since you had news from uncle Ben and therefore you sit down, open the letter and "
           f"read it with curiosity.", envelope, "-----", "-----", "Afternoon", '\n'.join(inventory))
        opening(f"*You read the letter*", invitation, "-----", "-----", '\n'.join(inventory))
        opening(f"Although I have a lot of work next week I should be able to free some time for uncles' birthday",
                invitation, "-----", "-----", '\n'.join(inventory))
        ui(f" ", transition, "-----", "-----", "-----", '\n'.join(inventory))
        ui(f"*You are in front of uncle Ben's house and notice that all lights are lit.*", house, "-----", "-----",
           night, '\n'.join(inventory))
        ui(f"~I hope I am not too late.", fence, "-----", "-----", night, '\n'.join(inventory))
        ui(f"*While you get closer to the entrance you can hear music and people talking*", house_out, "-----", "-----",
           night, '\n'.join(inventory))
        ui(f"~Well it seems uncle called quite a few people for his birthday. I should better go and greet him.",
           house_hall, "-----", "-----", night, '\n'.join(inventory))
        ui(f"*You spend some time searching but you can't find uncle Ben. He is probably upstairs att his office.*",
           default, "-----", "-----", night, '\n'.join(inventory))
        ui(f"*It is way more quiet upstairs, you think*", base_room, "-----", "-----", night, '\n'.join(inventory))
        ui(f"*Once you arrive just outside of the office, you can hear people talking the other side. Although impolite"
           f", you decide to eavesdrop before entering.*", base, "-----", "-----", night, '\n'.join(inventory))
        ui(f"[Voice 1]~ We know everything about your plans.\n I hope you understand though it's nothing personal to "
           f"me.I am just following orders here", default, "-----", "-----", night, '\n'.join(inventory))
        ui(f"[Voice 2]~ You must be mistaken. I am not the one that you are looking for. I am a simple businessman!",
           default, "-----", "-----", night, '\n'.join(inventory))
        ui(f"[Voice 1]~ I am sorry old man, but my orders are clear. You made angry some very powerful people and now "
           f"its time to pay.", default, "-----", "-----", night, '\n'.join(inventory))
        ui(f"*BAM*\nYou hear the sound of a gun and you immediately rush in the room!", base, "-----", "-----",
           night, '\n'.join(inventory))

        ui(f"~UNCLE BEN!\n*Someone shot uncle ben*"
           f"\n* You see a masked person taking the door on your left in order to escape *", room_1, "-----", "-----",
           night, '\n'.join(inventory))

        # Create the window and set (text rows, character limit, y,x coordinates for the window)
        loop = True
        while loop:
            counter_win = curses.newwin(4, 84, 25, 30)

            counter_win.addstr("I will: [a] Run after the assassin. [b] Check uncle Ben."
                               "\n \nType [a] or [b]: ")
            counter_win.refresh()

            c = counter_win.getkey()
            if c == "a":
                ui(f"* At once you try to catch the person before he manages to escape *", mafia_run,
                   "-----", "-----", night, '\n'.join(inventory))
                ui(f"* You run as fast as you can and are just a few meters behind the assassin *", mafia_run_two,
                   "-----", "-----", night, '\n'.join(inventory))
                ui(f"* Suddenly the masked person throws towards you a big chinese vase from the corridor "
                   f"and you fall down *", default, "-----", "-----", night, '\n'.join(inventory))
                ui(f"* It takes only a few seconds to get up but the masked assassin is far from gone *", corridor,
                   "-----", "-----", night, '\n'.join(inventory))
                ui(f"* At this point you decide to run back in uncle Ben's office, and hope that is not too late *",
                   b2r, "-----", "-----", night, '\n'.join(inventory))
                loop = False
            elif c == "b":
                ui(f"* You ignore the person escaping and you immediately run to help uncle Ben *", mafia_run, "-----",
                   "-----",
                   night, '\n'.join(inventory))
                loop = False
            else:
                ui(f"* Wrong input try again! Uncle Ben is dying! *", room_1, "-----", "-----", night,
                   '\n'.join(inventory))

        ui(f"* You grab him carefully and he tries to tell you something *", default, "-----", "-----",
           night, '\n'.join(inventory))
        ui(f"~ Listen {menu.main_player.name}...\nWith great power, comes great responsibility! ",
           ben_two, "Uncle Ben", "75", night, '\n'.join(inventory))
        ui(f"~ Don't let them destroy my life's work. \n Don't let them escape!",
           ben_two, "Uncle Ben", "75", night, '\n'.join(inventory))
        ui(f"~ 'The key is in the stars'.....", ben_two, "Uncle Ben", "75",
           night, '\n'.join(inventory))
        ui(f"* Uncle Ben falls unconscious and you can hear footsteps from the corridor *", uncle, "Uncle Ben", "75",
           night, '\n'.join(inventory))

        ui(f"* You turn your back and you see a police officer standing on the door *", default, "Officer Greg",
           "80", night, '\n'.join(inventory))
        ui(f"Officer: You there!", police, "Officer Greg", "85", night, '\n'.join(inventory))

        loop = True
        while loop:
            counter_win = curses.newwin(4, 84, 25, 30)

            counter_win.addstr(" [a] Tell the officer about the assassin\n [b] 'I am innocent' \n [c] Say nothing "
                               "\n Type [a], [b] or [c]: ", curses.A_BOLD)
            counter_win.refresh()

            c = counter_win.getkey().lower()
            if c == "a":
                ui(f"~ I was looking for my uncle and I heard a gunshot from inside the office."
                   f"\n  I entered in the room and I saw a masked person with a gun", player, "Officer Greg", "82",
                   night, '\n'.join(inventory))
                ui(f"~ I was not able to catch the assassin nor help my uncle.", police, "Officer Greg", "82", night,
                   '\n'.join(inventory))
                loop = False
            elif c == "b":
                ui(f"* At the sight of the officer you panic and immediately prepare to tell the truth *", default,
                   "Officer Greg", "82", night, '\n'.join(inventory))
                ui(f"~ I am innocent * You shout panicked * \n~ An assassin killed my uncle, you must find him!",
                   player, "officer Greg", "83", night, '\n'.join(inventory))
                ui(f"* The officer looks att you and seems a bit confused with your reaction *\n Officer: Relax you are"
                   f" not under arrest", police, "officer Greg", "83", night, '\n'.join(inventory))
                loop = False
            elif c == "c":
                ui(f"* For a moment there you freeze and try to process what is going on *", default, "Officer Greg",
                   "82", night, '\n'.join(inventory))
                ui(f"* You decide to not say a word *\n* The officer looks at you and says *", police, "Officer Greg",
                   "85", night, '\n'.join(inventory))
                loop = False
            else:
                ui(f"* That was not a valid choice! Try again!  *", default, "-----", "-----", night,
                   '\n'.join(inventory))

        ui(f"Officer: We received an anonymous phone call about a murder from this house about half an hour ago."
           f"\nWas that you? ", police, "Officer Greg", "85", night, '\n'.join(inventory))
        ui(f"~ Half an hour ago? That's not possible. The murder happened just a few minutes ago!"
           f"\nThere is no way the phone call was made half an hour ago unless.... ", player, "Officer Greg", "85",
           night, '\n'.join(inventory))
        ui(f"Officer: Unless there is an 'impostor amongst us'. "
           f"\n I am afraid that someone within the house is involved in this case.\n We'll need access to the guest "
           f"list to start interrogating everyone", police, "Officer Greg", "89", night, '\n'.join(inventory))
        ui(f"* The police has surrounded the house and conducts one on one interrogations with everyone *"
           f"\n* While you wait for your turn you can talk with the other guests *", transition_two, "-----", "-----",
           night, '\n'.join(inventory))

        ui(f"* The police surrounded the house and conducts one on one interrogations *"
           f"\n* While you wait for your turn you can talk with the other guests *", transition_two, "-----", "-----",
           night, '\n'.join(inventory))

        loop = True
        while loop:
            counter_win = curses.newwin(4, 84, 25, 30)

            counter_win.addstr(f" [a] Talk with a person nearby [b] Wait for your turn"
                               "\n Type [a] or [b]: ", curses.A_BOLD)
            counter_win.refresh()

            c = counter_win.getkey()
            if c == "a":
                ui(f"~ Hello there, my name is {menu.main_player.name}.", player, "-----", "-----", night,
                   '\n'.join(inventory))
                ui(f"~ Hy my name is {menu.civilian_1.name}. How can I help you?", menu.civilian_1.picture,
                   f"{menu.civilian_1.name}", f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                looper = True
                while looper:
                    counter_win = curses.newwin(4, 85, 25, 30)

                    counter_win.addstr(f" [a] Ask about the assassin [b] Ask about uncle Ben [c] Ask about "
                                       f"{menu.civilian_1.name}s' " f"occupation\n [d] 'I have to go...'\n "
                                       f"\nType [a-d : ", curses.A_BOLD)
                    counter_win.refresh()

                    q = counter_win.getkey()
                    if q == "a":
                        ui(f"~ So did you see or hear anything weird tonight?", player, f"{menu.civilian_1.name}",
                           f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        ui(f"~ You mean anything related to the assassin?\n Well...I heard that Ben was involved with "
                           f"mafia business and they wanted him dead.", menu.civilian_1.picture,
                           f"{menu.civilian_1.name}", f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        ui(f"~ What makes you say that? Who told you about this story?", player,
                           f"{menu.civilian_1.name}", f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        ui(f"~ Look I would say its more like a rumor rather than the truth.\nIn any case "
                           f"{menu.civilian_2.name} told me about these rumors.", menu.civilian_1.picture,
                           f"{menu.civilian_1.name}", f"{menu.civilian_1.reliability}",
                           night, '\n'.join(inventory))
                        ui(f"~ If you want more details go and ask {menu.civilian_2.name} yourself!\nit's that person "
                           f"there with the {menu.civilian_2.hair} hair and the {menu.civilian_2.eyes} eyes.",
                           menu.civilian_1.picture, f"{menu.civilian_1.name}", f"{menu.civilian_1.reliability}",
                           night, '\n'.join(inventory))
                        ui(f"~ Thanks for your time!", player, f"{menu.civilian_1.name}",
                           f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                    elif q == "b":
                        ui(f"~ Hey did you know Ben?", player, f"{menu.civilian_1.name}",
                           f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        ui(f"~ I first met Ben a few years ago. Back then I was working on a non-profit organisation "
                           f"and we were in need of some money. Ben learned about our cause and immediately donated a"
                           f" large amount of money", menu.civilian_1.picture, f"{menu.civilian_1.name}",
                           f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        ui(f"~ If I may ask, what was the cause of your organisation?", player,
                           f"{menu.civilian_1.name}", f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        ui(f"~ We were mostly developing new technologies for agricultural use. We tried to find new "
                           f"techniques for growing plants, increase production and minimize the cost of farming in "
                           f"general.", menu.civilian_1.picture, f"{menu.civilian_1.name}",
                           f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        ui(f"~ I never thought that Ben was interested in science ", player, f"{menu.civilian_1.name}",
                           f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        ui(f"~ If you want to know more about this you should go and speak with {menu.civilian_2.name}"
                           f"\nit's that person there with the {menu.civilian_2.hair} hair and the "
                           f"{menu.civilian_2.eyes} eyes.", menu.civilian_1.picture, f"{menu.civilian_1.name}",
                           f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        ui(f"~ Thanks for the information", player, f"{menu.civilian_1.name}",
                           f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                    elif q == "c":
                        ui(f"~ So what do you do for work? Are you also a psychiatrist like Ben?", player,
                           f"{menu.civilian_1.name}", f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        ui(f"~ I used to work as a secretary in a non-profit organisation but for the last 3 years I "
                           f"work as a {menu.civilian_1.role}", menu.civilian_1.picture, f"{menu.civilian_1.name}",
                           f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        ui(f"~ That sounds interesting!", player, f"{menu.civilian_1.name}",
                           f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                    elif q == "d":
                        ui(f"~I have to go now", player, f"{menu.civilian_1.name}", f"{menu.civilian_1.reliability}",
                           night, '\n'.join(inventory))
                        ui(f"~ Ok goodbye", menu.civilian_1.picture, f"{menu.civilian_1.name}",
                           f"{menu.civilian_1.reliability}", night, '\n'.join(inventory))
                        looper = False
                    else:
                        ui(f"* That was not a valid choice! Try again! *", default, "-----", "-----",
                           night, '\n'.join(inventory))

                ui(f"* Once you are done speaking with {menu.civilian_1.name} you decide to go and talk with "
                   f"{menu.civilian_2.name} *", default, "-----", "-----", night, '\n'.join(inventory))
                ui(f"~ Hi! My name's {menu.main_player.name} I was talking with {menu.civilian_1.name} about Ben and "
                   f"she told me that you knew him *", player, f"{menu.civilian_2.name}",
                   f"{menu.civilian_2.reliability}", night, '\n'.join(inventory))
                ui(f" Yes I knew Benny quite well. And you must be his nephew am I right?",
                   f"{menu.civilian_2.picture}",
                   f"{menu.civilian_2.name}", f"{menu.civilian_2.reliability}", night, '\n'.join(inventory))
                ui(f"~ Yes that's right.\nI wanted to ask you about these rumors about my uncle.\nDid he really had "
                   f"troubles with the local mafia?", player, f"{menu.civilian_2.name}",
                   f"{menu.civilian_2.reliability}", night, '\n'.join(inventory))
                ui(f" Listen kid, no matter what your uncle told you stay out of this business.\nThere is much you "
                   f"don't know and that is for the best", f"{menu.civilian_2.picture}", f"{menu.civilian_2.name}",
                   f"{menu.civilian_2.reliability - 5}", night, '\n'.join(inventory))
                ui(f" I am really sorry for your uncle but it's best if you forget what happened here today.",
                   f"{menu.civilian_2.picture}", f"{menu.civilian_2.name}", f"{menu.civilian_2.reliability - 10}",
                   night, '\n'.join(inventory))
                loop = False
            elif c == "b":
                loop = False
            else:
                ui(f"* That was not a valid choice! Try again! *", default, "-----", "-----", night,
                   '\n'.join(inventory))

        ui(f"* Suddenly the police comes forward with important information *", default, f"{menu.civilian_2.name}",
           f"{menu.civilian_2.reliability - 10}", night, '\n'.join(inventory))
        ui(f"Officer: Ladies and gentlemen I would like to inform you that we found who was the assassin. ", police,
           "-----", "-----", night, '\n'.join(inventory))
        ui(f"The assassin is {menu.civilian_4.name} Smith. While searching her bag we found a loaded gun and ammunition"
           f" matching the one that was used against Ben Steward\nFurthermore we have evidence that make us believe "
           f"that she has ties with the mafia.", police, "-----", "-----", night, '\n'.join(inventory))
        ui(f" ~ I am innocent, this is a big mistake!\nPlease I am not the assassin\nThis was all a setup!",
           f"{menu.civilian_4.picture}", "-----", "-----", night, '\n'.join(inventory))
        ui(f"* It's late and this was a horrible night *\n* There are many things that don't actually make sense but "
           f"you should probably just move on * ", default, "-----", "-----", night, '\n'.join(inventory))
        ui(f"* You wake up in the morning and you open the TV. *", transition_three, "-----", "-----",
           day, '\n'.join(inventory))
        ui(f"* A new mafia attack on Springfield, similar to the one on uncle Ben's house *\n* On that moment you can "
           f"hear vividly uncle Ben's last words *", tv, "-----", "-----", day, '\n'.join(inventory))
        ui(f"~ Don't let them destroy my life's work. \n Don't let them escape!", ben_two,
           "Uncle Ben", "75", day, '\n'.join(inventory))
        ui(f"~ 'The key is in the stars'.....", uncle, "Uncle Ben", "75", day, '\n'.join(inventory))
        ui(f"~ I wander if there is any clue on uncle Ben's house. There must be something left there to explain what"
           f" happened", default, "-----", "-----", day, '\n'.join(inventory))
        ui(f"* On your way to uncle Ben's house you see a convenience store *\n* Just outside of the store there is an "
           f"old woman asking for help *", store, "-----", "-----", day, '\n'.join(inventory))

        loop = True
        while loop:
            counter_win = curses.newwin(4, 84, 25, 30)

            counter_win.addstr(" [a] Help her [b] Ignore the old woman "
                               "\n \nType [a] or [b]: ")
            counter_win.refresh()

            c = counter_win.getkey()
            if c == "a":
                veronica_meet = True
                ui(f"* you walk towards the convenience store and offer your help *", default,
                   "-----", "-----", day, '\n'.join(inventory))
                ui(f"~ My cat, someone please help my cat!", old_woman, "-----", "-----", day, '\n'.join(inventory))
                ui(f"~ What's going on?", player, "-----", "-----", day, '\n'.join(inventory))
                ui(f"~ My cat fluffy climbed up on the tree and now he can't come down! Please help me!  ", old_woman,
                   "-----", "-----", day, '\n'.join(inventory))
                ui(f"~ I will help you, don't worry!", player, "-----", "-----", day, '\n'.join(inventory))
                looper = True
                while looper:
                    counter_win = curses.newwin(4, 84, 25, 30)

                    counter_win.addstr(" [a] Search for anything that can help you get the cat [b] Climb on the tree"
                                       "\n \nType [a] or [b]: ")
                    counter_win.refresh()

                    f = counter_win.getkey()
                    if f == "a":
                        ui(f"* You look around the place for a while until you see an old ladder *\n* Although a bit "
                           f"unsafe you decide to use it and save the cat *", default, "-----", "-----",
                           day, '\n'.join(inventory))
                        ui(f"* Once you have fluffy in your arms, you safely get down and hand him to his owner *",
                           mafia_the_t_g, "-----", "-----", day, '\n'.join(inventory))
                        ui(f"~ MY CAT! * shouts the old woman *", mafia_the_t_g, "-----", "-----", day,
                           '\n'.join(inventory))
                        looper = False
                    elif f == "b":
                        ui(f"* Without thinking about it you decide to try and climb on the tree without any help *",
                           default, "-----", "-----", day, '\n'.join(inventory))
                        ui(f"* Once you have the cat in your arms, you attempt to get down of the tree but you slip "
                           f"and end up on the ground *", mafia_the_t_g, "-----", "-----", day, '\n'.join(inventory))
                        pl_rel -= 20
                        ui(f"~ MY CAT!\n* shouts the old woman *\n* You are not severely injured but with that fall you"
                           f" could easily break a leg or arm *", mafia_the_t_g, "-----", "-----", day,
                           '\n'.join(inventory))
                        looper = False
                    else:
                        ui(f"* That was not a valid choice! Try again! *", default, "-----", "-----",
                           day, '\n'.join(inventory))

                ui(f"~ How can I ever repay you for this favour? ", old_woman, "-----", "-----", day,
                   '\n'.join(inventory))
                ui(f"~ It was nothing really.", player, "-----", "-----", day, '\n'.join(inventory))
                ui(f"~ Please come inside the store and get some fruits as a gift from me. \nIt's not much but they are"
                   f" fresh and they taste great!", old_woman, "-----", "-----", day, '\n'.join(inventory))
                ui(f"~ Well I wouldn't say no to some fruits\n~ By the way my name is {menu.main_player.name}", player,
                   "-----", "-----", day, '\n'.join(inventory))
                ui(f"Nice to meet you {menu.main_player.name}! My name is Veronica", old_woman, "Veronica", "85",
                   day, '\n'.join(inventory))
                ui(f"* While you wait in the store you see an old arcade machine *", arcade, "-----", "-----", day,
                   '\n'.join(inventory))
                ui(f"~ Is it ok if I play a few games? ", player, "Veronica", "85", day, '\n'.join(inventory))
                ui(f"~ Yes feel free to play as much as you want.", old_woman, "Veronica", "85", day,
                   '\n'.join(inventory))
                ui(f"~ Ok then lets see what games are available! ", s_screen, "-----", "-----",
                   day, '\n'.join(inventory))
                loop_ah = True
                while loop_ah:
                    arcade_win = curses.newwin(4, 84, 25, 30)

                    arcade_win.addstr(" [a] Play Snake      [b] Play Arkanoid\n [c] Play tetris       "
                                      "[d] 'I don't want to play!'\n \nType [a-d]: ")
                    arcade_win.refresh()

                    q = arcade_win.getkey()
                    if q == "a":
                        snake()
                        ui(f" ", s_screen, "-----", "-----", day, '\n'.join(inventory))
                    elif q == "b":
                        spider_game()
                        ui(f" ", s_screen, "-----", "-----", day, '\n'.join(inventory))
                    elif q == "c":
                        tetris()
                        ui(f" ", s_screen, "-----", "-----", day, '\n'.join(inventory))
                    elif q == "d":
                        loop_ah = False
                    else:
                        arcade_win.addstr("* Wrong input! Please try again! *")
                        arcade_win.refresh()
                        time.sleep(2)

                ui(f" ", s_screen, "-----", "-----", day, '\n'.join(inventory))
                ui(f"~ Alright! Here is a bag full with fresh and tasty fruits ", old_woman, "Veronica", "90", day,
                   '\n'.join(inventory))
                inventory.append("Fruits")
                ui(f"~ Thanks a lot for this! ", player, "Veronica", "90", day, '\n'.join(inventory))
                ui(f"~ It's the least I could do since you helped me get fluffy down of the tree! You are welcome here "
                   f"any time!", old_woman, "Veronica", "90", day, '\n'.join(inventory))
                ui(f"* After this short break, it's time to focus on today's main goal! *", default, "-----", "-----",
                   day, '\n'.join(inventory))
                loop = False
            elif c == "b":
                ui(f"* You decide to ignore the old woman.*\n * After all why waste your time when you have other more "
                   f"important things to do *", default, "-----", "-----", day, '\n'.join(inventory))
                ui(f"* On your way you find a 10 dollar bill and you pick it up  *", fence, "-----", "-----",
                   "Afternoon", '\n'.join(inventory))
                inventory.append("10 dollar bill")
                loop = False
            else:
                ui(f"* Wrong input try again! *", store, "-----", "-----", day, '\n'.join(inventory))

        # Go to store to take the keys for uncles house
        # Play video games + add them on main menu
        # Go to the house get clues
        ui(f"* It takes some time but you finally arrive att uncle Ben's house *", mafia_the_t_g, "-----", "-----",
           "Afternoon", '\n'.join(inventory))
        ui(f"* A month later and it all still seems unreal. *\n~ I must find out why the mafia targeted my uncle",
           default, "-----", "-----", "Afternoon", '\n'.join(inventory))
        ui(f"* The house is emptier than ever but at least that makes the investigation easier *", mafia_the_t_g,
           " ", " ", "Afternoon", '\n'.join(inventory))

        # Set a big loop and let the player explore the house
        # Here the player will find the clues needed to progress the story or the assassin will show and kill the player
        loop = True
        while loop:
            # Create an empty list to store the necessary items to progress the game
            # In total there are 6 items that can be added to the list but only 4 can be acquired for progression.
            needed_items = []

            counter_win = curses.newwin(4, 84, 25, 30)
            # Give the player choices for the places where clues may be hidden
            counter_win.addstr("I will: [a] Search the office upstairs. [b] Search the living room.\n      "
                               " [c] Search the kitchen. [d] Search staffroom\n \nType [a-d]: ")
            counter_win.refresh()

            c = counter_win.getkey()
            # Start a branch for going upstairs and search the office
            if c == "a":
                # Get the number of items from the list
                total_needed_items = len(inventory)
                # If the inventory is full start the next act
                if total_needed_items >= 7:
                    loop = False
                else:
                    # Let the user to go upstairs and explore
                    ui(f"* While you go upstairs to uncle Ben's office, the last of his words come in mind *\n'~The key"
                       f" is in the stars'", base_room, "-----", "-----", "Afternoon", '\n'.join(inventory))
                    ui(f"* You arrive out of the office and open the door *", base, "-----", "-----", "Afternoon",
                       '\n'.join(inventory))
                    ui(f"~ Of course uncle Ben had set a second fireplaces in his house.... \n~ In any case lets start "
                       f"looking for any clues", b_office, "-----", "-----", "Afternoon", '\n'.join(inventory))
                    looper = True
                    while looper:
                        office_win = curses.newwin(4, 84, 25, 30)
                        # Give the player choices for the places where clues may be hidden
                        office_win.addstr("I will: [a] Search the bookcase. [b] Search uncles desk.\n      "
                                          " [c] Search the safe. [d] I want to go somewhere else\n \nType [a-d]: ")
                        office_win.refresh()

                        c = office_win.getkey()
                        # Search the bookcases
                        if c == "a":
                            ui(f"* There are plenty books in this bookcase *", default, "-----", "-----", "Afternoon",
                               '\n'.join(inventory))
                            # Set the morse code book as an str that can be equipped in the inventory
                            # The book is essential for decoding the painting code found in the living room
                            morse_code_book = "Morse code book"
                            # Control if the player entered the room before and if the player took the morse code book
                            # If player enters for first time/returned to pick the book then spawn it in the bookshelf
                            if morse_code_book not in inventory:
                                ui(f"* You search one by one the books and find one that's quite bizarre. It's a book "
                                   f"about morse code *\n~ I didn't know that uncle was interested in morse code. "
                                   f"That's interesting.", bookshelf, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                                loop_ah = True
                                while loop_ah:
                                    book_win = curses.newwin(4, 84, 25, 30)

                                    book_win.addstr("Take the Morse code book?: [a] Yes. [b] No.\n \nType [a-b]: ")
                                    book_win.refresh()

                                    c = book_win.getkey()
                                    if c == "a":
                                        needed_items.append("Morse code book")
                                        inventory.append("Morse code book")
                                        loop_ah = False
                                    elif c == "b":
                                        loop_ah = False
                                    else:
                                        ui(f" Invalid choice! Please try again! ", default, "-----", "-----",
                                           "Afternoon", '\n'.join(inventory))
                                ui(f"¨~~Lets see what else I can find here", b_office, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                            # If the player enters the room x times and at some point took the lighter then show
                            # an empty drawer
                            elif morse_code_book in inventory:
                                ui(f"* Just random books nothing to see here *", bookshelf, "-----", "-----",
                                   "Afternoon", '\n'.join(inventory))
                                ui(f"~ ok I think I am done with this part of the room ", player, "-----", "-----",
                                   "Afternoon",
                                   '\n'.join(inventory))
                        # Search the desk
                        elif c == "b":
                            ui(f"~ Without a doubt there must be something important here", desk, "-----", "-----",
                               "Afternoon", '\n'.join(inventory))
                            # Set the paper as an str object that can be append in the players inventory
                            # If the player got the lighter from the living room then it could be possible to reveal the
                            # hidden names written in the paper
                            paper = "Paper"
                            # Control if the player entered the room before and if the player took the secrete paper
                            # If player enters for first time/returned to pick the paper, show the paper on the shelf
                            if paper not in inventory:
                                ui(f"* You search for a while and find a mysterious piece of paper *", papper, "-----",
                                   "-----", "Afternoon", '\n'.join(inventory))
                                loop_ah = True
                                while loop_ah:
                                    paper_win = curses.newwin(4, 84, 25, 30)

                                    paper_win.addstr("Take the mystery paper?: [a] Yes. [b] No.\n \nType [a-b]: ")
                                    paper_win.refresh()

                                    c = paper_win.getkey()
                                    if c == "a":
                                        needed_items.append("Paper")
                                        inventory.append("Paper")
                                        loop_ah = False
                                    elif c == "b":
                                        loop_ah = False
                                    else:
                                        ui(f" Invalid choice! Please try again! ", default, "-----", "-----",
                                           "Afternoon", '\n'.join(inventory))
                                ui(f" ~ Let's check if there is anything else left to find! ", desk, "-----", "-----",
                                   "Afternoon", '\n'.join(inventory))
                            # If the player enters the room x times and already took the secrete paper then show
                            # an empty desk
                            elif paper in inventory:
                                ui(f"* There are only random papers and tax books on this desk. Nothing interesting to "
                                   f"see! *", desk, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                ui(f"~ ok I think I am done with this part of the room ", default, "-----", "-----",
                                   "Afternoon", '\n'.join(inventory))
                        # Let the player try and open the safe
                        elif c == "c":
                            ui(f"~ Well that's a big safe...", safe, "-----", "-----", "Afternoon",
                               '\n'.join(inventory))
                            ui(f"~ I wonder what's inside there...", security_safe, "-----",
                               "-----", "Afternoon", '\n'.join(inventory))
                            loop_ah = True
                            while loop_ah:
                                safe_win = curses.newwin(4, 84, 25, 30)

                                safe_win.addstr(
                                    "The combinations seem endless but there is only one that will open the safe."
                                    "\n[Type quit to leave the safe] The code is : ")
                                safe_win.refresh()
                                curses.echo()
                            # .decode() is used because originally the [c = safe_win.gets()] returns the input in bits
                            # Ex. Input= Hello, without decoding returns b'Hello' and thous doesnt work in the if/elif
                                c = safe_win.getstr().decode()
                            # If the user find the code by chance or from the painting then open the safe
                                if c == "1974":
                                    # Set the diary as true and let the player read about the mafia
                                    secret_diary = True
                                    ui(f"* Inside the safe you find uncle Ben's diary and a lot of cash *.\n ~ I wonder"
                                       f" if there is information here that will help me find the reason for uncles "
                                       f"assassination...", safe, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                    ui(f"* You read many pages until you find the last entry *", diary, "-----",
                                       "-----", "Afternoon", '\n'.join(inventory))
                                    ui(f" ' This is my last entry on this diary. I believe that they will soon get me.",
                                       diary, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                    ui(f"'Many, years ago I made a deal with the local mafia and I allowed them to use "
                                       f"one of my stores as a storage for hiding drugs in return for a large sum of"
                                       f" money  '", diary, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                    ui(f"' What I did was wrong and that's why I decided last month to stop this "
                                       f"contract of ours. The head of the mafia Don Emilio, was not pleased with my "
                                       f"decision and threatened me.' ", diary, "-----", "-----", "Afternoon",
                                       '\n'.join(inventory))
                                    ui(f"' I tried to negotiate and even threaten them back, claiming that I will speak"
                                       f" with the police but I am afraid that made them even more angry. ", diary,
                                       "-----", "-----", "Afternoon", '\n'.join(inventory))
                                    ui(f"' Over the last weeks they sent two of their trusted mafioso's to follow me "
                                       f"and record every single move that I make' ", diary, "-----", "-----",
                                       "Afternoon", '\n'.join(inventory))
                                    ui(f"' Last night, a loud noise woke me up. I got up and looked out of the window "
                                       f"and I am sure that I saw someone hiding in the woods' ", diary, "-----",
                                       "-----", "Afternoon", '\n'.join(inventory))
                                    ui(f"' In case that someone finds this diary and I am dead, please sent this people"
                                       f" in prison' ", diary, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                    ui(f"* In the very last page of the diary you read the names: {menu.mafioso_1.name}"
                                       f" Smith, Don Emilio Bianchi, Marco Marconi, Christina Colombo, Petro Rossi *",
                                       diary, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                    ui(f"* These are the names of the richest and most powerful families in the entire "
                                       f"city! *",
                                       default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                    ui(f"~ If what Uncle wrote here is true then that explains why these families are "
                                       f"some of the wealthiest in the entire country.\n I should talk with the "
                                       f"police!", player, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                    loop_ah = False
                                    looper = False
                                    loop = False
                            # If player has no clue about the code then let them break the loop and do something else
                                elif c == "quit":
                                    loop_ah = False
                                # Generic frustration when the safe code is not correct.
                                else:
                                    ui(f"* Damn it! Wrong pass *", player, "-----", "-----", "Afternoon",
                                       '\n'.join(inventory))
                        elif c == "d":
                            looper = False
                        else:
                            ui(f"* Invalid choice! Please try again!  *", default, "-----", "-----", "Afternoon",
                               '\n'.join(inventory))
            # Start a branch for searching the living room
            elif c == "b":
                # Get the number of items from the list if the inventory is full the start act 3
                total_needed_items = len(inventory)
                if total_needed_items >= 7:
                    loop = False
                else:
                    ui(f"* The living room is a place were you could hide a lot of things. *\n* There might be "
                       f"something interesting here *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                    ui(f"~ There must be a clue somewhere around here", living_room, "-----", "-----", "Afternoon",
                       '\n'.join(inventory))
                    looper = True
                    while looper:
                        sub_win = curses.newwin(4, 84, 25, 30)

                        sub_win.addstr("I will: [a] Search near the fireplace. [b] Just look around.\n      "
                                       " [c] I want to look for clues somewhere else \nType [a-c]: ")
                        sub_win.refresh()

                        c = sub_win.getkey()
                        # Search for clues around the fireplace
                        if c == "a":
                            ui(f"* The fireplace is somewhere were you could hide a lot of things *\n* There might be "
                               f"something good here *", fireplace, "-----", "-----", "Afternoon", '\n'.join(inventory))
                            # Set the lighter object as a str
                            lighter = "Lighter"
                            # Check if the player entered the room before and if the player took the lighter If player
                            # enters for first time or returned to pick the lighter then show lighter in the drawer
                            if lighter not in inventory:
                                ui(f"Near the fireplace you find a small drawer. You open it and inside you find"
                                   f" only a lighter", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                loop_ah = True
                                while loop_ah:
                                    lighter_win = curses.newwin(4, 84, 25, 30)

                                    lighter_win.addstr("Take the lighter?: [a] Yes. [b] No.\n \nType [a-b]: ")
                                    lighter_win.refresh()

                                    c = lighter_win.getkey()
                                    if c == "a":
                                        needed_items.append("Lighter")
                                        inventory.append("Lighter")
                                        loop_ah = False
                                    elif c == "b":
                                        loop_ah = False
                                    else:
                                        ui(f" Invalid choice! Please try again! ", default, "-----", "-----",
                                           "Afternoon", '\n'.join(inventory))
                            # If the player enters the room x times and at some point took the lighter then
                            # show an empty drawer
                            elif lighter in inventory:
                                ui(f"* You open a small drawer but there is nothing important in there. *", default,
                                   "-----", "-----", "Afternoon", '\n'.join(inventory))
                                ui(f"~ ok I think I am done with this room ", player, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                        elif c == "b":
                            ui(f"* Just by looking around the massive room you notice the artwork on the walls *",
                               living_room,
                               "-----", "-----", "Afternoon", '\n'.join(inventory))
                            ui(f"* At some point you notice a weird painting on the wall *", room_O,
                               "-----", "-----", "Afternoon", '\n'.join(inventory))
                            # Set the key object as a str
                            key_one = "key"
                            # Control if the player entered the room before and if the player took the key
                            # If player enters for first time or returned to pick the key then show key on the painting
                            if key_one not in inventory:
                                ui(f"* The painting seems to represent the stars in the sky and on it you find a start "
                                   f"shaped key * "f"\n~ Someone hid the key on the painting....", painting, "-----",
                                   "-----", "Afternoon", '\n'.join(inventory))
                                loop_ah = True
                                while loop_ah:
                                    key_win = curses.newwin(4, 84, 25, 30)

                                    key_win.addstr("Take the key?: [a] Yes. [b] No.\n \nType [a-b]: ")
                                    key_win.refresh()

                                    c = key_win.getkey()
                                    if c == "a":
                                        # Append the key in the needed items to progress the game
                                        needed_items.append("key")
                                        # Add the key in the inventory
                                        inventory.append("Key")
                                        loop_ah = False
                                    elif c == "b":
                                        loop_ah = False
                                    else:
                                        ui(f" Invalid choice! Please try again! ", default, "-----", "-----",
                                           "Afternoon", '\n'.join(inventory))
                            # If the player enters the room x times and at some point took the lighter then show
                            # an empty drawer
                            elif key_one in inventory:
                                ui(f"* It's just an weird painting. Nothing to see here *", painting, "-----", "-----",
                                   "Afternoon", '\n'.join(inventory))
                            ui(f"~ ok I think I am done with this room ", player, "-----", "-----", "Afternoon",
                               '\n'.join(inventory))
                        elif c == "c":
                            looper = False
                        else:
                            ui(f" Invalid choice! Please try again! ", default, "-----", "-----", "Afternoon",
                               '\n'.join(inventory))
            # Start a branch for searching the kitchen
            elif c == "c":
                # Get the number of items from the list
                total_needed_items = len(inventory)
                if total_needed_items >= 7:
                    loop = False
                else:
                    # Let the player explore the kitchen
                    ui(f"* The kitchen is always a good place to visit *", default, "-----", "-----", "Afternoon",
                       '\n'.join(inventory))
                    mafioso_item = f"{menu.mafioso_1.item}"
                    # Check if the player found the item linked to the mafioso and depending on that either show
                    # nothing within the kitchen or let the user enter and grab the item
                    if mafioso_item not in inventory:
                        ui(f"* While there is not much here, you find out a {menu.mafioso_1.item} in the ground *",
                           kitchen, "-----", "-----", "Afternoon", '\n'.join(inventory))
                        loop_ah = True
                        while loop_ah:
                            item_win = curses.newwin(4, 84, 25, 30)
                            # Give the player choices for the places where clues may be hidden
                            item_win.addstr(f"Take {menu.mafioso_1.item}?: [a] Yes,  [b] No \nType [a-b]: ")
                            counter_win.refresh()

                            c = item_win.getkey()

                            if c == "a":
                                # Set clue on the needed items for the progression of the game
                                needed_items.append("maf_item")
                                inventory.append(f"{menu.mafioso_1.item}")
                                loop_ah = False
                            elif c == "b":
                                loop_ah = False
                            else:
                                ui(f"* Invalid choice! Please try again!  *", default, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                        ui(f"~ Lets keep searching!", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                    elif mafioso_item in inventory:
                        ui(f"~ Unfortunately there is nothing to do here\nMaybe I should drop by the convenience "
                           f"store later and grab something to eat!", player, "-----", "-----", "Afternoon",
                           '\n'.join(inventory))
            # Start a branch for searching the staffroom
            elif c == "d":
                # Get the number of items from the list
                total_needed_items = len(inventory)
                if total_needed_items >= 7:
                    loop = False
                else:
                    # Set a clue [assassins hair] in an str and then give ability to store it in the inventory
                    mafioso_hair = "A strand of black hair"
                    # If the player enter for the first time give them the ability to choose if they want a clue
                    if mafioso_hair not in inventory:
                        ui(f"~ Uncle Ben trusted a lot his staff. Maybe I shouldn't search here.", default, "-----",
                           "-----", "Afternoon", '\n'.join(inventory))
                        ui(f"* While you walk around the room you find out a {menu.mafioso_1.hair} strand of hair in "
                           f"the ground *", staff_room, "-----", "-----", "Afternoon", '\n'.join(inventory))
                        loop_ah = True
                        while loop_ah:
                            hair_win = curses.newwin(4, 84, 25, 30)
                            # Give the player choices for the places where clues may be hidden
                            hair_win.addstr(f"Take black strand of hair?: [a] Yes,  [b] No \nType [a-b]: ")
                            hair_win.refresh()

                            c = hair_win.getkey()

                            if c == "a":
                                # Add item to needed items list to progress the game
                                needed_items.append("hair")
                                inventory.append(f"A strand of {menu.mafioso_1.hair} hair")
                                loop_ah = False
                            elif c == "b":
                                loop_ah = False
                            else:
                                ui(f"* Invalid choice! Please try again!  *", default, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                        ui(f"~ Lets see what else is around in this house!", default, "-----", "-----", "Afternoon",
                           '\n'.join(inventory))
                    # If the player has been here and has taken the hair send him to the other rooms
                    elif mafioso_hair in inventory:
                        ui(f"~ The staff room seems nice but there is nothing for me here!", player, "-----", "-----",
                           "Afternoon", '\n'.join(inventory))
            else:
                ui(f"* Invalid choice! Please try again!  *", default, "-----", "-----", "Afternoon",
                   '\n'.join(inventory))

        ui(f"* While you are still looking around the house for clues you hear a window breaking *", default, "-----",
           "-----", "Afternoon", '\n'.join(inventory))
        ui(f"~ Did someone break in the house? \n~ What should I do now?", player, "-----", "-----", "Afternoon",
           '\n'.join(inventory))
        # Start a loop for the 3rd act of the game
        # Here the player chooses how to respond to the house intruder.
        # Based on the choice the player may 1) run-hide-escape 2)Hide-Fight-Die 3)Instantly die
        loop = True
        while loop:
            counter_win = curses.newwin(4, 84, 25, 30)
            # Give the player choices for the places where clues may be hidden
            counter_win.addstr("I will: [a] Try to get out of the house [b] Hide.\n [c] Do nothing.\n \nType [a-d]: ")
            counter_win.refresh()

            c = counter_win.getkey()
            # Players tries to escape from the house unnoticed
            # Eventually ends up out of the house
            # If meanwhile the player finds the code for the safe he can instantly end the game
            if c == "a":
                ui(f"~ I should better run and get out of the house! ", player, "-----", "-----", "Afternoon",
                   '\n'.join(inventory))
                ui(f"* While you try to escape you hear footsteps from the next room *", default, "-----", "-----",
                   "Night", '\n'.join(inventory))
                # Let the player choose a place to hide
                looper = True
                while looper:
                    run_win = curses.newwin(4, 84, 25, 30)
                    # Give the player choices for the places where clues may be hidden
                    run_win.addstr("I will: [a] Hide in the Staff room. [b] Hide in the kitchen.\n [c] Hide in the "
                                   "living room.\n \nType [a-c]: ")
                    run_win.refresh()

                    q = run_win.getkey()
                    # Hide in the staff room
                    if q == "a":
                        ui(f"* Without even thinking about it you quickly hide in a closet in the staff room *",
                           default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                        ui(f"~ Ok I m probably safe here. Now what though... ", player, "-----", "-----", "Afternoon",
                           '\n'.join(inventory))
                        # Simple while loop for the last decision of the player
                        # Call the police or run towards the front door
                        loop_ah = True
                        while loop_ah:
                            r_win = curses.newwin(4, 84, 25, 30)
                            # Display the choices to the player
                            r_win.addstr(
                                "I should: [a] Stay hidden and call the police. [b] Run towards the front door"
                                "\n \nType [a-b]: ")
                            r_win.refresh()

                            f = r_win.getkey()
                            # Let the player call the police and wait for them
                            if f == "a":
                                ui(f"* At once you pick up your cellphone and call 911 *", default, "-----", "-----",
                                   "Afternoon", '\n'.join(inventory))
                                ui(f"* The police tells you to wait were you are until they sent help *",
                                   default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                ui(f"* While you wait hidden in the closet you see the intruder enter the room *",
                                   mafioso, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                ui(f"* He seems to be searching for something in this room *", mafioso, "-----",
                                   "-----", "Afternoon", '\n'.join(inventory))
                                re_loop = True
                                while re_loop:
                                    re_win = curses.newwin(4, 84, 25, 30)
                                    # Display the choices to the player
                                    re_win.addstr(
                                        "I should: [a] Stay hidden and hope for the best. [b] Try to sneak out of the "
                                        "room in a Metal gear solid fashion\n \nType [a-b]: ")
                                    re_win.refresh()

                                    f = r_win.getkey()
                                    if f == "a":
                                        ui(f"* The man is searching all over the room and and he sounds frustrated. *"
                                           f"\n* Suddenly he makes a turn and looks in the closet where you are hiding "
                                           f"*", mafia_the_t_g, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"* With one quick move he opens the closet's door and sees you *",
                                           mafioso, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"~ I was looking for you all this time! You shouldn't have come back in "
                                           f"this house", mafioso, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"~ You will never get away with this. Neither you nor the others that hired"
                                           f" you", player, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"* Within a second the man takes his gun and shoots you three times *\n "
                                           f"* You are now dead *", gun, "-----", "-----", "Afternoon",
                                           '\n'.join(inventory))
                                        ui(f"* Bad luck {menu.main_player.name}! Feel free to try again or even choose"
                                           f" a different path *", game_over, "-----", "-----", "Afternoon",
                                           '\n'.join(inventory))
                                        quit()
                                    elif f == "b":
                                        ui(f"* You wait for a while hidden in the closet and you decide to secretly get"
                                           f" out *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"* It may be dangerous but no matter the odds you decide to run towards the"
                                           f" main entrance and get out of the house *", default, "-----", "-----",
                                           "Afternoon", '\n'.join(inventory))
                                        ui(f"* Without making any noise at all you get to the entrance and slowly open "
                                           f"the door and get out *", default, "-----", "-----", "Afternoon",
                                           '\n'.join(inventory))
                                        re_loop = False
                                        loop = False
                                        loop_ah = False
                                    else:
                                        ui(f"* Invalid input please try again *", default, "-----", "-----",
                                           "Afternoon", '\n'.join(inventory))
                            # Let the player try and run to the main door
                            elif f == "b":
                                ui(f"* You wait for a while hidden in a closet and there are no signs of intruders in"
                                   f" the house *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                ui(f"* It may be dangerous but no matter the odds you decide to run towards the main "
                                   f"entrance and get out of the house *", default, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                                ui(f"* Without making any noise at all you get to the entrance and slowly open the "
                                   f"door and get out *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                loop_ah = False
                                loop = False
                            else:
                                ui(f"* Invalid input please try again! *", default, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                        looper = False
                    elif q == "b":
                        ui(f"* Without even thinking about it you quickly hide in a closet in the kitchen *",
                           default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                        ui(f"~ Ok I m probably safe here. Now what though... ", player, "-----", "-----", "Afternoon",
                           '\n'.join(inventory))
                        # Simple while loop for the last decision of the player
                        # Call the police or run towards the front door
                        loop_ah = True
                        while loop_ah:
                            r_win = curses.newwin(4, 84, 25, 30)
                            # Display the choices to the player
                            r_win.addstr(
                                "I should: [a] Stay hidden and call the police. [b] Run towards the front door"
                                "\n \nType [a-b]: ")
                            r_win.refresh()

                            f = r_win.getkey()
                            # Let the player call the police and wait for them
                            if f == "a":
                                ui(f"* At once you pick up your cellphone and call 911 *", default, "-----", "-----",
                                   "Afternoon", '\n'.join(inventory))
                                ui(f"* The police tells you to wait were you are until they sent help *",
                                   default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                ui(f"* While you wait hidden in the closet you see the intruder enter the room *",
                                   mafioso, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                ui(f"* He seems to be searching for something in this room *", mafioso, "-----",
                                   "-----", "Afternoon", '\n'.join(inventory))
                                re_loop = True
                                while re_loop:
                                    re_win = curses.newwin(4, 84, 25, 30)
                                    # Display the choices to the player
                                    re_win.addstr(
                                        "I should: [a] Stay hidden and hope for the best. [b] Try to sneak out of the "
                                        "room in a Metal gear solid fashion\n \nType [a-b]: ")
                                    re_win.refresh()

                                    f = r_win.getkey()
                                    if f == "a":
                                        ui(f"* The man is searching all over the room and and he sounds frustrated. *"
                                           f"\n* Suddenly he makes a turn and looks in the closet where you are hiding "
                                           f"*", mafia_the_t_g, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"* With one quick move he opens the closet's door and sees you *",
                                           mafioso, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"~ I was looking for you all this time! You shouldn't have come back in "
                                           f"this house", mafioso, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"~ You will never get away with this. Neither you nor the others that hired"
                                           f" you", player, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"* Within a second the man takes his gun and shoots you three times *\n "
                                           f"* You are now dead *", gun, "-----", "-----", "Afternoon",
                                           '\n'.join(inventory))
                                        ui(f"* Bad luck {menu.main_player.name}! Feel free to try again or even choose"
                                           f" a different path *", game_over, "-----", "-----", "Afternoon",
                                           '\n'.join(inventory))
                                        quit()
                                    elif f == "b":
                                        ui(f"* You wait for a while hidden in the closet and you decide to secretly get"
                                           f" out *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"* It may be dangerous but no matter the odds you decide to run towards the"
                                           f" main entrance and get out of the house *", default, "-----", "-----",
                                           "Afternoon", '\n'.join(inventory))
                                        ui(f"* Without making any noise at all you get to the entrance and slowly open "
                                           f"the door and get out *", default, "-----", "-----", "Afternoon",
                                           '\n'.join(inventory))
                                        re_loop = False
                                        loop = False
                                        loop_ah = False
                                    else:
                                        ui(f"* Invalid input please try again *", default, "-----", "-----",
                                           "Afternoon", '\n'.join(inventory))
                            # Let the player try and run to the main door
                            elif f == "b":
                                ui(f"* You wait for a while hidden in a closet and there are no signs of intruders in"
                                   f" the house *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                ui(f"* It may be dangerous but no matter the odds you decide to run towards the main "
                                   f"entrance and get out of the house *", default, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                                ui(f"* Without making any noise at all you get to the entrance and slowly open the "
                                   f"door and get out *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                loop_ah = False
                                loop = False
                            else:
                                ui(f"* Invalid input please try again! *", default, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                        looper = False
                    # Player hides in the living room
                    elif q == "c":
                        ui(f"* Without even thinking about it you quickly hide in a closet in the living room *",
                           default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                        ui(f"~ Ok I m probably safe here. Now what though... ", player, "-----", "-----", "Afternoon",
                           '\n'.join(inventory))
                        # Simple while loop for the last decision of the player
                        # Call the police or run towards the front door
                        loop_ah = True
                        while loop_ah:
                            r_win = curses.newwin(4, 84, 25, 30)
                            # Display the choices to the player
                            r_win.addstr(
                                "I should: [a] Stay hidden and call the police. [b] Run towards the front door"
                                "\n \nType [a-b]: ")
                            r_win.refresh()

                            f = r_win.getkey()
                            # Let the player call the police and wait for them
                            if f == "a":
                                ui(f"* At once you pick up your cellphone and call 911 *", default, "-----", "-----",
                                   "Afternoon", '\n'.join(inventory))
                                ui(f"* The police tells you to wait were you are until they sent help *",
                                   default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                ui(f"* While you wait hidden in the closet you see the intruder enter the room *",
                                   mafioso, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                ui(f"* He seems to be searching for something in this room *", mafioso, "-----",
                                   "-----", "Afternoon", '\n'.join(inventory))
                                re_loop = True
                                while re_loop:
                                    re_win = curses.newwin(4, 84, 25, 30)
                                    # Display the choices to the player
                                    re_win.addstr(
                                        "I should: [a] Stay hidden and hope for the best. [b] Try to sneak out of the "
                                        "room in a Metal gear solid fashion\n \nType [a-b]: ")
                                    re_win.refresh()

                                    f = r_win.getkey()
                                    if f == "a":
                                        ui(f"* The man is searching all over the room and and he sounds frustrated. *"
                                           f"\n* Suddenly he makes a turn and looks in the closet where you are hiding "
                                           f"*", mafia_the_t_g, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"* With one quick move he opens the closet's door and sees you *",
                                           mafioso, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"~ I was looking for you all this time! You shouldn't have come back in "
                                           f"this house", mafioso, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"~ You will never get away with this. Neither you nor the others that hired"
                                           f" you", player, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"* Within a second the man takes his gun and shoots you three times *\n "
                                           f"* You are now dead *", gun, "-----", "-----", "Afternoon",
                                           '\n'.join(inventory))
                                        ui(f"* Bad luck {menu.main_player.name}! Feel free to try again or even choose"
                                           f" a different path *", game_over, "-----", "-----", "Afternoon",
                                           '\n'.join(inventory))
                                        quit()
                                    elif f == "b":
                                        ui(f"* You wait for a while hidden in the closet and you decide to secretly get"
                                           f" out *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                        ui(f"* It may be dangerous but no matter the odds you decide to run towards the"
                                           f" main entrance and get out of the house *", default, "-----", "-----",
                                           "Afternoon", '\n'.join(inventory))
                                        ui(f"* Without making any noise at all you get to the entrance and slowly open "
                                           f"the door and get out *", default, "-----", "-----", "Afternoon",
                                           '\n'.join(inventory))
                                        re_loop = False
                                        loop = False
                                        loop_ah = False
                                    else:
                                        ui(f"* Invalid input please try again *", default, "-----", "-----",
                                           "Afternoon", '\n'.join(inventory))
                            # Let the player try and run to the main door
                            elif f == "b":
                                ui(f"* You wait for a while hidden in a closet and there are no signs of intruders in"
                                   f" the house *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                ui(f"* It may be dangerous but no matter the odds you decide to run towards the main "
                                   f"entrance and get out of the house *", default, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                                ui(f"* Without making any noise at all you get to the entrance and slowly open the "
                                   f"door and get out *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                                loop_ah = False
                                loop = False
                            else:
                                ui(f"* Invalid input please try again! *", default, "-----", "-----", "Afternoon",
                                   '\n'.join(inventory))
                        looper = False
            # The player hides and then takes a series of decisions that either kill him or save him.
            # If the player survives the he ends up out of the house with the police
            # If meanwhile the player finds the code for the safe he can instantly end the game
            elif c == "b":
                ui(f"* The best thing to do is to quickly hide in the closet and see what is going on *", default,
                   "-----", "-----", "Afternoon", '\n'.join(inventory))
                ui(f"* The time passes and suddenly someone enters the room and is searching for either you or "
                   f"something completely else *\n* Unfortunately its too dark and you can't really see the person nor"
                   f" what exactly is happening*", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                loop_ah = True
                while loop_ah:
                    r_win = curses.newwin(4, 84, 25, 30)
                    # Give the player choices for the places where clues may be hidden
                    r_win.addstr(
                        "I should: [a] Stay hidden and try to call the police when possible. [b] Try to fight the"
                        " intruder without any weapons\n \nType [a-b]: ")
                    r_win.refresh()

                    f = r_win.getkey()
                    if f == "a":
                        ui(f"* You wait and wait and after a while you pick up your cellphone and call 911 *", default,
                           "-----", "-----", "Afternoon", '\n'.join(inventory))
                        ui(f"* The police informs you to wait were you are and wait until they sent you help *",
                           default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                        ui(f"* You wait for a while hidden in a closet and there are no signs of intruders in the"
                           f" house *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                        ui(f"* It may be dangerous but no matter the odds you decide to run towards the main "
                           f"entrance and get out of the house *", default, "-----", "-----", "Afternoon",
                           '\n'.join(inventory))
                        ui(f"* Without making any noise at all you get in the entrance and slowly open the door and get"
                           f" outside *", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
                        loop_ah = False
                        loop = False
                    elif f == "b":
                        ui(f"* Without hesitation you get out of the closets safety and rush out *", default, "-----",
                           "-----", "Afternoon", '\n'.join(inventory))
                        ui(f"* The once mysterious figure in the room can now be easily seen *"
                           f"\n[Mysterious man]: You must be {menu.main_player.name} I assume....\n You know, if you "
                           f"had stayed hidden I would have left you alone. Now you give me no other choice", mafioso,
                           "-----", "-----", "Afternoon", '\n'.join(inventory))
                        ui(f"* You hit the man as hard as you can but it's pointless! *\n* After all you are just a "
                           f"simple {menu.main_player.role} not a fighter *", player, "-----", "-----", "Afternoon",
                           '\n'.join(inventory))
                        ui(f"* In the very end you try to land a few more hits but it's late. *\n The assassin takes"
                           f" his gun and shoots you two times ", gun, "-----", "-----", "Afternoon",
                           '\n'.join(inventory))
                        ui(f"* Bad luck {menu.main_player.name} you lost! Feel free to try again or even choose"
                           f" a different path *", game_over, "-----", "-----", "Afternoon", '\n'.join(inventory))
                        quit()
                    else:
                        ui(f"~ Invalid input please try again!", default, "-----", "-----", "Afternoon",
                           '\n'.join(inventory))
            # The player does nothing and dies
            elif c == "c":
                ui(f"* For some reason you decided to do nothing..... *", player, "-----", "-----", "Afternoon",
                   '\n'.join(inventory))
                ui(f"* You are completely frozen and can't escape at this point *", default, "-----", "-----",
                   "Afternoon", '\n'.join(inventory))
                ui(f"* Suddenly you see a tall figure coming out of the other room *", default, "-----", "-----",
                   "Afternoon", '\n'.join(inventory))
                ui(f" [Mysterious man]: You made a big mistake by coming here friend ", mafioso, "-----", "-----",
                   "Afternoon", '\n'.join(inventory))
                ui(f"~ Oh please don't!\n* BAM *\n You got shot two times ", mafia_the_t_g, "-----", "-----",
                   "Afternoon", '\n'.join(inventory))
                ui(f"* Thanks for playing 'Mafia: The terminal game' *\n* Feel free to play again and try the other "
                   f"choices or just play the mini-games from the main menu*", game_over, "-----", "-----", "Afternoon",
                   '\n'.join(inventory))
                quit()
            else:
                ui(f"~ Invalid input please try again!", default, "-----", "-----", "Afternoon", '\n'.join(inventory))

        ui(f" ~ You there! What are you doing here? Why are you sneaking out of your uncles house"
           f" like that?\n* Its officer Greg *", police, "Officer Greg", "80", "Afternoon",
           '\n'.join(inventory))
        ui(f"- I came in order to collect some books that I left here a few months ago but someone"
           f" broke in the house!. You have to stop him!", player, "Officer Greg", "80",
           "Afternoon", '\n'.join(inventory))
        ui(f"~ One of the neighbors saw a strange man entering the house with a gun and called us."
           f" I assume they were right ", police, "-----", "-----",
           "Afternoon", '\n'.join(inventory))
        ui(f"* Officer Greg and another officer enter the house while you wait outside *", default,
           "-----", "-----", "Afternoon", '\n'.join(inventory))

        # show clues to police, gather all back and vote one out
        ui(f"* Suddenly you hear a gunshot from inside the house * \n ", default, "-----", "-----", "Afternoon",
           '\n'.join(inventory))
        ui(f"* Officer Greg gets out of the house and run directly to his car in order to call for backup * \n ",
           default, "-----", "-----", "Afternoon", '\n'.join(inventory))
        ui(f" At this point the story went too far and the author got extremely bored to the point were we had to hire "
           f"a new one. Here's a quick summary of what happened later on", default, "-----", "-----", "Afternoon",
           '\n'.join(inventory))
        ui(f"* The mafioso that tried to kill you shot officer Greg on his shoulder. once officer greg was out he asked"
           f" for backup and soon after a huge police chase started. The mafioso was eventually shot and was sent to "
           f"jail * \n ", default, "-----", "-----", "Afternoon", '\n'.join(inventory))
        ui(f"* The police interrogated the mafioso but he didn't want to to betray the mafia. Because of that the"
           f" police gathered all suspects in the police station and now it's you time to shine * \n ", default,
           "-----", "-----", "Afternoon", '\n'.join(inventory))
        ui(f"* All suspects are gathered in a secrete location and you must use the clues you gathered in order to find"
           f" the rest mafia members * \n ", default, "-----", "-----", "Afternoon", '\n'.join(inventory))

        # Start talking with people and add staff on your inventory in order to help find who might be mafia
        # Depending on the players role generate the rest of the players
        ui(f"* The people in the room are: {menu.civilian_1.name}, {menu.civilian_2.name}, {menu.civilian_3.name}, "
           f"{menu.civilian_4.name}, {menu.mafioso_1.name}, {menu.doctor.name}, {menu.mafioso_2.name}* \n ", default,
           "-----", "-----", "Afternoon", '\n'.join(inventory))

        # Start a loop for the interrogation phase.
        # Let the player talk with the others without any limit on time
        # Rerun this piece of code until the end of the game
        loop = True
        while loop:
            counter_win = curses.newwin(4, 84, 25, 30)

            counter_win.addstr(f" Talk with: [a] {menu.civilian_1.name} [b] {menu.civilian_2.name}, "
                               f"[c] {menu.civilian_3.name}, [d] {menu.civilian_4.name}, [e] {menu.mafioso_1.name}, "
                               f"[f] {menu.mafioso_2.name}, [g] {menu.doctor.name}, [h] Start the voting possess\n"
                               f" Type [a-h]: ", curses.A_BOLD)
            counter_win.refresh()
            active_players = ["a", "b", "c", "d", "e", "f", "g"]
            c = counter_win.getkey()

            # Search for the picked character within the active players list
            # Based on the input [a-g] specify witch character from counter_win is chosen
            # Note: Fix this so you don't need two have two active lists in the future
            if c in active_players and c == "a":
                person = menu.civilian_1
                interrogations(person)
            elif c in active_players and c == "b":
                person = menu.civilian_2
                interrogations(person)
            elif c in active_players and c == "c":
                person = menu.civilian_3
                interrogations(person)
            elif c in active_players and c == "d":
                person = menu.civilian_4
                interrogations(person)
            elif c in active_players and c == "e":
                person = menu.mafioso_1
                interrogations(person)
            elif c in active_players and c == "f":
                person = menu.mafioso_2
                interrogations(person)
            elif c in active_players and c == "g":
                person = menu.doctor
                interrogations(person)
            elif c == "h":
                looper = True
                while looper:
                    counter_win = curses.newwin(4, 84, 25, 30)
                    curses.echo()
                    counter_win.addstr(f" After this point you wont be able to speak with the other characters again!\n"
                                       f" Are you sure you are done? [Y/N]: ", curses.A_BOLD)
                    counter_win.refresh()
                    c = counter_win.getstr().decode().lower()
                    if c == "y" or "yes":
                        ui(f"* Time to vote someone out then! *", default, "-----", "-----", night,
                           '\n'.join(inventory))
                        looper = False
                        loop = False
                    elif c == "n" or "no":
                        ui(f"* OK! Sending you back now *", default, "-----", "-----", night, '\n'.join(inventory))
                        looper = False
                    else:
                        ui(f"* Invalid choice! Please type [Y/N] or [YES/NO]*", default, "-----", "-----", night,
                           '\n'.join(inventory))
            else:
                ui(f"* Player doesn't exist. Please try again *", default, "-----", "-----", night,
                   '\n'.join(inventory))

        # Create a second list with all the active players in the game.
        # This list is used only if the player is a detective
        det_active_players = [f"{menu.civilian_1.name}", f"{menu.civilian_2.name}", f"{menu.civilian_3.name}",
                              f"{menu.civilian_4.name}", f"{menu.mafioso_1.name}", f"{menu.mafioso_2.name}",
                              f"{menu.doctor.name}"]

        det_active_roles = [f"{menu.civilian_1.category}", f"{menu.civilian_2.category}", f"{menu.civilian_3.category}",
                            f"{menu.civilian_4.category}", f"{menu.mafioso_1.real_role}", f"{menu.mafioso_2.real_role}",
                            f"{menu.doctor.role}", f"{menu.main_player.role}"]

        ui(f" It is finally time for the voting process. It is important to choose carefully in order to avoid any "
           f"unexpected result", default, "-----", "-----", night, '\n'.join(inventory))
        vote_as_a_detective(det_active_players, det_active_roles)
        check(det_active_roles)

        ui(f" ~ OK that wasn't easy to be honest....", player, " ", " ", night, '\n'.join(inventory))
        ui(f"* From a distance you see an officer approaching *", default, " ", " ", night, '\n'.join(inventory))
        ui(f"~ It is late everyone. We should better continue tomorrow. We will wait for you here at the same place in"
           f" the morning ", officer_one, " ", " ", night, '\n'.join(inventory))
        ui(f"* Now it is time to go *", mafia_the_t_g, " ", " ", night, '\n'.join(inventory))
        ui(f"* This is an important part of the game. Choose carefully were you will go next*", mafia_the_t_g, " ",
           " ", night, '\n'.join(inventory))

        # Let the players go and hide/wait somewhere else until its time for the very last part of the game
        loop = True
        while loop:
            hide_win = curses.newwin(4, 84, 25, 30)

            hide_win.addstr(f" Go to : [a] Home, [b] Hotel, [c] The convenience store", curses.A_BOLD)
            hide_win.refresh()
            c = hide_win.getkey()

            if c == "a":
                ui(f"~ The night is cold and you can't hear anything as you walk downtown *", player, "-----",
                   "-----", night, '\n'.join(inventory))
                ui(f"* Suddenly you see a hooded person coming towards you *", hooded_person, "-----",
                   "-----", night, '\n'.join(inventory))
                looper = True
                while looper:
                    run_win = curses.newwin(4, 84, 25, 30)

                    run_win.addstr(f" You should: [a] Run, [b] Keep walking, [c] Do nothing", curses.A_BOLD)
                    run_win.refresh()
                    c = run_win.getkey()

                    if c == "a":
                        ui(f"* Without even thinking about it you start running faster than Forrest Gump himself *",
                           run, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* The hooded person doesn't bother to run towards you for some reason but that is a "
                           f"good thing *", default, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* You enter you house and lock the doors and windows *\n* Maybe it was nothing...Or "
                           f"that person was a mafioso *", hall, "-----", "-----", night, '\n'.join(inventory))
                        looper = False
                        loop = False
                    elif c == "b":
                        ui(f"* You decide to keep walking down the street although the hooded person seems very sus *",
                           hooded_person, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* The hooded person seems to be walking directly towards you. Something is certainly not "
                           f"right. You have to act carefully *", default, "-----", "-----", night,
                           '\n'.join(inventory))
                        loop_ah = True
                        while loop_ah:
                            run_win = curses.newwin(4, 84, 25, 30)

                            run_win.addstr(f" You should: [a] Run, [b] Keep walking, [c] Do nothing", curses.A_BOLD)
                            run_win.refresh()
                            c = run_win.getkey()

                            if c == "a":
                                ui(f"* Without even thinking about it you start running faster than Forrest Gump "
                                   f"himself *", run, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* The hooded person doesn't bother to run towards you for some reason but that is"
                                   f" a good thing *", default, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* You enter you house and lock the doors and windows *\n~ Maybe it was nothing..."
                                   f"Or that person was a mafioso who wanted to kill me*", hall, "-----", "-----",
                                   night, '\n'.join(inventory))
                                looper = False
                                loop_ah = False
                                loop = False
                            elif c == "b":
                                ui(f"* You see a suspicious hooded person and for some reason you think that the best "
                                   f"thing to do is to simply keep walking towards him him *", hooded_person, "-----",
                                   "-----", night, '\n'.join(inventory))
                                ui(f"* The hooded person comes nearer and nearer and eventually pulls a gun out *",
                                   default, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"~You got in the middle of mafias business..I hope you understand its nothing "
                                   f"personal", menu.mafioso_2.picture, menu.mafioso_2.name, "15", night,
                                   '\n'.join(inventory))
                                ui(f"* BAM *\n", gun, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* Unfortunately you lost {menu.main_player.name} *\n  Thanks for playing Mafia: "
                                   f"The terminal game! Feel free to start over and take a different path", game_over,
                                   "-----", "-----", night, '\n'.join(inventory))
                                quit()
                            elif c == "c":
                                ui(f"* You see a suspicious hooded person and for some reason you decide to not even "
                                   f"try to avoid him *", default, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* The hooded person comes nearer and nearer and eventually pulls a gun out *",
                                   default, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"~You got in the middle of mafias business..I hope you understand its nothing "
                                   f"personal", menu.mafioso_2.picture, menu.mafioso_2.name, "15", night,
                                   '\n'.join(inventory))
                                ui(f"* BAM *\n", gun, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* Unfortunately you lost {menu.main_player.name} *\n  Thanks for playing Mafia: "
                                   f"The terminal game! Feel free to start over and take a different path", game_over,
                                   "-----", "-----", night, '\n'.join(inventory))
                                quit()
                            else:
                                ui(f"* Invalid input! Please try again! *", default, "-----", "-----", night,
                                   '\n'.join(inventory))
                    elif c == "c":
                        ui(f"* You see a suspicious hooded person and for some reason you decide to not even try to "
                           f"avoid him *", default, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* The hooded person comes nearer and nearer and eventually pulls a gun out *", default,
                           "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* You got in the middle of mafias business....I hope you understand its nothing personal"
                           f" *", menu.mafioso_2.picture, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* BAM *\n", game_over, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* Unfortunately you lost {menu.main_player.name} *\n  Thanks for playing Mafia: The "
                           f"terminal game! Feel free to start over and take a different path", game_over, "-----",
                           "-----", night, '\n'.join(inventory))
                        quit()

                    else:
                        ui(f"* Invalid input! Please try again! *", default, "-----", "-----", night,
                           '\n'.join(inventory))
            elif c == "b":
                ui(f"* Today someone tried to kill you and your house is quite far away *\n~ The best thing is to go to"
                   f" the nearest hotel and stay there for the night. Last thing that I want is a surprise attack in my"
                   f" own house", player, "-----", "-----", night, '\n'.join(inventory))
                ui(f"~ Springfield is beautiful even at night when you can't really see anything", town_two, "-----",
                   "-----", night, '\n'.join(inventory))
                ui(f"* Suddenly though you see a hooded person coming towards you *", hooded_person, "-----",
                   "-----", night, '\n'.join(inventory))
                looper = True
                while looper:
                    run_win = curses.newwin(4, 84, 25, 30)

                    run_win.addstr(f" You should: [a] Run, [b] Keep walking, [c] Do nothing", curses.A_BOLD)
                    run_win.refresh()
                    c = run_win.getkey()

                    if c == "a":
                        ui(f"* Without even thinking about it you start running faster than Forrest Gump himself *",
                           run, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* The hooded person doesn't bother to run towards you for some reason but that is a "
                           f"good thing *", default, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* You enter you house and lock the doors and windows *\n* Maybe it was nothing...Or "
                           f"that person was a mafioso *", hall, "-----", "-----", night, '\n'.join(inventory))
                        looper = False
                        loop = False
                    elif c == "b":
                        ui(f"* You decide to keep walking down the street although the hooded person seems very sus *",
                           hooded_person, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* The hooded person seems to be walking directly towards you. Something is certainly not "
                           f"right. You have to act carefully *", default, "-----", "-----", night,
                           '\n'.join(inventory))
                        loop_ah = True
                        while loop_ah:
                            run_win = curses.newwin(4, 84, 25, 30)

                            run_win.addstr(f" You should: [a] Run, [b] Keep walking, [c] Do nothing", curses.A_BOLD)
                            run_win.refresh()
                            c = run_win.getkey()

                            if c == "a":
                                ui(f"* Without even thinking about it you start running faster than Forrest Gump "
                                   f"himself *", run, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* The hooded person doesn't bother to run towards you for some reason but that is "
                                   f"a good thing *", default, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* You enter you house and lock the doors and windows *\n* Maybe it was nothing..."
                                   f"Or that person was a mafioso *", hall, "-----", "-----", night,
                                   '\n'.join(inventory))
                                looper = False
                                loop_ah = False
                                loop = False
                            elif c == "b":
                                ui(f"* You see a suspicious hooded person and for some reason you think that the best "
                                   f"thing to do is to simply keep walking towards him him *", hooded_person, "-----",
                                   "-----", night, '\n'.join(inventory))
                                ui(f"* The hooded person comes nearer and nearer and eventually pulls a gun out *",
                                   default, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"~You got in the middle of mafias business..I hope you understand its nothing "
                                   f"personal", menu.mafioso_2.picture, menu.mafioso_2.name, "15", night,
                                   '\n'.join(inventory))
                                ui(f"* BAM *\n", gun, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* Unfortunately you lost {menu.main_player.name} *\n  Thanks for playing Mafia: "
                                   f"The terminal game! Feel free to start over and take a different path", game_over,
                                   "-----", "-----", night, '\n'.join(inventory))
                                quit()
                            elif c == "c":
                                ui(f"* You see a suspicious hooded person and for some reason you decide to not even "
                                   f"try to avoid him *", default, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* The hooded person comes nearer and nearer and eventually pulls a gun out *",
                                   default, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"~You got in the middle of mafias business..I hope you understand its nothing "
                                   f"personal", menu.mafioso_2.picture, menu.mafioso_2.name, "15", night,
                                   '\n'.join(inventory))
                                ui(f"* BAM *\n", gun, "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* Unfortunately you lost {menu.main_player.name} *\n  Thanks for playing Mafia: "
                                   f"The terminal game! Feel free to start over and take a different path", game_over,
                                   "-----", "-----", night, '\n'.join(inventory))
                                quit()
                            else:
                                ui(f"* Invalid input! Please try again! *", default, "-----", "-----", night,
                                   '\n'.join(inventory))
                    elif c == "c":
                        ui(f"* You see a suspicious hooded person and for some reason you decide to not even try to"
                           f" avoid him *", default, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* The hooded person comes nearer and nearer and eventually pulls a gun out *", default,
                           "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* You got in the middle of mafias business....I hope you understand its nothing personal "
                           f"*", menu.mafioso_2.picture, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* BAM *\n", game_over, "-----", "-----", night, '\n'.join(inventory))
                        ui(f"* Unfortunately you lost {menu.main_player.name} *\n  Thanks for playing Mafia: The "
                           f"terminal game! Feel free to start over and take a different path", game_over, "-----",
                           "-----", night, '\n'.join(inventory))
                        quit()

                    else:
                        ui(f"* Invalid input! Please try again! *", default, "-----", "-----", night,
                           '\n'.join(inventory))
            elif c == "c":
                if veronica_meet:
                    ui(f"* Its been a long day so you decide to go home *\n * In your way there you decide to stop by"
                       f" the convenience store *", store, "-----", "-----", night, '\n'.join(inventory))
                    ui(f"* You enter and inside you meet Veronica, the old woman that you helped before *", default,
                       "Veronica", "87", night, '\n'.join(inventory))
                    ui(f"* Welcome back {menu.main_player.name}! How can I help you? *", old_woman, "Veronica", "87",
                       night, '\n'.join(inventory))
                    looper = True
                    while looper:
                        o_win = curses.newwin(4, 84, 25, 30)

                        o_win.addstr(f" I want to: [a] Use the arcade , [b] Ask about mysterious paper, [c] Ask about"
                                     f" the local mafia, [d] 'Actually I have to go' \nType [a-d]", curses.A_BOLD)
                        o_win.refresh()
                        c = o_win.getkey()
                        if c == "a":
                            ui(f"~ I would like to play some games on the arcade is that ok? ", player, "Veronica",
                               "87", night, '\n'.join(inventory))
                            ui(f"~ No problem at all play as much as you like! ", old_woman, "Veronica", "87", night,
                               '\n'.join(inventory))
                            ui(f"* Ok lets see what games are available! *", s_screen, " ", " ", night,
                               '\n'.join(inventory))
                        # Start a loop for letting the player play the mini games until the letter [d] is given as input
                            loop_ah = True
                            while loop_ah:
                                arcade_win = curses.newwin(4, 84, 25, 30)

                                arcade_win.addstr(
                                    " [a] Play Snake      [b] Play Arakanoid\n [c] Play tetris       [d] 'I don't want"
                                    " to play!'\n \nType [a-d]: ")
                                arcade_win.refresh()

                                q = arcade_win.getkey()
                                if q == "a":
                                    snake()
                                    ui(f" ", s_screen, "-----", "-----", day, '\n'.join(inventory))
                                elif q == "b":
                                    spider_game()
                                    ui(f" ", s_screen, "-----", "-----", day, '\n'.join(inventory))
                                elif q == "c":
                                    tetris()
                                    ui(f" ", s_screen, "-----", "-----", day, '\n'.join(inventory))
                                elif q == "d":
                                    loop_ah = False
                                else:
                                    arcade_win.addstr("* Wrong input! Please try again! *")
                                    arcade_win.refresh()
                                    time.sleep(2)
                        elif c == "b":
                            ui(f"~ I found this mysterious piece of paper. Do you have any idea what it may be?",
                               player, "Veronica", "87", night, '\n'.join(inventory))
                            ui(f"~ Well let me see.", papper, "Veronica", "87", night, '\n'.join(inventory))
                            ui(f"~ There is obviously a hidden message on this piece of paper. You see when I was a "
                               f"child we used to take some lemon juice and use it as ink in order to write secrete "
                               f"messages!", old_woman, "Veronica", "87", night, '\n'.join(inventory))
                            ui(f"~ I don't understand....", player, "Veronica", "87", night, '\n'.join(inventory))
                            ui(f"~ When you use lemon juice to write on paper there is not much to be seen obviously "
                               f"but if you heat the paper the lemon will turn grey nad you will be able to read",
                               old_woman, "Veronica", "87", night, '\n'.join(inventory))
                            ui(f"~ Oh I see. Then we need something to heat the paper!", player, "Veronica", "87",
                               night, '\n'.join(inventory))
                            if lighter in inventory:
                                ui(f"Do you have a lighter a candle or anything that could help us?", old_woman,
                                   "Veronica", "87", night, '\n'.join(inventory))
                                ui(f"~ I have a lighter\n* You give the lighter to Veronica *", player, "Veronica",
                                   "87", night, '\n'.join(inventory))
                                inventory.remove(lighter)
                                ui(f"* You wait a bit while Veronica heats the paper *", default, "Veronica",
                                   "87", night, '\n'.join(inventory))
                                ui(f"~ {menu.main_player.name}, you have to come and read this", old_woman, "Veronica",
                                   "87", night, '\n'.join(inventory))
                                reveal(f"*  Read the letter *", papper, "Veronica", "87", night)
                                ui(f"~That's it. We found  a mafia member! I have to go to the police ", player,
                                   "Veronica", "87", night, '\n'.join(inventory))
                                ui(f"~ Run {menu.main_player.name} and be careful", old_woman, "Veronica",
                                   "87", night, '\n'.join(inventory))
                                ui(f"* You stand up and run towards the police to tell them what happened *", default,
                                   "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* Before we continue here is a short message from our sponsor *", default, "-----",
                                   "-----", night, '\n'.join(inventory))
                                ui(f"* Use the promo code: Mafia2022 and claim 10 000 gold and a VIP status for"
                                   f" 30 days *", raid, "-----", "-----", night, '\n'.join(inventory))
                                looper = False
                                loop = False
                            else:
                                ui(f"Do you have a lighter a candle or anything that could help us?", old_woman,
                                   "Veronica", "87", night, '\n'.join(inventory))
                                ui(f"* You check inside you pockets but nothing *\n~ No i don't have anything...",
                                   player, "Veronica", "87", night, '\n'.join(inventory))
                                ui(f"~ Don't worry I have a small lighter around here that could help us!", old_woman,
                                   "Veronica", "87", night, '\n'.join(inventory))
                                ui(f"* You wait a bit while Veronica grabs a lighter and heats the paper *", default,
                                   "Veronica", "87", night, '\n'.join(inventory))
                                ui(f"~ {menu.main_player.name}, you have to come and read this", old_woman, "Veronica",
                                   "87", night, '\n'.join(inventory))
                                reveal(f"*  Read the letter *", papper, "Veronica", "87", night)
                                ui(f"~That's it. We found  a mafia member! I have to go to the police ", player,
                                   "Veronica", "87", night, '\n'.join(inventory))
                                ui(f"~ Run {menu.main_player.name} and be careful", old_woman, "Veronica",
                                   "87", night, '\n'.join(inventory))
                                ui(f"* You stand up and run towards the police to tell them what happened *", default,
                                   "-----", "-----", night, '\n'.join(inventory))
                                ui(f"* Before we continue here is a short message from our sponsor *", default, "-----",
                                   "-----", night, '\n'.join(inventory))
                                ui(f"* Use the promo code: Mafia2022 and claim 69.420 gold and a VIP status for 69"
                                   f" days *", raid, "-----", "-----", night, '\n'.join(inventory))
                                looper = False
                                loop = False
                        elif c == "c":
                            ui(f"~ It's probably a weird question but do you know anything about the towns mafia?",
                               player, "Veronica", "87", night, '\n'.join(inventory))
                            ui(f"~ I don't know much to be honest {menu.main_player.name}. They are very secretive and "
                               f"usually stay away from us, the ordinary civilians.", old_woman, "Veronica",
                               "87", night, '\n'.join(inventory))
                            ui(f"~ Do you know who may be involved behind them? Like is any of the locals around here"
                               f" helping them?", player, "Veronica", "87", night, '\n'.join(inventory))
                            ui(f"~ I don't really know. As I said they are very secretive and keep a low profile. There"
                               f" are rumors though that {menu.mafioso_2.name} the {menu.mafioso_2.role} is working "
                               f"with them", old_woman, "Veronica", "87", night, '\n'.join(inventory))
                            ui(f"~ That's very interesting. Thank you Veronica!", player,
                               "Veronica", "87", night, '\n'.join(inventory))
                            ui(f"~ Don't even mention it {menu.main_player.name}", old_woman, "Veronica", "90", night,
                               '\n'.join(inventory))
                            ui(f"~ I should better be going now it's late", player, "Veronica", "87", night,
                               '\n'.join(inventory))
                            ui(f"~ Goodbye, take care!", old_woman, "Veronica", "90", night, '\n'.join(inventory))
                            looper = False
                            loop = False
                        elif c == "d":
                            ui(f"* I actually came here just to say hi! I have to go now! *", player, "Veronica", "87",
                               night, '\n'.join(inventory))
                            ui(f"~ Oh thank you {menu.main_player.name}! You better go home and get some rest now. See"
                               f" you next time*", old_woman, "Veronica", "87", night, '\n'.join(inventory))
                            looper = False
                            loop = False
                        else:
                            ui(f"* Invalid input! Please try again! *", default, "-----", "-----", night,
                               '\n'.join(inventory))
                else:
                    ui(f"* Its been a long day so you decide to go home *\n * In your way there you decide to stop by "
                       f"the convenience store *", store, "-----", "-----", night, '\n'.join(inventory))
                    ui(f"* You enter and inside you meet an old woman. *", default, "-----", "-----", night,
                       '\n'.join(inventory))
                    ui(f"~ Excuse sir but we are closed ", old_woman, "-----", "-----", night,
                       '\n'.join(inventory))
                    ui(f"~ Oh I am sorry I thought the store was open. Could I please buy some rice and milk? ", player,
                       "-----", "-----", night, '\n'.join(inventory))
                    ui(f"~ Well I would be willing to help you but once I needed help you ignored me *", old_woman,
                       "-----", "-----", night, '\n'.join(inventory))
                    ui(f"* Well well well..... I should have helped the old woman back then *\n~ Once again I am very "
                       f"sorry", player, "-----", "-----", night, '\n'.join(inventory))
                    ui(f"* As you turn towards the door the old woman stops you *", default, "-----", "-----", night,
                       '\n'.join(inventory))
                    ui(f"~ You were very rude for not helping me but here take these\n* The old woman hands you some "
                       f"rice and a packet of milk *", old_woman, "-----", "-----", night, '\n'.join(inventory))
                    ui(f"~ Thank you very much, you are very kind!\n* You take your things and head home *", player,
                       "-----", "-----", night, '\n'.join(inventory))
                    loop = False
            else:
                ui(f"* Invalid input! Please try again! *", default, "-----", "-----", night, '\n'.join(inventory))

        # If the player has not the secrete diary then proceed in the game and voting process
        if secret_diary is False:
            ui(f"* The next morning you return to the same place as before and get yourself ready for the voting"
               f" process*", default, "-----", "-----", day, '\n'.join(inventory))
            ui(f"~ OK everyone take a place it's time for you to vote who is the mafioso but first a word from our "
               f"sponsor...", officer_one, "-----", "-----", day, '\n'.join(inventory))
            ui(f"* Raid Shadow Legends. The entire police department is sponsored from Raid Shadow legends so please "
               f"download the game and use the promo code Police2022*", raid, " ", " ", day, '\n'.join(inventory))
            ui(f"~ Now Let the voting begin!.", officer_one, "-----", "-----", day, '\n'.join(inventory))
            vote_as_a_detective(det_active_players, det_active_roles)
            check(det_active_roles)
            ui(f"~ Now that you picked one out we will interrogate that individual and tell you what we found",
               officer_one, "-----", "-----", day, '\n'.join(inventory))
            ui(f"* Its been an hour since the last suspect was send in prison and the police/game-master made no "
               f"statements regarding the state of the case *", mafia_the_t_g, " ", " ", day, '\n'.join(inventory))
            ui(f"* While you wait you can feel the tension on the room rising *", default, "-----", "-----", day,
               '\n'.join(inventory))
            ui(f"~ Ok everyone time to gather up once more and tell us who do you think is the assassin among us",
               police, "Officer Greg", "90", day, '\n'.join(inventory))
            ui(f"~ We think the mafia is still among you people so lets get over with it",
               officer_one, "Officer Mark", "87", day, '\n'.join(inventory))
            vote_as_a_detective(det_active_players, det_active_roles)
            check(det_active_roles)
            ui(f"* For once more you voted one out but still the police has not identified the assassin *",
               default, "Officer Greg", "90", day, '\n'.join(inventory))
            ui(f"~ Come everyone we have to do this one more time, the mafia members are still here we know it", police,
               "Officer Greg", "90", day, '\n'.join(inventory))
            ui(f"~ How many more times are we going to do this officer Greg? ", player, "Officer Greg",
               "90", day, '\n'.join(inventory))
            ui(f"~ Look {menu.main_player.name} I am not the one making the rules here. Lets just get over with this",
               police, "Officer Greg", "90", day, '\n'.join(inventory))
            ui(f"* Although most of the people in the room look frustrated, they gather in order to vote one out *",
               default, " ", " ", day, '\n'.join(inventory))
            vote_as_a_detective(det_active_players, det_active_roles)
            check(det_active_roles)
            ui(f"* Apparently the mafia is hiding very VERY well. *\n* You have to try a bit harder to find who is the"
               f" impostor *", later, " ", " ", day, '\n'.join(inventory))
            ui(f"* At least this time there are not many left so it will be soon over*", mafia_the_t_g, " ", " ",
               day, '\n'.join(inventory))
            vote_as_a_detective(det_active_players, det_active_roles)
            check(det_active_roles)
            ui(f"~ At this point there are not many options so it will be easy to find the one who is sus",
               later, "Officer Greg", "90", day, '\n'.join(inventory))
            ui(f"* You are at the end of the game. At this point you either win epically or loose and try all over "
               f"again*", later, "Officer Greg", "90", day, '\n'.join(inventory))
            vote_as_a_detective(det_active_players, det_active_roles)
            check(det_active_roles)
        # If the user found the secrete diary then finish the game
        else:
            ui(f"* You Showed the diary to the police and they with it's contents they found out everything about the "
               f"mafia*", mafia_the_t_g, "  ", " ", night, '\n'.join(inventory))
            ui(f"* Finally the mafia got exposed. The last mafioso was {menu.mafioso_1.name} *\n* {menu.mafioso_1.name}"
               f" even admitted that {menu.mafioso_2.name} was involved in Ben's assassination *", default, "-----",
               "-----", night, '\n'.join(inventory))
            ui(f"* A month later since the police arrested the mafia members and Springfield looks better than ever *",
               transition_three, "-----", "-----", night, '\n'.join(inventory))
            ui(f"* The crime rates dropped by 50% and people feel safe thanks to you ! *", springfield, "-----",
               "-----", night, '\n'.join(inventory))
            ui(f"* Congratulations {menu.main_player.name}! You won the game! *", game_over, "-----", "-----", night,
               '\n'.join(inventory))


wrapper(main)
