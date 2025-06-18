Welcome to ByteQuest: Terminal Edition, a classic rogue-like adventure that runs directly in your terminal. Navigate a dangerous dungeon, outsmart intelligent enemies, avoid traps, and find the key to escape. Built with pure Python, this game is a lightweight and fun demonstration of object-oriented programming and dynamic level generation.

# Features
Classic Rogue-like Gameplay: A simple yet challenging dungeon-crawl experience focused on survival and exploration.

Selectable Difficulty Levels: Choose from three distinct challenges:

* Easy: More health and fewer threats for a casual playthrough.

* Hard: The standard, balanced experience.

* Impossible: A true test of skill with low health and numerous dangers.

Dynamic Level Generation: The positions of the key, traps, and enemies are randomized for each playthrough, guaranteeing a unique experience and preventing items from overlapping.

Smart Enemy: Enemies don't just mindlessly chase you. They use a line-of-sight algorithm and a probabilistic chase mechanic, making their behavior less predictable and more strategic. You can use walls and corners to your advantage to break pursuit.

Tactical Knockback Mechanic: Colliding with an enemy knocks them back, giving you a crucial moment of breathing room and adding a layer of tactical depth to combat.

Colorful Terminal Graphics: The game uses ANSI escape codes to create a vibrant and clear visual experience, right in your command line.

# Gameplay
The objective of ByteQuest is to guide your character (@) through the dungeon to find the key (K) and then escape through the portal (O).

# The World
@: Your character.

E: An enemy. They will pursue and attack you.

K: The key. You must collect it to unlock the portal.

O: The escape portal. Becomes active once you have the key.

^: A hidden trap. Step on one, and you will lose health.

■: An impassable wall.

# Controls
The game is controlled with simple keyboard commands:

W: Move Up

A: Move Left

S: Move Down

D: Move Right

Q: Quit the game at any time.

# Requirements
This game is written in Python 3 and uses only standard libraries (os, random, time, math), so no external packages are needed. It should run on any system with Python 3 installed that supports ANSI color codes in the terminal (most modern terminals on macOS, Linux, and Windows 10/11 do).

# How to Run the Game
Make sure you have Python 3 installed on your system.

Download the game Python file (bytequest.py).

Open your terminal or command prompt.

Navigate to the directory where you saved the file.

Run the following command:

** python bytequest.py **

The game will start, and you can begin your quest
