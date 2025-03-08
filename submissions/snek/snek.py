"""
Snek. A simple snake game in the terminal.
"""

import os
import random
import sys
import termios
import time
import tty
from typing import List, Dict, Optional
import select
import signal

import colorama


colorama.init()

# Constants
CHARS = {"full_shade": "\u2588", "medium_shade": "\u2592"}
CHAR_WIDTH = 2
INITIAL_SNAKE_LENGTH = 1
INITIAL_SCORE = 1
INITIAL_HIGH_SCORE = 1
GRID_HEIGHT_OFFSET = (
    4  # Offset for the grid height (terminal.lines - GRID_HEIGHT_OFFSET)
)
GRID_WIDTH_OFFSET = (
    2  # Offset for the grid width ((terminal.columns // 2) - GRID_WIDTH_OFFSET)
)
APPLE_DENSITY = 100  # Adjust for apple density (grid_area // APPLE_DENSITY)
MIN_APPLES = 1  # Minimum number of apples
SNAKE_GROWTH_RATE = 1  # Number of segments added when eating an apple
SNAKE_MOVE_DELAY = 0.25  # Delay between snake movements (in seconds)
APPLE_SPACING = 3  # Minimum distance between apples and snake/other apples

MENU_OPTIONS: List[Dict[str, str]] = [
    {
        "no": "1",
        "name": "Apple Density",
        "key": "apple_density",
        "prompt": "Enter new Apple Density: ",
        "convert_func": int,
    },
    {
        "no": "2",
        "name": "Initial Snake Length",
        "key": "initial_snake_length",
        "prompt": "Enter new Initial Snake Length: ",
        "convert_func": int,
    },
    {
        "no": "3",
        "name": "Snake Growth Rate",
        "key": "snake_growth_rate",
        "prompt": "Enter new Snake Growth Rate: ",
        "convert_func": int,
    },
    {
        "no": "4",
        "name": "Snake Move Delay",
        "key": "snake_move_delay",
        "prompt": "Enter new Snake Move Delay: ",
        "convert_func": float,
    },
    {
        "no": "5",
        "name": "Apple Spacing",
        "key": "apple_spacing",
        "prompt": "Enter new Apple Spacing: ",
        "convert_func": int,
    },
    {
        "no": "6",
        "name": "Pride Theme",
        "key": "lgbtq_theme",
        "prompt": "",
        "convert_func": None,
    },
]


class Snake:
    """Class to represent the snake in the game."""

    def __init__(self, world: "GameWorld") -> None:
        """Initialize the Snake object."""
        self.world = world
        self.vertices: List[Dict[str, int]] = []
        self.score = INITIAL_SCORE
        self.high_score = INITIAL_HIGH_SCORE
        self.direction = "RIGHT"
        self.last_direction = "RIGHT"
        self.growth_queue: List[Dict[str, int]] = []

        # Initialize the snake with the correct length
        start_x = self.world.width // 2
        start_y = self.world.height // 2
        for i in range(self.world.config["initial_snake_length"]):
            self.vertices.append({"x": start_x - i, "y": start_y})

    def reset(self) -> None:
        """Reset the snake to its initial state."""
        self.vertices = []
        self.score = INITIAL_SCORE
        self.direction = "RIGHT"
        self.last_direction = "RIGHT"
        self.growth_queue = []

        # Initialize the snake with the correct length
        start_x = self.world.width // 2
        start_y = self.world.height // 2
        for i in range(self.world.config["initial_snake_length"]):
            self.vertices.append({"x": start_x - i, "y": start_y})

    def update_direction(self, char: Optional[str]) -> bool:
        """Update the direction of the snake based on input character."""
        if char is not None:
            last_direction = self.direction

            if char == "w" and last_direction != "DOWN":
                self.direction = "UP"
            elif char == "s" and last_direction != "UP":
                self.direction = "DOWN"
            elif char == "a" and last_direction != "RIGHT":
                self.direction = "LEFT"
            elif char == "d" and last_direction != "LEFT":
                self.direction = "RIGHT"

            if last_direction != self.direction:
                self.last_direction = last_direction
                return True  # Direction changed

        return False  # Direction unchanged


