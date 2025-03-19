import os
import curses
import shutil
import time

maze = [
    "#############################################################",
    "#@#   #         #           #                               #",
    "# # ### ### ### ##### ##### ####### ################### ### #",
    "# # #   # # #         #   # #     # #       #           # # #",
    "# # # ### # ########### ### # ### # ####### # ########### # #",
    "# #   #   #           #   # # # # # #       #         #   # #",
    "# # ### ############# ### # # # # # # ##### ######### # ### #",
    "# #   #     #         #   #   #   # # #   #   # #     #   # #",
    "# ### ##### # ######### ####### ### # # # ### # # ####### # #",
    "# #   #     #   # #     #       # # #   # #     # #       # #",
    "# # ### ### ### # # ### # ####### # ##### ####### # ####### #",
    "# #     # #   # #   # #   #   #         #     #   # #     # #",
    "# ####### # ### # ### ##### ### ####### ##### # ### # ### # #",
    "# #       # #   # #     #       #     # #     # #     #   # #",
    "# ##### # # # ### # ### ### ##### ### # # ##### ### ### # # #",
    "#     # #   # # # # #     #   #   #   #   #   #   # #   # # #",
    "##### ####### # # # ##### ### # ### ####### # # # ### ### # #",
    "#   # #       # # #   # #   # #   #         # # # #   #   # #",
    "### # # ####### # ### # ### ##### ########### # # # ##### # #",
    "#   # # #       #     #   #       #     #     # # #     # # #",
    "# ### # # ##### ####### ########### ### # ####### # ### # # #",
    "# #   # # #   #         #     #   # #   #   #     #   # # # #",
    "# # ### # # # # ######### ### # # # # ##### # ####### # ### #",
    "#       #   # #             #   #   #         #       #    E#",
    "#############################################################"
]

navigator_position = [1, 1]

cell_mapping = {
    '#': 1,
    ' ': 0,
    '@': 0,
    'E': 0
}

player_grid_position = [1, 1]

def block_for_seconds(seconds):
    end_time = time.time() + seconds
    while time.time() < end_time:
        pass

def display_loading_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    columns, rows = shutil.get_terminal_size()
    art = """
████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ███╗ █████╗ ███████╗███████╗
╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗ ████║██╔══██╗╚══███╔╝██╔════╝
   ██║   █████╗  ██████╔╝██╔████╔██║██║██╔████╔██║███████║  ███╔╝ █████╗  
   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╔╝██║██╔══██║ ███╔╝  ██╔══╝  
   ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚═╝ ██║██║  ██║███████╗███████╗
   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝
""".strip('\n')
    art_lines = art.splitlines()
    top_padding = (rows - len(art_lines)) // 2
    print("\n" * top_padding, end='')
    for line in art_lines:
        print(line.center(columns))
    block_for_seconds(3)
    os.system('cls' if os.name == 'nt' else 'clear')

    additional_art = """
        ┬┌┐┌  ┌┬┐┬ ┬┌─┐  ┌┐ ┬  ┌─┐┌┐┌┬┌─  ┌─┐┌─┐┬─┐┌─┐┌─┐┌┐┌              
        ││││   │ ├─┤├┤   ├┴┐│  ├─┤│││├┴┐  └─┐│  ├┬┘├┤ ├┤ │││              
        ┴┘└┘   ┴ ┴ ┴└─┘  └─┘┴─┘┴ ┴┘└┘┴ ┴  └─┘└─┘┴└─└─┘└─┘┘└┘              
┌─┐┬  ┬┌─┐┬┌─  ┌─┐┌┐┌  ┌─┐┬─┐┬─┐┌─┐┬ ┬  ┬┌─┌─┐┬ ┬  ┌┬┐┌─┐  ┌─┐┌┬┐┌─┐┬─┐┌┬┐
│  │  ││  ├┴┐  ├─┤│││  ├─┤├┬┘├┬┘│ ││││  ├┴┐├┤ └┬┘   │ │ │  └─┐ │ ├─┤├┬┘ │ 
└─┘┴─┘┴└─┘┴ ┴  ┴ ┴┘└┘  ┴ ┴┴└─┴└─└─┘└┴┘  ┴ ┴└─┘ ┴    ┴ └─┘  └─┘ ┴ ┴ ┴┴└─ ┴ 
""".strip('\n')
    additional_art_lines = additional_art.splitlines()
    top_padding = (rows - len(additional_art_lines)) // 2
    print("\n" * top_padding, end='')
    for line in additional_art_lines:
        print(line.center(columns))
    block_for_seconds(3)
    os.system('cls' if os.name == 'nt' else 'clear')

def print_labyrinth():
    columns, rows = shutil.get_terminal_size()
    os.system('cls' if os.name == 'nt' else 'clear')
    header = " TermiMaze (v1.0) ".center(columns, "=")
    footer = " ↑ ↓ → ← contorls, q for quit ".center(columns, "=")

    print(header)
    for row in maze:
        print(row.center(columns), end='')
    print()
    print()
    print(footer)

def move_player(direction):
    global navigator_position
    x, y = navigator_position
    if direction == 'up' and maze[x-1][y] != '#':
        if maze[x-1][y] == 'E':
            win()
        navigator_position[0] -= 1
    elif direction == 'down' and maze[x+1][y] != '#':
        if maze[x+1][y] == 'E':
            win()
        navigator_position[0] += 1
    elif direction == 'left' and maze[x][y-1] != '#':
        if maze[x][y-1] == 'E':
            win()
        navigator_position[1] -= 1
    elif direction == 'right' and maze[x][y+1] != '#':
        if maze[x][y+1] == 'E':
            win()
        navigator_position[1] += 1

def update_labyrinth():
    global maze
    updated_maze = []
    for i, row in enumerate(maze):
        new_row = ""
        for j, char in enumerate(row):
            if [i, j] == navigator_position:
                new_row += '@'
            elif char == '@':
                new_row += ' '
            else:
                new_row += char
        updated_maze.append(new_row)
    maze[:] = updated_maze

def main():
    display_loading_screen()
    curses.wrapper(game_loop)
    print_labyrinth()
    os.system('cls' if os.name == 'nt' else 'clear')

def game_loop(stdscr):
    stdscr.nodelay(False) 
    while True:
        key = stdscr.getch()
        if key == curses.KEY_UP:
            move_player('up')
        elif key == curses.KEY_DOWN:
            move_player('down')
        elif key == curses.KEY_LEFT:
            move_player('left')
        elif key == curses.KEY_RIGHT:
            move_player('right')
        elif key == ord('q'):
            os.system('cls' if os.name == 'nt' else 'clear')
            break
        update_labyrinth()
        print_labyrinth()

def win():
    curses.endwin()
    os.system('cls' if os.name == 'nt' else 'clear')
    winner_art = """
██╗    ██╗██╗███╗   ██╗███╗   ██╗███████╗██████╗ 
██║    ██║██║████╗  ██║████╗  ██║██╔════╝██╔══██╗
██║ █╗ ██║██║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝
██║███╗██║██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗
╚███╔███╔╝██║██║ ╚████║██║ ╚████║███████╗██║  ██║
 ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
""".strip('\n')
    columns, rows = shutil.get_terminal_size()
    art_lines = winner_art.splitlines()
    top_padding = (rows - len(art_lines)) // 2
    print("\n" * top_padding, end='')
    for line in art_lines:
        print(line.center(columns))
    block_for_seconds(3)
    os.system('cls' if os.name == 'nt' else 'clear')
    exit()

if __name__ == "__main__":
    main()