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
TOTAL_LEVELS = 5

# --- Game Element Graphics ---
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
    os.system('cls' if os.name == 'nt' else 'clear')

def get_single_char():
    if 'msvcrt' in sys.modules:
        return msvcrt.getch().decode('utf-8')
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def show_title_screen():
    clear_screen()
    print(TITLE_ART)
    input("\n\x1b[1m           Press Enter to start your quest...            \x1b[0m")

def select_difficulty():
    clear_screen()
    print("\n\x1b[1mSelect Your Challenge:\x1b[0m\n")
    print("  \x1b[92m1. Easy\x1b[0m      (Fewer walls and dangers)")
    print("  \x1b[93m2. Hard\x1b[0m      (A balanced, standard challenge)")
    print("  \x1b[91m3. Impossible\x1b[0m (Dense mazes and many threats)\n")
    
    while True:
        choice = input("Enter your choice (1, 2, or 3): ")
        if choice in ['1', '2', '3']:
            return {'1': 'easy', '2': 'hard', '3': 'impossible'}[choice]
        print("\n\x1b[90mInvalid selection. Please enter 1, 2, or 3.\x1b[0m")

class Entity:
    def __init__(self, x, y, char):
        self.x, self.y, self.char = x, y, char

    def move(self, dx, dy, walls):
        new_x, new_y = self.x + dx, self.y + dy
        if 0 <= new_x < WIDTH and 0 <= new_y < HEIGHT and [new_x, new_y] not in walls:
            self.x, self.y = new_x, new_y

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_CHAR)
        self.health = 10
        self.has_key = False

class Enemy(Entity):
    CHASE_PROBABILITY = 0.75

    def __init__(self, x, y):
        super().__init__(x, y, ENEMY_CHAR)

    def has_line_of_sight(self, target_pos, walls):
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
        distance = abs(player_pos[0] - self.x) + abs(player_pos[1] - self.y)
        if distance <= 8 and self.has_line_of_sight(player_pos, walls) and random.random() < self.CHASE_PROBABILITY:
            dx, dy = player_pos[0] - self.x, player_pos[1] - self.y
            move_dx = (1 if dx > 0 else -1) if abs(dx) > abs(dy) else 0
            move_dy = (1 if dy > 0 else -1) if abs(dy) >= abs(dx) and move_dx == 0 else 0
            self.move(move_dx, move_dy, walls)
        else:
            self.move(*random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)]), walls)

class Game:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.current_level = 1
        self.player = Player(1, 1)
        self.message_log = []
        self._setup_level()

    def _setup_level(self):
        self.player.x, self.player.y = 1, 1
        self.player.has_key = False
        player_start_pos = [1, 1]
        self.portal_pos = [WIDTH - 2, HEIGHT - 2]

        settings = {
            'easy': {'health': 15, 'enemies': 1, 'traps': 3},
            'hard': {'health': 10, 'enemies': 2, 'traps': 5},
            'impossible': {'health': 5, 'enemies': 4, 'traps': 8}
        }
        
        if self.current_level == 1: self.player.health = settings[self.difficulty]['health']
        
        num_enemies = settings[self.difficulty]['enemies'] + self.current_level - 1
        num_traps = settings[self.difficulty]['traps'] + (self.current_level - 1)
        
        wall_counts = {
            'easy': (15, 25), 'hard': (30, 40), 'impossible': (45, 55)
        }
        min_walls, max_walls = wall_counts[self.difficulty]
        wall_count = random.randint(min_walls, max_walls)
        
        self.walls = []
        for _ in range(wall_count):
            start_x, start_y = random.randint(1, WIDTH - 2), random.randint(1, HEIGHT - 2)
            length = random.randint(3, 7)
            direction = random.choice(['h', 'v'])
            for i in range(length):
                wall_pos = None
                if direction == 'h' and start_x + i < WIDTH - 1: wall_pos = [start_x + i, start_y]
                elif direction == 'v' and start_y + i < HEIGHT - 1: wall_pos = [start_x, start_y + i]

                if wall_pos and wall_pos != player_start_pos and wall_pos != self.portal_pos and wall_pos not in self.walls:
                    self.walls.append(wall_pos)

        spawn_points = [pos for y in range(HEIGHT) for x in range(WIDTH) 
                        if (pos := [x, y]) not in self.walls and pos != player_start_pos and pos != self.portal_pos]
        
        random.shuffle(spawn_points)
        
        self.key_pos = spawn_points.pop()
        self.enemies = [Enemy(*spawn_points.pop()) for _ in range(num_enemies) if spawn_points]
        self.traps = [spawn_points.pop() for _ in range(num_traps) if spawn_points]

    def next_level(self):
        self.current_level += 1
        self.player.health += 3
        self.message_log.append(f"\x1b[96m✨ Level Cleared! Proceeding to Level {self.current_level}. (+3 HP)\x1b[0m")
        self.render()
        time.sleep(2)
        self._setup_level()

    def display_art_screen(self, art, message=""):
        clear_screen()
        print(art)
        if message: print(f"\n{message}")
        input("\nPress Enter to continue...")

    def render(self):
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
        print(f"\n\x1b[1m❤️  Health: {self.player.health:<5} {key_status}   Level: {self.current_level}/{TOTAL_LEVELS}\x1b[0m")
        print("\x1b[1mLegend: @-Player E-Enemy K-Key O-Portal ^-Trap ■-Wall\x1b[0m")
        # --- FIX: Corrected ANSI escape code ---
        print("\n\x1b[1mControls: W/A/S/D to move, Q to quit.\x1b[0m")

        for msg in self.message_log: print(msg)
        self.message_log.clear()

    def update_game_state(self):
        player_pos = [self.player.x, self.player.y]
        
        for enemy in self.enemies[:]:
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
        while True:
            self.render()

            if self.player.health <= 0:
                self.display_art_screen(GAME_OVER_ART, "\x1b[1m\x1b[91m💀 You have perished in the dungeon.\x1b[0m")
                break
            
            if self.player.has_key and [self.player.x, self.player.y] == self.portal_pos:
                if self.current_level < TOTAL_LEVELS:
                    self.next_level()
                    continue
                else:
                    self.display_art_screen(VICTORY_ART, "\x1b[1m\x1b[92m🚪 You have successfully escaped all dungeons! Victory is yours.\x1b[0m")
                    break

            move = get_single_char().upper()
            if move == 'Q':
                print("\n\x1b[90m👋 Fleeing the dungeon... for now.\x1b[0m")
                break
                
            if move in (move_map := {'W': (0, -1), 'A': (-1, 0), 'S': (0, 1), 'D': (1, 0)}):
                self.player.move(*move_map[move], self.walls)
                for enemy in self.enemies:
                    enemy.update_ai([self.player.x, self.player.y], self.walls)
                
                self.update_game_state()
                
                if self.message_log:
                    self.render()
                    time.sleep(0.75)

def main():
    show_title_screen()
    chosen_difficulty = select_difficulty()
    game = Game(difficulty=chosen_difficulty)
    game.run()

if __name__ == '__main__':
    main()