class Apples:
    """Class to represent the apples in the game."""

    def __init__(self, world: "GameWorld") -> None:
        """Initialize the Apples object."""
        self.world = world
        self.vertices: List[Dict[str, int]] = []
        self.calculate_initial_apples()

    def calculate_initial_apples(self) -> None:
        """Calculate the initial number of apples based on the grid area."""
        grid_area = self.world.width * self.world.height
        self.num_apples = max(
            MIN_APPLES, grid_area // self.world.config["apple_density"]
        )
        self.reset()

    def reset(self) -> None:
        """Reset the apples to their initial state."""
        self.vertices = []
        for _ in range(self.num_apples):
            self.add_apple()

    def add_apple(self) -> None:
        """Add a new apple to the grid."""
        attempts = 0
        while attempts < 100:  # Limit attempts to avoid infinite loops
            new_apple = {
                "x": random.randrange(0, self.world.width),
                "y": random.randrange(0, self.world.height),
            }

            if self.is_position_valid(new_apple):
                self.vertices.append(new_apple)
                if (
                    0 <= new_apple["y"] < self.world.height
                    and 0 <= new_apple["x"] < self.world.width
                ):
                    self.world.grid[new_apple["y"]][new_apple["x"]] = "A"
                break
            attempts += 1

    def is_position_valid(self, position: Dict[str, int]) -> bool:
        """Check if the position is valid for placing an apple."""
        for vertex in self.world.snake.vertices:
            if (
                abs(vertex["x"] - position["x"]) < self.world.config["apple_spacing"]
                and abs(vertex["y"] - position["y"])
                < self.world.config["apple_spacing"]
            ):
                return False

        for apple in self.vertices:
            if (
                abs(apple["x"] - position["x"]) < self.world.config["apple_spacing"]
                and abs(apple["y"] - position["y"]) < self.world.config["apple_spacing"]
            ):
                return False

        return True


