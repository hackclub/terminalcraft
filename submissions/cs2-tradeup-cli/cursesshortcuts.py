from cs2_functions import calculate_exterior

def draw_borders(screen):
    """A simple function that draws a border around the app"""
    # Horizontal borders
    screen.addstr(0, 0, ''.join('─' for _ in range(120)))
    screen.addstr(34, 0, ''.join('─' for _ in range(120)))

    # Vertical borders
    for i in range(33):
        screen.addstr(1+i, 0, '│')
        screen.addstr(1+i, 119, '│')

    # Corners
    screen.addstr(0, 0, '┌')
    screen.addstr(34, 0, '└')
    screen.addstr(0, 119, '┐')
    screen.addstr(34, 119, '┘')
    
def draw_box_borders(screen, curses):
    # Draws borders around each of the boxes
    screen.addstr(6, 2, '│')
    screen.addstr(6, 22, '│')
    screen.addstr(6, 26, '│')
    screen.addstr(6, 46, '│')
    screen.addstr(6, 50, '│')
    screen.addstr(6, 69, '│')
    screen.addstr(6, 73, '│')
    screen.addstr(6, 93, '│')
    screen.addstr(6, 97, '│')
    screen.addstr(6, 117, '│')
    
    screen.addstr(7, 2, '└')
    screen.addstr(7, 22, '┘')
    screen.addstr(7, 26, '└')
    screen.addstr(7, 46, '┘')
    screen.addstr(7, 50, '└')
    screen.addstr(7, 69, '┘')
    screen.addstr(7, 73, '└')
    screen.addstr(7, 93, '┘')
    screen.addstr(7, 97, '└')
    screen.addstr(7, 117, '┘')

    screen.addstr(5, 2, '┌')
    screen.addstr(5, 22, '┐')
    screen.addstr(5, 26, '┌')
    screen.addstr(5, 46, '┐')
    screen.addstr(5, 50, '┌')
    screen.addstr(5, 69, '┐')
    screen.addstr(5, 73, '┌')
    screen.addstr(5, 93, '┐')
    screen.addstr(5, 97, '┌')
    screen.addstr(5, 117, '┐')

    screen.addstr(5, 3, ''.join('─' for _ in range(19)))
    screen.addstr(5, 27, ''.join('─' for _ in range(19)))
    screen.addstr(5, 51, ''.join('─' for _ in range(18)))
    screen.addstr(5, 74, ''.join('─' for _ in range(19)))
    screen.addstr(5, 98, ''.join('─' for _ in range(19)))

    screen.addstr(7, 3, ''.join('─' for _ in range(19)))
    screen.addstr(7, 27, ''.join('─' for _ in range(19)))
    screen.addstr(7, 51, ''.join('─' for _ in range(18)))
    screen.addstr(7, 74, ''.join('─' for _ in range(19)))
    screen.addstr(7, 98, ''.join('─' for _ in range(19)))


    diff = 10
    screen.addstr(6+diff, 2, '│')
    screen.addstr(6+diff, 22, '│')
    screen.addstr(6+diff, 26, '│')
    screen.addstr(6+diff, 46, '│')
    screen.addstr(6+diff, 50, '│')
    screen.addstr(6+diff, 69, '│')
    screen.addstr(6+diff, 73, '│')
    screen.addstr(6+diff, 93, '│')
    screen.addstr(6+diff, 97, '│')
    screen.addstr(6+diff, 117, '│')
    
    screen.addstr(7+diff, 2, '└')
    screen.addstr(7+diff, 22, '┘')
    screen.addstr(7+diff, 26, '└')
    screen.addstr(7+diff, 46, '┘')
    screen.addstr(7+diff, 50, '└')
    screen.addstr(7+diff, 69, '┘')
    screen.addstr(7+diff, 73, '└')
    screen.addstr(7+diff, 93, '┘')
    screen.addstr(7+diff, 97, '└')
    screen.addstr(7+diff, 117, '┘')

    screen.addstr(5+diff, 2, '┌')
    screen.addstr(5+diff, 22, '┐')
    screen.addstr(5+diff, 26, '┌')
    screen.addstr(5+diff, 46, '┐')
    screen.addstr(5+diff, 50, '┌')
    screen.addstr(5+diff, 69, '┐')
    screen.addstr(5+diff, 73, '┌')
    screen.addstr(5+diff, 93, '┐')
    screen.addstr(5+diff, 97, '┌')
    screen.addstr(5+diff, 117, '┐')

    screen.addstr(5+diff, 3, ''.join('─' for _ in range(19)))
    screen.addstr(5+diff, 27, ''.join('─' for _ in range(19)))
    screen.addstr(5+diff, 51, ''.join('─' for _ in range(18)))
    screen.addstr(5+diff, 74, ''.join('─' for _ in range(19)))
    screen.addstr(5+diff, 98, ''.join('─' for _ in range(19)))

    screen.addstr(7+diff, 3, ''.join('─' for _ in range(19)))
    screen.addstr(7+diff, 27, ''.join('─' for _ in range(19)))
    screen.addstr(7+diff, 51, ''.join('─' for _ in range(18)))
    screen.addstr(7+diff, 74, ''.join('─' for _ in range(19)))
    screen.addstr(7+diff, 98, ''.join('─' for _ in range(19)))


    screen.addstr(4, 3  , "item 1:", curses.A_BOLD + curses.A_UNDERLINE)
    screen.addstr(4, 27  , "item 2:", curses.A_BOLD + curses.A_UNDERLINE)
    screen.addstr(4, 51  , "item 3:", curses.A_BOLD + curses.A_UNDERLINE)
    screen.addstr(4, 74  , "item 4:", curses.A_BOLD + curses.A_UNDERLINE)
    screen.addstr(4, 98  , "item 5:", curses.A_BOLD + curses.A_UNDERLINE)

    screen.addstr(4+diff, 3  , "item 6:", curses.A_BOLD + curses.A_UNDERLINE)
    screen.addstr(4+diff, 27  , "item 7:", curses.A_BOLD + curses.A_UNDERLINE)
    screen.addstr(4+diff, 51  , "item 8:", curses.A_BOLD + curses.A_UNDERLINE)
    screen.addstr(4+diff, 74  , "item 9:", curses.A_BOLD + curses.A_UNDERLINE)
    screen.addstr(4+diff, 98  , "item 10:", curses.A_BOLD + curses.A_UNDERLINE)

    screen.addstr(21, 3  , "Outputs:", curses.A_BOLD + curses.A_UNDERLINE)
    screen.addstr(20, 0, ''.join('─' for _ in range(120)))
    screen.addstr(20, 119, '┤')
    screen.addstr(20, 0, '├')

    



