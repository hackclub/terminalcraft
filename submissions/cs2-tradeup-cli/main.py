import json
import os
import sys

import curses

from cursesshortcuts import draw_borders, draw_box_borders, draw_text
from gen_colors import gen_colors
from text_entry import search_item, change_float
from search_items import generate_matrix
from calculate_tradeup import calculate_tradeup
# Deal with being unable to import curses on windows because it doesnt work properly by default
try:
    import curses
except ModuleNotFoundError:
    print("Could not import curses. If you are running on windows please install the 'windows-curses' module")
    sys.exit(1)

# This wont work from an ide shell so deal with that
try:
    screen = curses.initscr()
except ModuleNotFoundError:
    print("could not create screen. This is most likely because you are"
          "running from an IDE shell and not a terminal. Please run this"
          "program from a terminal")
    sys.exit(1)

# Min terminal height needed to run this program without issues
term_height = os.get_terminal_size().lines
term_width = os.get_terminal_size().columns
if term_height < 35 or term_width < 121:
    print(f"Terminal size must be at least 121x35 (currently {term_width}x{term_height})")
    quit()

# Curses colour stuff
curses.start_color()
gen_colors(curses)
curses.init_pair(1, 1, 0) # default text
curses.init_pair(2, 0, 1) # Inverted from default
curses.init_pair(3, 4, 0) # Red FG


# Curses config
curses.curs_set(False)
screen.keypad(True)
curses.noecho()

# Initial setup
draw_borders(screen)
draw_box_borders(screen, curses)
matrix, vectorizer = generate_matrix() 

current_selection = 1
box_selection = 0

selected_items = ['PLACEHOLDER', '', '', '', '', '', '', '', '', '', '']
float_values = [-1, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035]
# main loop
while True:
    draw_text(screen, curses, selected_items, current_selection, float_values, box_selection)
    key = screen.getch()
    # screen.addstr(35, 2, str(key) + "####")

    match key:
        case 9: # tab
            current_selection = current_selection+1 if current_selection != 10 else 1
            box_selection = 0
            # draw_text(screen, curses, selected_items, current_selection, float_values)
        case 351: # shift+tab
            current_selection = current_selection-1 if current_selection != 1 else 10
            box_selection = 0
        
        case 10:
            if box_selection == 0:
                selected_items[current_selection] = search_item(screen, curses, selected_items[current_selection], current_selection, matrix, vectorizer)
            elif box_selection == 1:
                float_values[current_selection] = change_float(screen, curses, float_values[current_selection], current_selection)
        
        case 258: # Arrow down
            if 1 <= current_selection <= 10:
                box_selection = 1 if box_selection == 0 else 0
                
        case 259: # Arrow down
            if 1 <= current_selection <= 10:
                box_selection = 1 if box_selection == 0 else 0
        
    
    success, result = calculate_tradeup(selected_items[1:], float_values[1:])
    screen.addstr(22, 2, '                                                     ')
    if not success:
        if result == 'covert':
            screen.addstr(22, 2, 'Covert items can not be used in trade ups', curses.color_pair(3))
        if result == 'missing':
            screen.addstr(22, 2, 'Please select items to trade up', curses.color_pair(3))
        if result == 'rarity':
            screen.addstr(22, 2, 'All items must be of same rarity for trade up', curses.color_pair(3))
    
    else:
        # Border stuff
        for i in range(12):
            screen.addstr(22+i, 39, '│')
            screen.addstr(22+i, 77, '│')
        row_inc = 0
        column_inc = 0

        for i in result[:36]:
            s = f'{i[1]}%: ({i[2]}) {i[0]}'
            if len(i[0]) > 25:
                s = f'{i[1]}%: ({i[2]}) {i[0][:24]}…'
            screen.addstr(22+row_inc, 2+column_inc*38, s)
            if column_inc != 2:
                column_inc += 1
            else:
                column_inc = 0
                row_inc += 1
        # case
    
    # screen.addstr(1, 0, "asd", 2)



