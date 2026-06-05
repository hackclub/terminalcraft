import random
import time
import shutil


class Colors:
    RESET = "\033[0m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    WHITE = "\033[97m"
    MAGENTA = "\033[95m"


fish_types = [
    {"art": "><((('>", "color": Colors.BLUE},
    {"art": "><> ", "color": Colors.MAGENTA},
    {"art": "><(((º>", "color": Colors.YELLOW},
    {"art": "><> ", "color": Colors.CYAN},
    {"art": "><((°> ", "color": Colors.GREEN},
    {"art": "<°)))>< ", "color": Colors.BLUE},
]

background_art = [
    # Rocks
    {"art": ["  _/\\_", " /    \\", "/_/\\/\\_\\"], "min_width": 10, "color": Colors.WHITE},
    {"art": ["   __", " _/  \\", "/      \\", "\\_/\\_/"], "min_width": 8, "color": Colors.WHITE},
    {"art": ["   ___", "  /   \\", " /     \\", "/_/\\_/\\_"], "min_width": 9, "color": Colors.WHITE},
    # Coral
    {"art": ["  |", " /|\\", "/_|_\\"], "min_width": 5, "color": Colors.MAGENTA},
    {"art": ["  |", " /|", "/ |"], "min_width": 4, "color": Colors.MAGENTA},
    # Seaweed
    {"art": ["   /\\", "  /  \\", " /_/\\_\\"], "min_width": 7, "color": Colors.GREEN},
    {"art": ["  |", " /|", "/ |"], "min_width": 4, "color": Colors.GREEN},
    {"art": ["  |", "  |/", " /|"], "min_width": 3, "color": Colors.GREEN},
    # Starfish
    {"art": ["  *", " /|\\", "<-O->", " \\|/"], "min_width": 5, "color": Colors.YELLOW},
    # Pebbles
    {"art": [" .  .", "  ..", " ."], "min_width": 4, "color": Colors.WHITE},
]

class Fish:

    def __init__(self, y, x, direction, art, color):
        self.y = y
        self.x = x
        self.direction = direction  # 1 for right, -1 for left
        self.art = art if direction == 1 else art[::-1]
        self.color = color

    def move(self, width, height):
        self.x += self.direction
        # Bounce off walls
        if self.x < 0:
            self.direction = 1
            self.art = self.art[::-1]
            self.x = 0
        elif self.x + len(self.art) > width:
            self.direction = -1
            self.art = self.art[::-1]
            self.x = width - len(self.art)
        # Randomly move up/down
        if random.random() < 0.1:
            self.y += random.choice([-1, 1])
            self.y = max(0, min(height - 1, self.y))

class Bubble:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # --- New: Bubbles are now cyan ---
        self.color = Colors.CYAN

    def move(self):
        self.y -= 1

def clear():

    print("\033[H", end="")

def place_background(width, height):

    bg_map = [[(" ", Colors.RESET) for _ in range(width)] for _ in range(height)]
    num_items = random.randint(3, 5)
    for _ in range(num_items):
        art_obj = random.choice(background_art)
        art = art_obj["art"]
        color = art_obj["color"]
        art_height = len(art)
        art_width = max(len(line) for line in art)
        if art_width > width:
            continue
        x = random.randint(0, width - art_width)
        y = height - art_height
        for dy, line in enumerate(art):
            for dx, ch in enumerate(line):
                if ch != " ":
                    bg_map[y + dy][x + dx] = (ch, color)
    return bg_map

def draw_aquarium(fishes, bubbles, bg_map, width, height):
    aquarium = [row[:] for row in bg_map]

    for bubble in bubbles:
        if 0 <= bubble.y < height and 0 <= bubble.x < width:
            aquarium[bubble.y][bubble.x] = ("o", bubble.color)

    for fish in fishes:
        for i, ch in enumerate(fish.art):
            fx = fish.x + i
            if 0 <= fx < width and 0 <= fish.y < height:
                aquarium[fish.y][fx] = (ch, fish.color)

    output_str = []
    output_str.append(Colors.BLUE + "+" + "-" * width + "+" + Colors.RESET)
    for row in aquarium:
        line_str = [Colors.BLUE + "|" + Colors.RESET]
        current_color = Colors.RESET
        for char, color in row:
            if color != current_color:
                line_str.append(color)
                current_color = color
            line_str.append(char)

        if current_color != Colors.RESET:
            line_str.append(Colors.RESET)
        line_str.append(Colors.BLUE + "|" + Colors.RESET)
        output_str.append("".join(line_str))
    output_str.append(Colors.BLUE + "+" + "-" * width + "+" + Colors.RESET)

    print("\n".join(output_str))

def main():
    width, height = shutil.get_terminal_size((80, 24))
    width -= 2
    height -= 2
    num_fish = min(8, height // 2)
    fishes = []
    for _ in range(num_fish):
        y = random.randint(0, height - 4)
        x = random.randint(0, width - 10)
        direction = random.choice([1, -1])
        fish_obj = random.choice(fish_types)
        fishes.append(Fish(y, x, direction, fish_obj["art"], fish_obj["color"]))

    bg_map = place_background(width, height)
    bubbles = []
    try:
        while True:
            if random.random() < 0.15:
                bx = random.randint(1, width - 2)
                bubbles.append(Bubble(bx, height - 1))

            for bubble in bubbles:
                bubble.move()
            bubbles = [b for b in bubbles if b.y >= 0]

            clear()
            draw_aquarium(fishes, bubbles, bg_map, width, height)

            for fish in fishes:
                fish.move(width, height)

            time.sleep(0.2)
    except KeyboardInterrupt:

        print(f"\n{Colors.RESET}Aquarium closed.")

if __name__ == "__main__":
    main()
