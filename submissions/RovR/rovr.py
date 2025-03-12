import curses
import os
import sys

dotFiles = False

def main(stdscr):
  curses.start_color()
  curses.use_default_colors()
  curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
  curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
  curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)
  curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)

  curses.curs_set(0)
  
  #variables:
  c_dir = os.getcwd()
  f_list = filterList(sorted(os.listdir(c_dir)), c_dir)
  f_index = 0
  history = []
  height, width = stdscr.getmaxyx()
  max_visible_items = height - 6
  scroll_offset = max(0, f_index - max_visible_items + 1)
  search_query = ""

  while True:
    stdscr.clear()

    if f_index < scroll_offset:
      scroll_offset = f_index
    elif f_index >= scroll_offset + max_visible_items:
      scroll_offset = f_index - max_visible_items + 1


    if search_query:
      f_list = searchResults(search_query, f_list)
    else:
      f_list = filterList(sorted(os.listdir(c_dir)), c_dir);

    if not f_list:
      f_list = ["(No Results Found)"]
      f_index = 0

    stdscr.addstr(height - 3, 2, f"🔍: {search_query}".ljust(width - 6), curses.color_pair(4))

    stdscr.border(0)
    stdscr.addstr(0, 2, " RovR 🛰 ", curses.A_BOLD)

    stdscr.addstr(1, 2, f"💾{c_dir}", curses.A_BOLD)

    for i, item in enumerate(f_list[scroll_offset:scroll_offset + max_visible_items]):
      full_path = os.path.join(c_dir, item)
      is_dir = os.path.isdir(full_path)

      actual_index = i + scroll_offset

      color = curses.color_pair(1) if is_dir else curses.color_pair(2)

      display_text = f"{' 📁' if is_dir else ' 📄'}{item}"
      padded_text = ">"+display_text.ljust(width - 6)

      if actual_index == f_index:
          stdscr.attron(curses.color_pair(3))
          stdscr.attron(curses.A_BOLD)
          stdscr.addstr(i + 3, 2, padded_text)
          stdscr.attroff(curses.color_pair(3))
          stdscr.attron(curses.A_BOLD)
      else:
          stdscr.addstr(i + 3, 2, display_text, color)

    key = stdscr.getch()

    if key == curses.KEY_UP and f_index > 0:
      f_index -= 1 
    elif key == curses.KEY_DOWN and f_index < len(f_list) - 1:
      f_index += 1  
    elif key == 27:
      if search_query:
        search_query = ""
      else:
        break
    elif key in (curses.KEY_BACKSPACE, 127):
      search_query = search_query[:-1]
      f_index = 0

    #TODO: ADD DOT FILES TOGGLE
    # elif key == 46:  # ASCII code for "."
    #   next_key = stdscr.getch()  # Get the next key press
    #   if next_key == 27:
    #       global dotFiles
    #       dotFiles = not dotFiles
    #       f_list = filterList(sorted(os.listdir(c_dir)), c_dir)
    #       f_index = 0

    elif 32 <= key <= 126:
      search_query += chr(key)
      f_index = 0

    elif key == curses.KEY_RIGHT:
      selected_item = f_list[f_index]
      new_path = os.path.join(c_dir, selected_item)
      if(os.path.isdir(new_path)):
        try:
          history.append(c_dir)
          c_dir = new_path
          f_list = filterList(sorted(os.listdir(c_dir)), c_dir)
          if not f_list:
            f_list = ["(Empty Folder.)"]
          f_index = 0
        except PermissionError:
            stdscr.addstr(len(f_list) + 4, 2, "🚫 Access Denied", curses.color_pair(1))
      search_query = ""

    elif key == curses.KEY_LEFT:
      parent_dir = os.path.dirname(c_dir)
      dir_name = os.path.basename(c_dir)
      if parent_dir != c_dir:  # Prevent infinite loop at root
          c_dir = parent_dir
      c_dir = parent_dir
      f_list = filterList(sorted(os.listdir(c_dir)), c_dir)
      f_index = f_list.index(dir_name) if dir_name in f_list else 0
      history.append(dir_name)
      search_query = ""
    elif key in (curses.KEY_ENTER, 10): 
      selected_item = f_list[f_index]
      new_path = os.path.join(c_dir, selected_item)

      if os.path.isdir(new_path):  
          curses.endwin()
          print(f'Path: "{new_path}"')  
          sys.exit(0)
    stdscr.refresh()

def filterList(arr, c):
  if arr:
    if not dotFiles:
      return sort_folders_first(list(filter(lambda item: not item.startswith("."), arr)), c)
    else:
      return sort_folders_first(arr, c)

def sort_folders_first(file_list, current_path):
    return sorted(file_list, key=lambda item: (not os.path.isdir(os.path.join(current_path, item)), item.lower()))

def searchResults(searchQ, file_list):
    if not searchQ:
        return file_list

    return [item for item in file_list if searchQ.lower() in item.lower()]

curses.wrapper(main)