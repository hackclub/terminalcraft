import os
import random
import time

# --- Platform-specific imports for single-key input ---
try:
    # For Unix-like systems (Linux, macOS)
    import sys
    import tty
    import termios
except ImportError:
    # For Windows
    import msvcrt

# --- Game Configuration ---
WIDTH = 30
HEIGHT = 12

# --- Game Element Graphics ---
# ANSI escape codes provide color. \x1b[92m is green, and \x1b[0m resets the color.
PLAYER_CHAR = '\x1b[92m@\x1b[0m'  # Green
ENEMY_CHAR = '\x1b[91mE\x1b[0m'   # Red
KEY_CHAR = '\x1b[93mK\x1b[0m'     # Yellow
TRAP_CHAR = '\x1b[95m^\x1b[0m'    # Magenta
WALL_CHAR = '\x1b[90m■\x1b[0m'     # Gray
PORTAL_CHAR = '\x1b[94mO\x1b[0m'  # Blue
EMPTY_CHAR = ' '

# --- ASCII Art for Different Screens ---
TITLE_ART = """
\x1b[1m\x1b[44m
██████╗ ██╗   ██╗████████╗███████╗ ██████╗ ██╗   ██╗███████╗███████╗████████╗
██╔══██╗╚██╗ ██╔╝╚══██╔══╝██╔════╝██╔═══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝
██████╔╝ ╚████╔╝    ██║   █████╗  ██║   ██║██║   ██║█████╗  ███████╗   ██║   
██╔══██╗  ╚██╔╝     ██║   ██╔══╝  ██║▄▄ ██║██║   ██║██╔══╝  ╚════██║   ██║   
██████╔╝   ██║      ██║   ███████╗╚██████╔╝╚██████╔╝███████╗███████║   ██║   
╚═════╝    ╚═╝      ╚═╝   ╚══════╝ ╚══▀▀═╝  ╚═════╝ ╚══════╝╚══════╝   ╚═╝   
                                                                             
\x1b[0m
"""

GAME_OVER_ART = """
\x1b[1m\x1b[41m
 ██████╗  █████╗ ███╗   ███╗███████╗     ██████╗ ██╗   ██╗███████╗██████╗ 
██╔════╝ ██╔══██╗████╗ ████║██╔════╝    ██╔═══██╗██║   ██║██╔════╝██╔══██╗
██║  ███╗███████║██╔████╔██║█████╗      ██║   ██║██║   ██║█████╗  ██████╔╝
██║   ██║██╔══██║██║╚██╔╝██║██╔══╝      ██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗
╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗    ╚██████╔╝ ╚████╔╝ ███████╗██║  ██║
 ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝     ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝
\x1b[0m
"""

VICTORY_ART = """
\x1b[1m\x1b[42m
██╗   ██╗██╗ ██████╗████████╗ ██████╗ ██████╗ ██╗   ██╗
██║   ██║██║██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝
██║   ██║██║██║        ██║   ██║   ██║██████╔╝ ╚████╔╝ 
╚██╗ ██╔╝██║██║        ██║   ██║   ██║██╔══██╗  ╚██╔╝  
 ╚████╔╝ ██║╚██████╗   ██║   ╚██████╔╝██║  ██║   ██║   
  ╚═══╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
\x1b[0m
"""

