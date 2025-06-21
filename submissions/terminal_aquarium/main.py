import os
import random
import time
import shutil

fish_types = [
    "><((('>",
    "><> ",
    "><(((º>",
    "><> ",
    "><((°> ",
    "<°)))>< ",

]

background_art = [
    # Rocks
    {"art": ["  _/\\_", " /    \\", "/_/\\/\\_\\"], "min_width": 10},
    {"art": ["   __", " _/  \\", "/      \\", "\\_/\\_/"], "min_width": 8},
    {"art": ["   ___", "  /   \\", " /     \\", "/_/\\_/\\_"], "min_width": 9},
    # Coral
    {"art": ["  |", " /|\\", "/_|_\\"], "min_width": 5},
    {"art": ["  |", " /|", "/ |"], "min_width": 4},
    {"art": ["   /\\", "  /  \\", " /_/\\_\\"], "min_width": 7},
    # Seaweed
    {"art": ["  |", " /|", "/ |"], "min_width": 4},
    {"art": ["  |", "  |/", " /|"], "min_width": 3},
    {"art": ["  /", " /|", "/ |"], "min_width": 3},
    # Starfish
    {"art": ["  *", " /|\\", "<-O->", " \\|/"], "min_width": 5},
    # Pebbles
    {"art": [" .  .", "  ..", " ."], "min_width": 4},
]

class Fish:
    def __init__(self, y, x, direction, fish_type):
        self.y = y
        self.x = x
        self.direction = direction  # 1 for right, -1 for left
        self.fish_type = fish_type if direction == 1 else fish_type[::-1]

    def move(self, width, height):
        self.x += self.direction
        # Bounce off walls
        if self.x < 0:
            self.direction = 1
            self.fish_type = self.fish_type[::-1]
            self.x = 0
        elif self.x + len(self.fish_type) > width:
            self.direction = -1
            self.fish_type = self.fish_type[::-1]
            self.x = width - len(self.fish_type)
        # Randomly move up/down
        if random.random() < 0.1:
            self.y += random.choice([-1, 1])
            self.y = max(0, min(height - 1, self.y))

class Bubble:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self):
        self.y -= 1

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def place_background(width, height):
    # Randomly place background art at the bottom of the aquarium.
    bg_map = [[" " for _ in range(width)] for _ in range(height)]
    num_items = random.randint(2, 4)
    for _ in range(num_items):
        art_obj = random.choice(background_art)
        art = art_obj["art"]
        art_height = len(art)
        art_width = max(len(line) for line in art)
        if art_width > width:
            continue
        x = random.randint(0, width - art_width)
        y = height - art_height
        for dy, line in enumerate(art):
            for dx, ch in enumerate(line):
                if ch != " ":
                    bg_map[y + dy][x + dx] = ch
    return bg_map

def draw_aquarium(fishes, bubbles, bg_map, width, height):
    aquarium = [[" " for _ in range(width)] for _ in range(height)]
    # Place background art
    for y in range(height):
        for x in range(width):
            if bg_map[y][x] != " ":
                aquarium[y][x] = bg_map[y][x]
    # Place bubbles
    for bubble in bubbles:
        if 0 <= bubble.y < height and 0 <= bubble.x < width:
            aquarium[bubble.y][bubble.x] = "o"
    # Place fish
    for fish in fishes:
        for i, ch in enumerate(fish.fish_type):
            fx = fish.x + i
            if 0 <= fx < width and 0 <= fish.y < height:
                aquarium[fish.y][fx] = ch
    print("+" + "-" * width + "+")
    for row in aquarium:
        print("|" + "".join(row) + "|")
    print("+" + "-" * width + "+")

def main():
    width, height = shutil.get_terminal_size((80, 24))
    width -= 2
    height -= 2
    num_fish = min(8, height)
    fishes = []
    for _ in range(num_fish):
        y = random.randint(0, height - 4)
        x = random.randint(0, width - 8)
        direction = random.choice([1, -1])
        fish_type = random.choice(fish_types)
        fishes.append(Fish(y, x, direction, fish_type))
    bg_map = place_background(width, height)
    bubbles = []
    try:
        while True:
            # Adds bubble from a random bottom position
            if random.random() < 0.15:
                bx = random.randint(0, width - 1)
                bubbles.append(Bubble(bx, height - 1))
            # Move bubbles up and remove those that reach the top
            for bubble in bubbles:
                bubble.move()
            bubbles = [b for b in bubbles if b.y >= 0]
            clear()
            draw_aquarium(fishes, bubbles, bg_map, width, height)
            for fish in fishes:
                fish.move(width, height)
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nAquarium closed.")

main()