def draw_text(screen, curses, item_values: list, selection: int, floats: list, box_selection: int):
    """Draws the text for each of the boxes"""
    start_locations = [3, 27, 51, 74, 98]
    start_heights = [6, 16]
    screen.addstr(8, 1, ''.join(' ' for _ in range(118)))
    screen.addstr(18, 1, ''.join(' ' for _ in range(118)))
    for count, i in enumerate(item_values):
        if count > 5:
            column = count-5
            row = 2
        else:
            column = count
            row = 1
        
        if column == 3:
            box_width = 18
        else:
            box_width = 19

        c = 1 if selection != count or box_selection != 0 else 2
        if len(i) <= 17:
            screen.addstr(start_heights[row-1], start_locations[column-1],
                            i + ''.join(' ' for _ in range(box_width-len(i))),
                              curses.color_pair(c))
        else:
            screen.addstr(start_heights[row-1], start_locations[column-1], i[:box_width-1]+"…", curses.color_pair(c))

        c = 1 if selection != count or box_selection != 1 else 2
        screen.addstr(start_heights[row-1]+2, start_locations[column-1], f"Float: {floats[count]}", curses.color_pair(c))
        screen.addstr(start_heights[row-1]+3, start_locations[column-1], f"Exterior: {calculate_exterior(floats[count])}", curses.color_pair(1))
    
    
        

