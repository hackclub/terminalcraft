import sys
import os
import select
import time
import random
import pygame

if os.name == 'nt':
    import msvcrt
else:
    import termios
    import tty

def get_terminal_size():
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except OSError:
        return 80, 24

WIDTH, HEIGHT = get_terminal_size()
WIDTH, HEIGHT = max(40, WIDTH - 2), max(20, HEIGHT - 2)
DUNGEON = [['#' for _ in range(WIDTH)] for _ in range(HEIGHT)]
PLAYER_POS = [1, 1]
NEXT_ROOM_ICON = [WIDTH - 3, HEIGHT - 3]
START_TIME = time.time()
ROOMS_PASSED = 0
BOSS_POS = None

def show_start_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    title = """
  ____   _____    __  ____  ____         __  ____    ____  __    __  _     
 /    | / ___/   /  ]|    ||    |       /  ]|    \  /    ||  |__|  || |    
|  o  |(   \_   /  /  |  |  |  |       /  / |  D  )|  o  ||  |  |  || |    
|     | \__  | /  /   |  |  |  |      /  /  |    / |     ||  |  |  || |___ 
|  _  | /  \ |/   \_  |  |  |  |     /   \_ |    \ |  _  ||    '  ||     |
|  |  | \    |\     | |  |  |  |     \     ||  .  \|  |  | \      / |     |
|__|__|  \___| \____||____||____|     \____||__|\_||__|__|  \_/\_/  |_____|  
    """
    print(title)    
    print("Navigate with W/A/S/D and press 'CTRL + C' or 'Q' to quit.")
    print("The game will start soon!")
    time.sleep(3)
    get_key()

def show_ending_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    elapsed_time = int(time.time() - START_TIME)
    print("""
    CONGRATULATIONS!
    You have defeated the dungeon boss and emerged victorious!
    Thank you for playing!
    """)
    print(f"Total Time: {elapsed_time} seconds")
    time.sleep(5)
    sys.exit()

def generate_boss_room():
    global DUNGEON, NEXT_ROOM_ICON, BOSS_POS
    DUNGEON = [['#' for _ in range(WIDTH)] for _ in range(HEIGHT)]
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    boss_room_size = min(WIDTH, HEIGHT) // 2
    
    for i in range(center_y - boss_room_size // 2, center_y + boss_room_size // 2):
        for j in range(center_x - boss_room_size // 2, center_x + boss_room_size // 2):
            DUNGEON[i][j] = '.'
    
    BOSS_POS = [center_x, center_y]
    DUNGEON[center_y][center_x] = 'B'  # Boss symbol
    PLAYER_POS[0], PLAYER_POS[1] = center_x - boss_room_size // 4, center_y
    DUNGEON[PLAYER_POS[1]][PLAYER_POS[0]] = '■'
    
    NEXT_ROOM_ICON = None  # No exit until boss is defeated

def generate_dungeon():
    global DUNGEON, NEXT_ROOM_ICON, ROOMS_PASSED
    
    if ROOMS_PASSED >= 5:
        generate_boss_room()
        return
    
    DUNGEON = [['#' for _ in range(WIDTH)] for _ in range(HEIGHT)]
    rooms = []
    num_rooms = random.randint(8, 15)

    for _ in range(num_rooms):
        w, h = random.randint(5, 10), random.randint(4, 8)
        x, y = random.randint(1, WIDTH - w - 1), random.randint(1, HEIGHT - h - 1)
        rooms.append((x, y, w, h))

        for i in range(y, y + h):
            for j in range(x, x + w):
                DUNGEON[i][j] = '.'

    for i in range(len(rooms) - 1):
        x1, y1, _, _ = rooms[i]
        x2, y2, _, _ = rooms[i + 1]
        while x1 != x2:
            DUNGEON[y1][x1] = '.'
            x1 += 1 if x1 < x2 else -1
        while y1 != y2:
            DUNGEON[y1][x1] = '.'
            y1 += 1 if y1 < y2 else -1

    start_room = rooms[0]
    PLAYER_POS[0], PLAYER_POS[1] = start_room[0] + 1, start_room[1] + 1
    DUNGEON[PLAYER_POS[1]][PLAYER_POS[0]] = '■'
    
    farthest_room = rooms[-1]
    NEXT_ROOM_ICON = [farthest_room[0] + farthest_room[2] - 2, farthest_room[1] + farthest_room[3] - 2]
    DUNGEON[NEXT_ROOM_ICON[1]][NEXT_ROOM_ICON[0]] = '>'

def draw_dungeon():
    elapsed_time = int(time.time() - START_TIME)
    print("\033[H", end="")
    print(f"Time: {elapsed_time} seconds | Room: {ROOMS_PASSED}".ljust(WIDTH))
    
    color_map = {
        '#': "\033[1;30m",  # Gray for walls
        '■': "\033[1;96m",  # Bright Cyan for player
        'B': "\033[1;31m",  # Red for boss
        '>': "\033[1;33m",  # Yellow for exit
        '.': "\033[1;97m"   # Bright White for floor
    }
    
    for row in DUNGEON:
        for char in row:
            print(f"{color_map.get(char, '')}{char}\033[0m", end="")
        print("")


def move_player(dx, dy):
    global ROOMS_PASSED
    new_x = PLAYER_POS[0] + dx
    new_y = PLAYER_POS[1] + dy
    
    if DUNGEON[new_y][new_x] == '#':
        return
    
    DUNGEON[PLAYER_POS[1]][PLAYER_POS[0]] = '.'
    PLAYER_POS[0] = new_x
    PLAYER_POS[1] = new_y
    
    if BOSS_POS and PLAYER_POS == BOSS_POS:
        show_ending_screen()
    
    if NEXT_ROOM_ICON and PLAYER_POS == NEXT_ROOM_ICON:
        ROOMS_PASSED += 1
        generate_dungeon()
    else:
        DUNGEON[PLAYER_POS[1]][PLAYER_POS[0]] = '■'

def get_key():
    if os.name == 'nt':
        if msvcrt.kbhit():
            return msvcrt.getch().decode('utf-8')
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
            if rlist:
                return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return None


def play_music():
    pygame.mixer.init()
    pygame.mixer.music.load("8 Bit Dungeon.mp3")
    pygame.mixer.music.play(-1)


def main():
    play_music()
    show_start_screen()
    os.system('cls' if os.name == 'nt' else 'clear')
    generate_dungeon()
    draw_dungeon()
    
    while True:
        key = get_key()
        if key:
            key = key.lower()
            if key == 'w':
                move_player(0, -1)
            elif key == 's':
                move_player(0, 1)
            elif key == 'a':
                move_player(-1, 0)
            elif key == 'd':
                move_player(1, 0)
            elif key == 'q':
                print("Exiting game...")
                break
            draw_dungeon()
        time.sleep(0.05)

if __name__ == "__main__":
    main()