# --- Helper Functions ---
def clear_screen():
    """Clears the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_single_char():
    """Gets a single character from standard input without requiring Enter."""
    if 'msvcrt' in sys.modules:
        # Windows implementation
        return msvcrt.getch().decode('utf-8')
    else:
        # Unix/Linux/macOS implementation
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


def show_title_screen():
    """Displays the title screen and waits for the user to press Enter."""
    clear_screen()
    print(TITLE_ART)
    input("\n\x1b[1m           Press Enter to start your quest...            \x1b[0m")

def select_difficulty():
    """Prompts the user to select a difficulty level and returns the choice."""
    clear_screen()
    print("\n\x1b[1mSelect Your Challenge:\x1b[0m\n")
    print("  \x1b[92m1. Easy\x1b[0m      (More health, fewer dangers)")
    print("  \x1b[93m2. Hard\x1b[0m      (A balanced, standard challenge)")
    print("  \x1b[91m3. Impossible\x1b[0m (Low health, many threats)\n")
    
    while True:
        choice = input("Enter your choice (1, 2, or 3): ")
        if choice in ['1', '2', '3']:
            return {'1': 'easy', '2': 'hard', '3': 'impossible'}[choice]
        print("\n\x1b[90mInvalid selection. Please enter 1, 2, or 3.\x1b[0m")

class Entity:
    """A base class for any object in the game that has a position."""
    def __init__(self, x, y, char):
        self.x = x
        self.y = y
        self.char = char

    def move(self, dx, dy, walls):
        """Moves the entity by dx and dy if the path is not blocked."""
        new_x, new_y = self.x + dx, self.y + dy
        if 0 <= new_x < WIDTH and 0 <= new_y < HEIGHT and [new_x, new_y] not in walls:
            self.x, self.y = new_x, new_y

class Player(Entity):
    """The player character, managing health and key status."""
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_CHAR)
        self.health = 10
        self.has_key = False

class Enemy(Entity):
    """An enemy character."""
    CHASE_PROBABILITY = 0.75

    def __init__(self, x, y):
        super().__init__(x, y, ENEMY_CHAR)

    def has_line_of_sight(self, target_pos, walls):
        """Checks if there is a clear line of sight to the target."""
        x1, y1, x2, y2 = self.x, self.y, target_pos[0], target_pos[1]
        dx, dy = x2 - x1, y2 - y1
        steps = max(abs(dx), abs(dy))
        if steps == 0: return True
        
        x_inc, y_inc = dx / steps, dy / steps
        for i in range(1, steps + 1):
            if [round(x1 + i * x_inc), round(y1 + i * y_inc)] in walls:
                return False
        return True

    def update_ai(self, player_pos, walls):
        """Enemy Logic: Chase the player only if close, visible, and a random chance succeeds."""
        distance = abs(player_pos[0] - self.x) + abs(player_pos[1] - self.y)
        should_chase = distance <= 8 and self.has_line_of_sight(player_pos, walls) and random.random() < self.CHASE_PROBABILITY

        if should_chase:
            dx, dy = player_pos[0] - self.x, player_pos[1] - self.y
            move_dx = (1 if dx > 0 else -1) if abs(dx) > abs(dy) else 0
            move_dy = (1 if dy > 0 else -1) if abs(dy) >= abs(dx) and move_dx == 0 else 0
            self.move(move_dx, move_dy, walls)
        else:
            self.move(*random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)]), walls)

class Game:
    """Manages the main game state, rendering, and game loop."""
    def __init__(self, difficulty):
        self.player = Player(1, 1)
        self.portal_pos = [WIDTH - 2, HEIGHT - 2]
        self.walls = [[x, 5] for x in range(5, 25)] + [[12, y] for y in range(6, 10)]
        self.message_log = []

        self._setup_level(difficulty)

    def _setup_level(self, difficulty):
        """Generates and places level objects without overlap based on difficulty."""
        settings = {
            'easy': {'health': 15, 'enemies': 1, 'traps': 3},
            'hard': {'health': 10, 'enemies': 2, 'traps': 5},
            'impossible': {'health': 5, 'enemies': 4, 'traps': 8}
        }
        
        self.player.health = settings[difficulty]['health']
        num_enemies = settings[difficulty]['enemies']
        num_traps = settings[difficulty]['traps']
        
        spawn_points = []
        for y in range(HEIGHT):
            for x in range(WIDTH):
                pos = [x, y]
                if pos not in self.walls and pos != [self.player.x, self.player.y] and pos != self.portal_pos:
                    spawn_points.append(pos)
        
        random.shuffle(spawn_points)
        
        self.key_pos = spawn_points.pop()
        
        self.enemies = []
        for _ in range(num_enemies):
            x, y = spawn_points.pop()
            self.enemies.append(Enemy(x, y))
            
        self.traps = []
        for _ in range(num_traps):
            self.traps.append(spawn_points.pop())

    def display_art_screen(self, art, message=""):
        """Displays a full-screen message like the title or game over screen."""
        clear_screen()
        print(art)
        if message: print(f"\n{message}")
        input("Press Enter to continue...")

    def render(self):
        """Draws the entire game screen, including all objects and UI elements."""
        clear_screen()
        grid = [[EMPTY_CHAR for _ in range(WIDTH)] for _ in range(HEIGHT)]

        for x, y in self.walls: grid[y][x] = WALL_CHAR
        if not self.player.has_key: grid[self.key_pos[1]][self.key_pos[0]] = KEY_CHAR
        grid[self.portal_pos[1]][self.portal_pos[0]] = PORTAL_CHAR
        for x, y in self.traps: grid[y][x] = TRAP_CHAR
        for enemy in self.enemies: grid[enemy.y][enemy.x] = enemy.char
        grid[self.player.y][self.player.x] = self.player.char

        print("\n\x1b[1m\x1b[44m     BYTEQUEST TERMINAL EDITION     \x1b[0m")
        print("╔" + "═" * WIDTH + "╗")
        for row in grid: print("║" + "".join(row) + "║")
        print("╚" + "═" * WIDTH + "╝")

        key_status = '🔑 Key Collected' if self.player.has_key else '   No Key   '
        print(f"\n\x1b[1m❤️  Health: {self.player.health:<5} {key_status}\x1b[0m")
        print("\x1b[1mLegend: @-Player E-Enemy K-Key O-Portal ^-Trap ■-Wall\x1b[0m")
        print("\n\x1b[1mControls: W/A/S/D to move, Q to quit.\x1b[0m")

        for msg in self.message_log: print(msg)
        self.message_log.clear()

    def update_game_state(self):
        """Checks for collisions and other game events after a move."""
        player_pos = [self.player.x, self.player.y]
        
        for enemy in self.enemies:
            if [enemy.x, enemy.y] == player_pos:
                self.player.health -= 2
                self.message_log.append("\x1b[91m⚔️ You collided with an enemy! (-2 HP)\x1b[0m")
                possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                random.shuffle(possible_moves)
                for dx, dy in possible_moves:
                    new_pos = [enemy.x + dx, enemy.y + dy]
                    if 0 <= new_pos[0] < WIDTH and 0 <= new_pos[1] < HEIGHT and new_pos not in self.walls:
                        enemy.x, enemy.y = new_pos[0], new_pos[1]
                        self.message_log.append("\x1b[90mThe impact knocks the enemy back!\x1b[0m")
                        break

        if player_pos in self.traps:
            self.player.health -= 1
            self.traps.remove(player_pos)
            self.message_log.append("\x1b[95m💥 You stumbled into a trap! (-1 HP)\x1b[0m")
        
        if not self.player.has_key and player_pos == self.key_pos:
            self.player.has_key = True
            self.message_log.append("\x1b[93m🔑 You found the key! The escape portal is now active.\x1b[0m")

    def run(self):
        """The main game loop, handling input, rendering, and state updates."""
        while True:
            self.render()

            if self.player.health <= 0:
                self.display_art_screen(GAME_OVER_ART, "\x1b[1m\x1b[91m💀 You have perished in the dungeon.\x1b[0m")
                break
            if self.player.has_key and [self.player.x, self.player.y] == self.portal_pos:
                self.display_art_screen(VICTORY_ART, "\x1b[1m\x1b[92m🚪 You have successfully escaped! Victory is yours.\x1b[0m")
                break

            move = get_single_char().upper()
            if move == 'Q':
                print("\n\x1b[90m👋 Fleeing the dungeon... for now.\x1b[0m")
                break
                
            move_map = {'W': (0, -1), 'A': (-1, 0), 'S': (0, 1), 'D': (1, 0)}
            if move in move_map:
                dx, dy = move_map[move]
                self.player.move(dx, dy, self.walls)
                for enemy in self.enemies:
                    enemy.update_ai([self.player.x, self.player.y], self.walls)
                
                self.update_game_state()
                
                if self.message_log:
                    self.render()
                    time.sleep(0.75)

def main():
    """Sets up and runs the game."""
    show_title_screen()
    chosen_difficulty = select_difficulty()
    game = Game(difficulty=chosen_difficulty)
    game.run()

if __name__ == '__main__':
    main()
