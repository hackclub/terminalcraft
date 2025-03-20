import json
import difflib

from cursesshortcuts import draw_borders, draw_box_borders

from search_items import search_matrix

with open('json/skinlist.json', 'r') as f:
    skins_list = json.loads(f.read())

letters = list('abcdefghijklmnopqrstuvwxyz')

letters_upper = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def search_item(screen, curses, current_value, selection, matrix, vectorizer):
    current_text = current_value
    start_locations = [3, 27, 51, 74, 98]
    start_heights = [6, 16]
    if selection > 5:
        column = selection-5
        row = 2
    else:
        column = selection
        row = 1

    
    y = start_heights[row-1]
    x = start_locations[column-1]

    # Clear selection highlight and add search box
    if column == 3:
        screen.addstr(y, x, '                  ', curses.color_pair(1))
        screen.addstr(y+1, x-1, '├──────────────────┤')
        for j in range(4):
            screen.addstr(y+2+j, x-1, '│                  │')
        screen.addstr(y+6, x-1, '└──────────────────┘')
    else:
        screen.addstr(y, x, '                   ', curses.color_pair(1))
        screen.addstr(y+1, x-1, '├───────────────────┤')
        for j in range(4):
            screen.addstr(y+2+j, x-1, '│                   │')
        screen.addstr(y+6, x-1, '└───────────────────┘')

    
    current_search_selection = 0
    best_matches = ['', '', '', '']

    
    if len(current_value)<17:
        screen.addstr(y, x, current_text, curses.color_pair(1))
        screen.addstr(y, x+len(current_value), " ", curses.color_pair(2))
    else:
        visible_text = current_text[-16:]
        screen.addstr(y, x, "…" + visible_text,curses.color_pair(1))
        screen.addstr(y, x+17, " ", curses.color_pair(2))

    # Stupid but really useful
    spaces = '                  ' if column == 3 else '                   '

    while True:
        c = screen.getch()
        if c == 10: # Enter
            screen.clear()
            draw_box_borders(screen, curses)
            draw_borders(screen)

            if current_search_selection > 0:
                return best_matches[current_search_selection-1]
            
            if len(best_matches) > 0:
                return best_matches[0]
            else:
                return ''

        elif c == 27: # esc
            screen.clear()
            draw_box_borders(screen, curses)
            draw_borders(screen)
            return ''
        
        elif 97 <= c <= 122 and current_search_selection == 0: # Lower case letters
            current_text += letters[c-97]
            
        
        elif 65 <= c <= 90 and current_search_selection == 0: # Upper case letters
            current_text += letters_upper[c-65]

        elif 48 <= c <= 57: # Numbers
            current_text += str(c-48)

        elif c == 45: # -
            current_text += '-'
        
        elif c == 124: # |
            current_text += '|'
        
        elif c == 32: # space 
            current_text += ' '
        
        elif c == 8: # Delete key
            if len(current_text) <18:
                screen.addstr(y, x+len(current_text), " ", curses.color_pair(1)) # deletes cursor
            current_text = current_text[:-1]
            
        
        elif c == 258: # Down arrow
            screen.addstr(y, x+len(current_text), " ", curses.color_pair(1)) # Remove cursor

            if current_search_selection != 4:
                current_search_selection += 1
            else:
                current_search_selection = 0
        
        elif c == 259: # Up arrow
            screen.addstr(y, x+len(current_text), " ", curses.color_pair(1)) # Remove cursor

            if current_search_selection != 0:
                current_search_selection -= 1
            else:
                current_search_selection = 4

        # Render the text
        if current_search_selection == 0:
            if len(current_text)<17:
                screen.addstr(y, x, current_text, curses.color_pair(1))
                screen.addstr(y, x+len(current_text), " ", curses.color_pair(2))
            else:
                visible_text = current_text[-16:]
                screen.addstr(y, x, "…" + visible_text,curses.color_pair(1))
                screen.addstr(y, x+17, " ", curses.color_pair(2))

            best_matches = search_matrix(matrix, vectorizer, current_text)
            # print(best_matches)

        for count, i in enumerate(best_matches):
            color = 1 if current_search_selection != count+1 else 2
            if len(i) > 18:
                
                screen.addstr(y+2+count, x, i[:17]+"…", curses.color_pair(color))
            else:
                screen.addstr(y+2+count, x, i + ''.join(' ' for _ in range(18-len(i))), curses.color_pair(color))
        
        if len(best_matches) < 4:
            for i in range(4-len(best_matches)):
                screen.addstr(y+5-i, x, spaces)
        
def change_float(screen, curses, current_value, selection):
    current_float = str(current_value)[2:]
    start_locations = [10, 34, 58, 81, 105]
    start_heights = [8, 18]

    if selection > 5:
        column = selection-5
        row = 2
    else:
        column = selection
        row = 1

    y = start_heights[row-1]
    x = start_locations[column-1]

    screen.addstr(y, x-7, "Float: ", curses.color_pair(1))

    screen.addstr(y,x, f"0.{current_float}", curses.color_pair(1))
    screen.addstr(y,x+2+len(current_float), " ", curses.color_pair(2))

    while True:
        c = screen.getch()
        
        if c == 10: # enter
            screen.addstr(y, x+len(current_float)+2, " ", curses.color_pair(1)) # deletes cursor
            return float("0." + current_float)

        elif c == 8: # Delete key
            screen.addstr(y, x+len(current_float)+2, " ", curses.color_pair(1)) # deletes cursor
            current_float = current_float[:-1]

        elif 48 <= c <= 57: # Numbers
            if len(current_float) <= 8:
                current_float += str(c-48)
        
        elif c == 27: # esc
            screen.addstr(y, x+len(current_float)+2, " ", curses.color_pair(1)) # deletes cursor
            return current_value
        
        screen.addstr(y,x, f"0.{current_float}", curses.color_pair(1))
        screen.addstr(y,x+2+len(current_float), " ", curses.color_pair(2))
        




