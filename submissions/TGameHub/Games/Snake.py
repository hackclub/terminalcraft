"""This is an edited version of https://github.com/kevinmarquesp/snake_game"""
from curses.textpad import rectangle
from datetime import datetime
import curses, random

class Globals:
    """
    GLOBALS: Stores most of the essential information for the game.
    These can be accessed by other classes.
    """

    def __init__(self):
        self.keys = {
            "left":     [97, 104, 260],
            "down":     [115, 106, 258],
            "up":       [119, 107, 259],
            "right":    [100, 108, 261],
            "return":   [32, 111, 10]
        }
        self.opposite = {
            "right": "left",
            "left": "right",
            "up": "down",
            "down": "up"
        }

        self.menu_list = ["Play", "Scoreboard", "Exit"]
        self.directions_list = ["left", "down", "up", "right"]


class Menu(Globals):
    """
    MENU: Displays the initial options on the screen and stores the selected item in self.selected_item.
    """

    def __init__(self):
        super().__init__()
        self.selected_item = 0

    @property
    def start(self):
        curses.wrapper(self.__run)

    def __run(self, screen):
        curses.curs_set(False)
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
        self.__loop(screen)

    def __loop(self, screen):
        while True:
            self.__y_len, self.__x_len = screen.getmaxyx()
            screen.clear()
            rectangle(screen, 5, 12, self.__y_len - 6, self.__x_len - 15)
            self.__show_menu(screen)

            if self.__handle_keyboard(screen):
                break
            screen.refresh()

    def __show_menu(self, screen):
        for index, text in enumerate(self.menu_list):
            x = self.__x_len // 2 - len(text) // 2
            y = self.__y_len // 2 - len(self.menu_list) // 2 + index

            if self.selected_item == index:
                screen.attron(curses.color_pair(1))

            screen.addstr(y, x, text)
            screen.attroff(curses.color_pair(1))

    def __handle_keyboard(self, screen):
        key = screen.getch()

        if key in self.keys["up"] and self.selected_item > 0:
            self.selected_item -= 1
        elif key in self.keys["down"] and self.selected_item < len(self.menu_list) - 1:
            self.selected_item += 1
        elif key in self.keys["return"]:
            return True
        return False


class Play(Globals):
    """
    PLAY: Manages the game logic, stores the score and the date when the game started.
    """

    def __init__(self, snake_body_fill, apple_fill):
        super().__init__()
        self.snake_body_fill = snake_body_fill
        self.apple_fill = apple_fill
        self.pause = False
        self.score = None

    @property
    def start(self):
        curses.wrapper(self.__run)

    def __run(self, screen):
        self.__y_len, self.__x_len = screen.getmaxyx()
        curses.curs_set(False)
        screen.nodelay(True)
        screen.clear()
        rectangle(screen, 2, 5, self.__y_len - 3, self.__x_len - 6)
        self.score = [str(datetime.today()), 0]
        self.__load_content(screen)
        self.__loop(screen)

    def __loop(self, screen):
        while True:
            screen.timeout(60 if self.current_direction in ["up", "down"] else 40)
            self.__get_new_direction(screen, self.current_direction)

            if not self.pause:
                self.__move_snake_head(screen)
                self.__remove_tail(screen)

            if self.__check_loss_conditions():
                break
            screen.refresh()

    def __load_content(self, screen):
        self.snake_body = [[self.__y_len // 2, self.__x_len // 2]]
        self.current_direction = "right"
        self.__spawn_apple(screen)
        screen.addstr(self.snake_body[0][0], self.snake_body[0][1], self.snake_body_fill)

    def __get_apple_position(self):
        while True:
            apple = [random.randint(3, self.__y_len - 4), random.randint(6, self.__x_len - 7)]
            if apple not in self.snake_body:
                break
        return apple

    def __spawn_apple(self, screen):
        self.apple = self.__get_apple_position()
        screen.addstr(self.apple[0], self.apple[1], self.apple_fill)

    def __get_new_direction(self, screen, direction):
        key = screen.getch()
        new_direction = None

        for dir_name, dir_keys in self.keys.items():
            if key in dir_keys:
                new_direction = dir_name

        if new_direction in self.keys and new_direction != self.opposite[direction] and new_direction != "return":
            self.current_direction = new_direction
        elif new_direction == "return":
            self.pause = not self.pause

    def __move_snake_head(self, screen):
        head = self.snake_body[0]
        if self.current_direction == "right":
            new_head = [head[0], head[1] + 1]
        elif self.current_direction == "left":
            new_head = [head[0], head[1] - 1]
        elif self.current_direction == "up":
            new_head = [head[0] - 1, head[1]]
        elif self.current_direction == "down":
            new_head = [head[0] + 1, head[1]]

        screen.addstr(new_head[0], new_head[1], self.snake_body_fill)
        self.snake_body.insert(0, new_head)

    def __remove_tail(self, screen):
        if self.snake_body[0] == self.apple:
            self.__spawn_apple(screen)
            self.score[1] += 1
            screen.addstr(2, 7, f" Score: {self.score[1]} ")
        else:
            tail = self.snake_body.pop()
            screen.addstr(tail[0], tail[1], " ")

    def __check_loss_conditions(self):
        head = self.snake_body[0]
        if (
            head[0] <= 2 or head[0] >= self.__y_len - 3
            or head[1] <= 5 or head[1] >= self.__x_len - 6
            or head in self.snake_body[1:]
        ):
            return True
        return False


class ScoreBoard(Globals):
    """
    SCOREBOARD: Stores the game score history along with the date of each game.
    Responsible for loading and displaying the formatted list on the screen.
    """

    def __init__(self):
        super().__init__()
        self.score_list = []
        self.y_value = 3
        self.x_value = 7

    @property
    def start(self):
        curses.wrapper(self.__run)

    def __run(self, screen):
        curses.curs_set(False)
        screen.clear()
        self.__loop(screen)

    def __loop(self, screen):
        while True:
            for key, value in enumerate(self.score_list):
                try:
                    screen.addstr(self.y_value + key, self.x_value, f"[{value[0]}] >>> {value[1]}")
                except:
                    pass

            if screen.getch() in self.keys["return"]:
                break

    def add_score(self, score):
        if not self.score_list:
            self.score_list.append(score)
        else:
            for key, value in enumerate(self.score_list):
                if score[1] > value[1]:
                    self.score_list.insert(key, score)
                    break
                elif score[1] == value[1]:
                    self.score_list.insert(key + 1, score)
                    break
                elif key == len(self.score_list) - 1:
                    self.score_list.append(score)
                    break
def play():
    menu = Menu()
    score_board = ScoreBoard()
    play = Play("█", "0")

    while True:
        menu.start

        if menu.selected_item == 0:
            try:
                play.start
            except:
                pass
            score_board.add_score(play.score[:])
        elif menu.selected_item == 1:
            score_board.start
        else:
            break