class GameWorld:
    """Class to represent the game world."""

    def __init__(self, config: Dict[str, int]) -> None:
        """Initialize the GameWorld object."""
        self.config = config
        self.terminal = os.get_terminal_size()
        self.height = self.terminal.lines - GRID_HEIGHT_OFFSET
        self.width = (self.terminal.columns // CHAR_WIDTH) - GRID_WIDTH_OFFSET
        self.grid: List[List[str]] = []
        self.last_update = time.perf_counter()
        self.updating = False

        self.rainbow_colors = [
            "\033[38;5;196m",  # Red
            "\033[38;5;214m",  # Orange
            "\033[38;5;226m",  # Yellow
            "\033[38;5;46m",  # Green
            "\033[38;5;33m",  # Blue
            "\033[38;5;129m",  # Purple
        ]

        self.initialize_grid()

        self.snake = Snake(self)
        self.apples = Apples(self)

        self.reset_world()

        # Handle terminal resizing
        signal.signal(signal.SIGWINCH, self.handle_resize)

    def initialize_grid(self) -> None:
        """Initialize the grid with empty values."""
        self.grid = [["" for _ in range(self.width)] for _ in range(self.height)]

    def move_cursor_to_top(self) -> None:
        """Move the cursor to the top of the terminal."""
        print(f"\033[{self.terminal.lines}A\033[2K", end="")

    def print_world(self, print_score: bool = True) -> None:
        """Print the current state of the game world."""
        self.move_cursor_to_top()
        print(f"\r{CHARS['full_shade']*self.terminal.columns}", end="\r\n")

        if print_score:
            score_string = f"Score: {self.snake.score}"
            high_score_string = f"High Score: {self.snake.high_score}"
            print(
                f"{CHARS['full_shade']*CHAR_WIDTH}{score_string}{CHARS['full_shade']*CHAR_WIDTH}{high_score_string}{(CHARS['full_shade'] * (self.terminal.columns - GRID_HEIGHT_OFFSET - len(score_string) - len(high_score_string)))}",
                end="\r\n",
            )
        else:
            print(f"\r{CHARS['full_shade']*self.terminal.columns}", end="\r\n")

        print(f"\r{CHARS['full_shade']*self.terminal.columns}", end="\r\n")

        for row in self.grid:
            print(f"{CHARS['full_shade']*CHAR_WIDTH}", end="")
            print(
                "".join(
                    [
                        (
                            # Apples: Randomly colored trans blue or trans pink in Pride Theme
                            (
                                random.choice(
                                    [
                                        "\033[38;5;45m",  # Trans Blue
                                        "\033[38;5;213m",  # Trans Pink
                                    ]
                                )
                                + f"{CHARS['full_shade']*2}"
                                + colorama.Fore.RESET
                                if self.config["lgbtq_theme"]
                                else f"{colorama.Fore.RED}{CHARS['full_shade']*2}{colorama.Fore.RESET}"  # Default theme
                            )
                            if entity == "A"
                            else (
                                f"{self.rainbow_colors[(i // 2) % len(self.rainbow_colors)]}{CHARS['full_shade']*2}{colorama.Fore.RESET}"
                                if self.config["lgbtq_theme"]
                                and entity in ["S", "H"]  # Snake body or head
                                else (
                                    f"{colorama.Fore.GREEN}{CHARS['full_shade']*2}{colorama.Fore.RESET}"
                                    if entity == "H"  # Snake Head (if not rainbow)
                                    else (
                                        f"{colorama.Fore.RED}{CHARS['full_shade']*2}{colorama.Fore.RESET}"  # Snake Body (if not rainbow)
                                        if entity == "S"
                                        else CHARS["medium_shade"] * 2
                                    )  # Empty space
                                )
                            )
                        )
                        for i, entity in enumerate(row)
                    ]
                ),
                end="",
            )
            print(
                f"{CHARS['full_shade']*(2 if self.terminal.columns % 2 == 0 else 3)}",
                end="\r\n",
            )

        print(f"\r{CHARS['full_shade']*self.terminal.columns}", end="")

    def vertex_in_world(self, vertex: Dict[str, int]) -> bool:
        """Check if a vertex is within the bounds of the world."""
        return (vertex["x"] >= 0 and vertex["x"] < self.width) and (
            vertex["y"] >= 0 and vertex["y"] < self.height
        )

    def reset_world(self) -> None:
        """Reset the game world to its initial state."""
        self.updating = False
        self.last_update = time.perf_counter()

        # Clear the grid
        self.initialize_grid()

        # Reset the snake and apples
        self.snake.reset()
        self.apples.reset()

        # Place the snake head on the grid
        if (
            0 <= self.snake.vertices[0]["y"] < self.height
            and 0 <= self.snake.vertices[0]["x"] < self.width
        ):
            self.grid[self.snake.vertices[0]["y"]][self.snake.vertices[0]["x"]] = "H"

    def update_world(self) -> None:
        """Update the game world state."""
        if self.updating:
            return

        self.updating = True
        last_vertex = None

        # Move the snake
        for index, vertex in enumerate(self.snake.vertices):
            if 0 <= vertex["y"] < self.height and 0 <= vertex["x"] < self.width:
                self.grid[vertex["y"]][vertex["x"]] = ""

            if last_vertex is not None:
                self.snake.vertices[index], last_vertex = last_vertex, vertex.copy()
            else:
                last_vertex = vertex.copy()
                vertex["x"] += (
                    1
                    if self.snake.direction == "RIGHT"
                    else -1 if self.snake.direction == "LEFT" else 0
                )
                vertex["y"] += (
                    1
                    if self.snake.direction == "DOWN"
                    else -1 if self.snake.direction == "UP" else 0
                )

                if not self.vertex_in_world(vertex):
                    self.reset_world()
                    break

        # Check for apple collisions
        for vertex in self.snake.vertices:
            if vertex in self.apples.vertices:
                self.apples.vertices.remove(vertex)
                self.snake.score += self.config["snake_growth_rate"]

                if self.snake.score > self.snake.high_score:
                    self.snake.high_score = self.snake.score

                # Add new vertices to the growth queue
                for _ in range(self.config["snake_growth_rate"]):
                    self.snake.growth_queue.append(last_vertex.copy())

                self.apples.add_apple()

        # Handle snake growth
        while self.snake.growth_queue:
            self.snake.vertices.append(self.snake.growth_queue.pop(0))

        # Update the grid with the new snake positions
        snake_length = len(self.snake.vertices)
        for index, vertex in enumerate(self.snake.vertices[::-1]):
            if 0 <= vertex["y"] < self.height and 0 <= vertex["x"] < self.width:
                self.grid[vertex["y"]][vertex["x"]] = (
                    "H" if index == snake_length - 1 else "S"
                )

            if index == snake_length - 1:
                if vertex in self.snake.vertices[1:]:
                    self.reset_world()
                    return self.update_world()

        self.print_world()

        self.updating = False
        self.last_update = time.perf_counter()

    def handle_resize(self, _signum: int, _frame: Optional[object]) -> None:
        """Handle terminal resize events."""
        # Update terminal size and grid dimensions
        self.terminal = os.get_terminal_size()
        self.height = self.terminal.lines - GRID_HEIGHT_OFFSET
        self.width = (self.terminal.columns // 2) - GRID_WIDTH_OFFSET

        # Reinitialize the grid
        self.initialize_grid()

        # Reposition the snake and apples
        self.reset_world()

    def start_game(self) -> None:
        """Start the game loop."""
        clear_terminal()

        while True:
            if time.perf_counter() - self.last_update > self.config["snake_move_delay"]:
                self.update_world()

            char = getchar()

            if char:  # If a key is pressed
                if char == "\x1b":  # If the key is the escape key
                    break
                if self.snake.update_direction(char):  # Update snake direction
                    self.update_world()  # Immediately update the world if direction changes


def clear_terminal() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def format_option(option: str, width: int) -> str:
    """Format an option string for display."""
    return f"║ {option}".ljust(width - 1) + "║"


def getchar() -> Optional[str]:
    """Get a single character from standard input."""
    if select.select([sys.stdin], [], [], 0.0)[0]:
        return sys.stdin.read(1)

    return None


def display_menu(config: Dict[str, int], old_settings: List[int]) -> Dict[str, int]:
    """Display the configuration menu and handle user input."""

    while True:
        clear_terminal()

        width = os.get_terminal_size().columns
        horizontal_line = "═" * (width - 2)

        print(f"╔{horizontal_line}╗", end="\r\n")
        print(f"║{'Snek Configuration Menu'.center(width - 2)}║", end="\r\n")
        print(f"╠{horizontal_line}╣", end="\r\n")

        for option in MENU_OPTIONS:
            current_value = config[option["key"]] if option["key"] in config else ""
            print(
                format_option(
                    f"{option['no']}: {option['name']} (current: {current_value})",
                    width,
                ),
                end="\r\n",
            )

        print(f"╠{horizontal_line}╣", end="\r\n")
        print(format_option("Enter: Start Game", width), end="\r\n")
        print(format_option("Esc: Exit (available while in game)", width), end="\r\n")
        print(f"╚{horizontal_line}╝", end="\r\n")

        while True:
            choice = getchar()

            if choice:
                break

        clear_terminal()

        selected_option = next(
            (opt for opt in MENU_OPTIONS if opt["no"] == choice), None
        )

        if selected_option:
            if selected_option["key"] == "lgbtq_theme":
                config["lgbtq_theme"] = not config["lgbtq_theme"]
                continue

            print(selected_option["prompt"], end="", flush=True)

            value = ""

            while True:
                char = getchar()

                if char is None:
                    continue
                elif char in ("\r", "\n"):
                    break
                elif char == "\x7f":
                    value = value[:-1]
                elif char == "\x1b":
                    break
                else:
                    value += char

                print(char, end="", flush=True)

            print()

            try:
                config[selected_option["key"]] = selected_option["convert_func"](value)
            except ValueError:
                pass

        elif choice == "\r":
            break
        elif choice == "\x1b":
            fd = sys.stdin.fileno()
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            sys.exit()
        else:
            print("Invalid choice. Please try again.")
            continue

    return config


def main() -> None:
    """Main function to start the game."""

    # Configurable variables (can be changed programmatically)
    config = {
        "apple_density": APPLE_DENSITY,
        "initial_snake_length": INITIAL_SNAKE_LENGTH,
        "snake_growth_rate": SNAKE_GROWTH_RATE,
        "snake_move_delay": SNAKE_MOVE_DELAY,
        "apple_spacing": APPLE_SPACING,
        "lgbtq_theme": False,
    }

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    tty.setraw(fd)

    while True:
        config = display_menu(
            config,
            old_settings,
        )  # Display the configuration menu before starting the game

        world = GameWorld(config)
        world.start_game()


if __name__ == "__main__":
    main()
