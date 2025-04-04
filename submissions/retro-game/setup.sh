#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

echo "==== Setting up SSH Multi-Game Platform ===="

# Create and ensure games user exists
if ! id games &>/dev/null; then
  echo "Creating games user..."
  useradd -m -s /bin/bash games
  echo "games:games" | chpasswd
else
  echo "User games already exists"
fi

# Setup directory structure
BASE_DIR="/home/games"
GAMES_DIR="$BASE_DIR/games"

# Clean start - remove any existing files
echo "Removing any existing files..."
rm -rf "$BASE_DIR/games" "$BASE_DIR/main_menu.sh" "$BASE_DIR/ssh_wrapper.sh"

# Create directory structure
echo "Creating directory structure..."
mkdir -p "$GAMES_DIR/snake"
mkdir -p "$GAMES_DIR/minesweeper"

# Install Python 
echo "Installing Python..."
yum -y install python3

# Create SSH wrapper script (entry point)
echo "Creating SSH wrapper script..."
cat > "$BASE_DIR/ssh_wrapper.sh" << 'EOL'
#!/bin/bash

# Display welcome header
clear
cat << "EOF"
==============================================
  __  __ _       _    ____                          
 |  \/  (_)_ __ (_)  / ___| __ _ _ __ ___   ___  ___ 
 | |\/| | | '_ \| | | |  _ / _` | '_ ` _ \ / _ \/ __|
 | |  | | | | | | | | |_| | (_| | | | | | |  __/\__ \
 |_|  |_|_|_| |_|_|  \____|\__,_|_| |_| |_|\___||___/
                                               
==============================================
   Welcome to ssh.karthik.lol Mini Games!     
==============================================

EOF

echo "Loading game menu..."
sleep 1

# Launch the main menu
exec bash /home/games/main_menu.sh
EOL

# Create the main menu script with phone UI
echo "Creating main menu script..."
cat > "$BASE_DIR/main_menu.sh" << 'EOL'
#!/bin/bash

# Set explicit paths
GAMES_DIR="/home/games/games"
BASE_DIR="/home/games"

# Function to draw the flip phone UI
draw_phone() {
  clear
  local selected=$1
  
  echo "  ┌─────────────────────┐  "
  echo "  │                     │  "
  echo "  │   ┌─────────────┐   │  "
  echo "  │   │             │   │  "
  echo "  │   │  GAME MENU  │   │  "
  echo "  │   │             │   │  "
  
  if [ $selected -eq 0 ]; then
    echo "  │   │ ▶ Snake      │   │  "
  else
    echo "  │   │   Snake      │   │  "
  fi
  
  if [ $selected -eq 1 ]; then
    echo "  │   │ ▶ Minesweeper│   │  "
  else
    echo "  │   │   Minesweeper│   │  "
  fi
  
  if [ $selected -eq 2 ]; then
    echo "  │   │ ▶ Exit       │   │  "
  else
    echo "  │   │   Exit       │   │  "
  fi
  
  echo "  │   │             │   │  "
  echo "  │   └─────────────┘   │  "
  echo "  │                     │  "
  echo "  │    ┌───┐ ┌───┐     │  "
  echo "  │    │ ↑ │ │sel│     │  "
  echo "  │    └───┘ └───┘     │  "
  echo "  │ ┌───┐ ┌───┐ ┌───┐  │  "
  echo "  │ │ ← │ │ ↓ │ │ → │  │  "
  echo "  │ └───┘ └───┘ └───┘  │  "
  echo "  │                     │  "
  echo "  └─────────────────────┘  "
  echo ""
  echo "  Use UP/DOWN to navigate  "
  echo "  Press ENTER to select    "
}

# Initialize selection
selected=0
total_options=3

# Get key press function
get_keypress() {
  # Read a single keystroke without displaying it
  IFS= read -r -s -n1 key

  # Check for escape sequence (arrow keys)
  if [[ $key == $'\e' ]]; then
    read -r -s -n2 -t 0.1 arrow
    if [[ $arrow == '[A' ]]; then
      echo "UP"
    elif [[ $arrow == '[B' ]]; then
      echo "DOWN"
    elif [[ $arrow == '[C' ]]; then
      echo "RIGHT"
    elif [[ $arrow == '[D' ]]; then
      echo "LEFT"
    fi
  elif [[ $key == "" ]]; then
    echo "ENTER"
  else
    echo "OTHER"
  fi
}

# Main menu loop
while true; do
  draw_phone $selected
  
  keypress=$(get_keypress)
  
  case $keypress in
    UP)
      # Move selection up
      if [ $selected -gt 0 ]; then
        selected=$((selected - 1))
      fi
      ;;
    DOWN)
      # Move selection down
      if [ $selected -lt $((total_options - 1)) ]; then
        selected=$((selected + 1))
      fi
      ;;
    ENTER)
      # Execute selected option
      case $selected in
        0)
          clear
          echo "Loading Snake Game..."
          sleep 1
          exec bash "$GAMES_DIR/snake/welcome.sh"
          ;;
        1)
          clear
          echo "Loading Minesweeper Game..."
          sleep 1
          exec bash "$GAMES_DIR/minesweeper/welcome.sh"
          ;;
        2)
          clear
          echo "Thanks for playing!"
          echo "Disconnecting in 3 seconds..."
          sleep 3
          exit 0
          ;;
      esac
      ;;
  esac
done
EOL

# Create Snake welcome script
echo "Creating snake welcome script..."
cat > "$GAMES_DIR/snake/welcome.sh" << 'EOL'
#!/bin/bash

# Set explicit paths
GAMES_DIR="/home/games/games"
BASE_DIR="/home/games"

clear
cat << "EOF"
==============================================
  _________             __            
 /   _____/ ____ _____  |  | __ ____  
 \_____  \ /    \\__  \ |  |/ // __ \ 
 /        \   |  \/ __ \|    <\  ___/ 
/_______  /___|  (____  /__|_ \\___  >
        \/     \/     \/     \/    \/ 
             
==============================================
   Welcome to the Classic Snake Game!    
==============================================

- Use ARROW KEYS to control the snake
- Eat regular food (*) to gain 10 points
- Collect special food ($) for 50 bonus points!
- Press 'p' to pause, 'q' to quit

EOF

echo "Press ENTER to begin..."
read

# Run the game
cd "$GAMES_DIR/snake"
/usr/bin/python3 "$GAMES_DIR/snake/snake.py"
GAME_EXIT=$?

echo ""
echo "Returning to main menu in 3 seconds..."
sleep 3
exec bash "$BASE_DIR/main_menu.sh"
EOL

echo "Creating snake game..."
cat > "$GAMES_DIR/snake/snake.py" << 'EOL'
#!/usr/bin/env python3

import curses
import random


def main(stdscr):
    curses.curs_set(0)
    stdscr.timeout(150)
    stdscr.keypad(True)

    try:
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        use_colors = True
    except:
        use_colors = False

    max_y, max_x = stdscr.getmaxyx()

    height = max_y - 4
    width = max_x - 4

    game_win = curses.newwin(height + 2, width + 2, 1, 1)
    game_win.keypad(True)
    game_win.timeout(150)

    stdscr.clear()
    welcome_msg = "SNAKE GAME - Press any key to start"
    stdscr.addstr(max_y // 2, (max_x - len(welcome_msg)) // 2, welcome_msg)
    stdscr.refresh()
    stdscr.getch()

    snake = [
        [height // 2, width // 2],
        [height // 2, width // 2 - 1],
        [height // 2, width // 2 - 2],
    ]

    food = [height // 2, width // 2 + 5]

    special_food = None
    special_food_timer = 0

    direction = curses.KEY_RIGHT

    score = 0

    while True:
        game_win.clear()
        game_win.box()

        stdscr.addstr(
            0, 2, f"Score: {score}   ", curses.color_pair(4) if use_colors else 0
        )
        stdscr.refresh()

        for i, segment in enumerate(snake):
            y, x = segment
            if i == 0:
                game_win.addstr(y, x, "O", curses.color_pair(1) if use_colors else 0)
            else:
                game_win.addstr(y, x, "o", curses.color_pair(1) if use_colors else 0)

        if food:
            game_win.addstr(
                food[0], food[1], "*", curses.color_pair(2) if use_colors else 0
            )

        if special_food:
            game_win.addstr(
                special_food[0],
                special_food[1],
                "$",
                curses.color_pair(5) if use_colors else 0,
            )

        game_win.refresh()

        key = stdscr.getch()

        if key == ord("q"):
            break

        if key == ord("p"):
            game_win.addstr(
                height // 2,
                width // 2 - 10,
                "PAUSED - Press 'p' to resume",
                curses.color_pair(4) if use_colors else 0,
            )
            game_win.refresh()

            stdscr.timeout(-1)
            while True:
                ch = stdscr.getch()
                if ch == ord("p"):
                    break
                elif ch == ord("q"):
                    return

            stdscr.timeout(150)

        if key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
            if (
                (direction == curses.KEY_DOWN and key != curses.KEY_UP)
                or (direction == curses.KEY_UP and key != curses.KEY_DOWN)
                or (direction == curses.KEY_LEFT and key != curses.KEY_RIGHT)
                or (direction == curses.KEY_RIGHT and key != curses.KEY_LEFT)
            ):
                direction = key

        head = snake[0].copy()
        if direction == curses.KEY_DOWN:
            head[0] += 1
        elif direction == curses.KEY_UP:
            head[0] -= 1
        elif direction == curses.KEY_LEFT:
            head[1] -= 1
        elif direction == curses.KEY_RIGHT:
            head[1] += 1

        if (
            head[0] <= 0
            or head[0] >= height + 1
            or head[1] <= 0
            or head[1] >= width + 1
        ):
            break

        if head in snake:
            break

        snake.insert(0, head)

        if head == food:
            score += 10

            for _ in range(100):
                food = [random.randint(1, height), random.randint(1, width)]
                if food not in snake and (not special_food or food != special_food):
                    break

            if special_food is None and random.random() < 0.1:
                for _ in range(100):
                    special_food = [random.randint(1, height), random.randint(1, width)]
                    if special_food not in snake and special_food != food:
                        break
                special_food_timer = 50

        elif special_food and head == special_food:
            score += 50

            special_food = None
            special_food_timer = 0
        else:
            snake.pop()

        if special_food:
            special_food_timer -= 1
            if special_food_timer <= 0:
                special_food = None

    stdscr.clear()
    game_over_msg = f"Game Over! Final Score: {score}"
    stdscr.addstr(
        max_y // 2,
        (max_x - len(game_over_msg)) // 2,
        game_over_msg,
        curses.color_pair(2) if use_colors else 0,
    )
    stdscr.addstr(max_y // 2 + 2, (max_x - 22) // 2, "Press any key to exit")
    stdscr.refresh()
    stdscr.timeout(-1)
    stdscr.getch()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"An error occurred: {e}")
EOL


echo "Creating minesweeper welcome script..."
cat > "$GAMES_DIR/minesweeper/welcome.sh" << 'EOL'
#!/bin/bash

# Set explicit paths
GAMES_DIR="/home/games/games"
BASE_DIR="/home/games"

clear
cat << "EOF"
==============================================
 __  __ _                                                
|  \/  (_)_ __   ___  _____      _____  ___ _ __   ___ _ __ 
| |\/| | | '_ \ / _ \/ __\ \ /\ / / _ \/ _ \ '_ \ / _ \ '__|
| |  | | | | | |  __/\__ \\ V  V /  __/  __/ |_) |  __/ |   
|_|  |_|_|_| |_|\___||___/ \_/\_/ \___|\___| .__/ \___|_|   
                                           |_|              
==============================================
       Welcome to the Minesweeper Game!       
==============================================

- Use ARROW KEYS to move the cursor
- Press SPACE to reveal a cell
- Press 'f' to flag a suspected mine
- Press 'p' to pause, 'q' to quit
- Reveal all non-mine cells to win!

EOF

echo "Press ENTER to begin..."
read

# Run the game
cd "$GAMES_DIR/minesweeper"
/usr/bin/python3 "$GAMES_DIR/minesweeper/minesweeper.py"
GAME_EXIT=$?

echo ""
echo "Returning to main menu in 3 seconds..."
sleep 3
exec bash "$BASE_DIR/main_menu.sh"
EOL

echo "Creating minesweeper game..."
cat > "$GAMES_DIR/minesweeper/minesweeper.py" << 'EOL'
#!/usr/bin/env python3

import curses
import random
import time

def main(stdscr):
    # Initialize curses
    curses.curs_set(0)
    stdscr.timeout(100)
    stdscr.keypad(True)
    
    # Setup colors
    try:
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Default
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)   # 1
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # 2
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)    # 3
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)# 4
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK) # 5
        curses.init_pair(7, curses.COLOR_CYAN, curses.COLOR_BLACK)   # 6
        curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLACK)  # 7
        curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_BLACK)  # 8
        curses.init_pair(10, curses.COLOR_RED, curses.COLOR_BLACK)   # Mine
        curses.init_pair(11, curses.COLOR_YELLOW, curses.COLOR_BLACK)# Flag
        curses.init_pair(12, curses.COLOR_BLACK, curses.COLOR_WHITE) # Cursor
        use_colors = True
    except:
        use_colors = False
    
    # Get screen dimensions
    max_y, max_x = stdscr.getmaxyx()
    
    # Game dimensions (make sure it fits the screen)
    rows = min(16, max_y - 6)
    cols = min(30, max_x - 6)
    mines = int((rows * cols) * 0.15)  # ~15% of cells are mines
    
    # Set up game window
    game_win = curses.newwin(rows + 2, cols * 2 + 2, 2, (max_x - (cols * 2 + 2)) // 2)
    game_win.keypad(True)
    
    # Display welcome message
    stdscr.clear()
    welcome_msg = "MINESWEEPER - Press any key to start"
    stdscr.addstr(max_y // 2, (max_x - len(welcome_msg)) // 2, welcome_msg)
    stdscr.refresh()
    stdscr.getch()
    
    # Initialize board
    def init_board():
        # Initialize blank board
        board = [["?" for _ in range(cols)] for _ in range(rows)]
        mines_pos = []
        
        # Place mines randomly
        mine_count = 0
        while mine_count < mines:
            r, c = random.randint(0, rows - 1), random.randint(0, cols - 1)
            if (r, c) not in mines_pos:
                mines_pos.append((r, c))
                mine_count += 1
        
        return board, mines_pos
    
    # Calculate number of adjacent mines
    def count_adjacent_mines(row, col, mines_pos):
        count = 0
        for r in range(max(0, row - 1), min(rows, row + 2)):
            for c in range(max(0, col - 1), min(cols, col + 2)):
                if (r, c) in mines_pos and (r, c) != (row, col):
                    count += 1
        return count
    
    # Reveal cells recursively for empty spaces
    def reveal_cells(board, row, col, mines_pos, revealed):
        if (row, col) in revealed:
            return
        
        revealed.add((row, col))
        
        if (row, col) in mines_pos:
            return  # Hit a mine!
        
        adjacent = count_adjacent_mines(row, col, mines_pos)
        if adjacent == 0:
            board[row][col] = " "
            # Reveal adjacent cells for empty space
            for r in range(max(0, row - 1), min(rows, row + 2)):
                for c in range(max(0, col - 1), min(cols, col + 2)):
                    if (r, c) != (row, col):
                        reveal_cells(board, r, c, mines_pos, revealed)
        else:
            board[row][col] = str(adjacent)
    
    # Game loop
    game_over = False
    win = False
    start_time = time.time()
    
    while True:
        # Initialize or reset the game
        board, mines_pos = init_board()
        flags = set()
        revealed = set()
        cursor_row, cursor_col = 0, 0
        game_over = False
        win = False
        start_time = time.time()
        
        # Game play loop
        while not game_over and not win:
            # Display board
            game_win.clear()
            game_win.box()
            
            # Display time and mines
            elapsed = int(time.time() - start_time)
            mines_left = mines - len(flags)
            info_msg = f"Time: {elapsed}s | Mines: {mines_left}"
            stdscr.addstr(0, (max_x - len(info_msg)) // 2, info_msg)
            stdscr.refresh()
            
            # Draw board
            for r in range(rows):
                for c in range(cols):
                    cell_char = board[r][c]
                    attr = curses.color_pair(1)
                    
                    # Apply colors based on cell content
                    if cell_char.isdigit():
                        attr = curses.color_pair(int(cell_char) + 1)
                    elif cell_char == "F":
                        attr = curses.color_pair(11)
                        cell_char = "F"
                    elif cell_char == "X":
                        attr = curses.color_pair(10)
                    
                    # Highlight cursor position
                    if r == cursor_row and c == cursor_col:
                        if use_colors:
                            attr = curses.color_pair(12)
                        else:
                            attr = curses.A_REVERSE
                    
                    game_win.addstr(r + 1, c * 2 + 1, cell_char + " ", attr if use_colors else 0)
            
            game_win.refresh()
            
            # Get user input
            key = stdscr.getch()
            
            if key == ord('q'):
                return  # Quit the game
            
            if key == ord('p'):
                # Pause the game
                game_win.addstr(rows // 2, cols - 10, "PAUSED - Press 'p' to resume")
                game_win.refresh()
                
                stdscr.timeout(-1)
                while True:
                    ch = stdscr.getch()
                    if ch == ord('p'):
                        break
                    elif ch == ord('q'):
                        return
                
                stdscr.timeout(100)
                continue
            
            if game_over or win:
                if key == ord('r'):
                    break  # Reset the game
                elif key == ord('q'):
                    return  # Quit the game
                continue
            
            # Move cursor
            if key == curses.KEY_UP and cursor_row > 0:
                cursor_row -= 1
            elif key == curses.KEY_DOWN and cursor_row < rows - 1:
                cursor_row += 1
            elif key == curses.KEY_LEFT and cursor_col > 0:
                cursor_col -= 1
            elif key == curses.KEY_RIGHT and cursor_col < cols - 1:
                cursor_col += 1
            elif key == ord('f') or key == curses.KEY_DC:  # Flag cell
                if (cursor_row, cursor_col) not in revealed:
                    if (cursor_row, cursor_col) in flags:
                        flags.remove((cursor_row, cursor_col))
                        board[cursor_row][cursor_col] = "?"
                    else:
                        flags.add((cursor_row, cursor_col))
                        board[cursor_row][cursor_col] = "F"
            elif key == ord(' ') or key == 10:  # Reveal cell (space or enter)
                if (cursor_row, cursor_col) not in flags:
                    if (cursor_row, cursor_col) in mines_pos:
                        # Game over - hit a mine
                        game_over = True
                        
                        # Show all mines
                        for r, c in mines_pos:
                            if (r, c) not in flags:
                                board[r][c] = "X"
                            
                        # Mark incorrectly flagged cells
                        for r, c in flags:
                            if (r, c) not in mines_pos:
                                board[r][c] = "!"
                    else:
                        reveal_cells(board, cursor_row, cursor_col, mines_pos, revealed)
            
            # Check win condition - all non-mine cells are revealed
            if len(revealed) == (rows * cols) - len(mines_pos):
                win = True
                
                # Flag all mines
                for r, c in mines_pos:
                    if (r, c) not in flags:
                        board[r][c] = "F"
            
            # Display game over message
            if game_over:
                msg = "GAME OVER! You hit a mine!"
                stdscr.addstr(max_y - 2, (max_x - len(msg)) // 2, msg, 
                             curses.color_pair(4) if use_colors else 0)
                stdscr.addstr(max_y - 1, (max_x - 20) // 2, "Press 'r' to restart")
                stdscr.refresh()
            
            # Display win message
            if win:
                elapsed = int(time.time() - start_time)
                msg = f"YOU WIN! Time: {elapsed}s"
                stdscr.addstr(max_y - 2, (max_x - len(msg)) // 2, msg, 
                             curses.color_pair(3) if use_colors else 0)
                stdscr.addstr(max_y - 1, (max_x - 20) // 2, "Press 'r' to restart")
                stdscr.refresh()
        
        # Wait for user decision after game ends
        stdscr.timeout(-1)
        while True:
            key = stdscr.getch()
            if key == ord('r'):
                stdscr.timeout(100)
                break  # Reset the game
            elif key == ord('q'):
                return  # Quit the game

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"An error occurred: {e}")
        # If curses fails, use the simple version
        try:
            import os
            os.system('clear')
            print("Curses initialization failed. Falling back to simple version.")
            print("Press Enter to continue...")
            input()
            import sys
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from simple_minesweeper import main as simple_main
            simple_main()
        except Exception as e2:
            print(f"Simple version also failed: {e2}")
EOL

# Create simplified minesweeper version
echo "Creating simplified minesweeper game..."
cat > "$GAMES_DIR/minesweeper/simple_minesweeper.py" << 'EOL'
#!/usr/bin/env python3
# Simple text-based minesweeper without curses

import os
import random
import sys
import termios
import tty
import select

# Game settings
ROWS = 10
COLS = 10
MINES = 10

# Game state
board = [['?' for _ in range(COLS)] for _ in range(ROWS)]
mines = []
revealed = set()
flagged = set()
cursor = [0, 0]
game_over = False
win = False

# Non-blocking keyboard input
def get_key():
    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        return sys.stdin.read(1)
    return None

# Setup terminal for single character input
def setup_terminal():
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        return old_settings
    except:
        return old_settings

# Restore terminal settings
def restore_terminal(old_settings):
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

# Place mines randomly
def place_mines():
    global mines
    mines = []
    while len(mines) < MINES:
        r = random.randint(0, ROWS-1)
        c = random.randint(0, COLS-1)
        if (r, c) not in mines:
            mines.append((r, c))

# Count adjacent mines
def count_adjacent_mines(row, col):
    count = 0
    for r in range(max(0, row-1), min(ROWS, row+2)):
        for c in range(max(0, col-1), min(COLS, col+2)):
            if (r, c) in mines:
                count += 1
    return count

# Reveal a cell
def reveal(row, col):
    global game_over, win
    
    if (row, col) in flagged or (row, col) in revealed:
        return
        
    revealed.add((row, col))
    
    if (row, col) in mines:
        game_over = True
        return
        
    # Count adjacent mines
    count = count_adjacent_mines(row, col)
    board[row][col] = str(count) if count > 0 else ' '
    
    # If empty, reveal adjacent cells
    if count == 0:
        for r in range(max(0, row-1), min(ROWS, row+2)):
            for c in range(max(0, col-1), min(COLS, col+2)):
                if (r, c) != (row, col) and (r, c) not in revealed:
                    reveal(r, c)
    
    # Check win condition
    if len(revealed) == ROWS * COLS - MINES:
        win = True

# Draw the game board
def draw_board():
    os.system('clear')
    print("=== MINESWEEPER ===")
    print(f"Flags: {len(flagged)} | Mines: {MINES}")
    
    # Print column numbers
    print("  ", end="")
    for c in range(COLS):
        print(f" {c}", end="")
    print()
    
    # Print board
    for r in range(ROWS):
        print(f"{r} |", end="")
        for c in range(COLS):
            if (r, c) == tuple(cursor):
                print("[", end="")
            else:
                print(" ", end="")
                
            if (r, c) in flagged:
                print("F", end="")
            elif (r, c) in revealed:
                if game_over and (r, c) in mines:
                    print("X", end="")
                else:
                    print(board[r][c], end="")
            else:
                print("?", end="")
                
            if (r, c) == tuple(cursor):
                print("]", end="")
            else:
                print(" ", end="")
        print("|")
    
    print()
    print("Controls:")
    print("WASD: Move cursor | F: Flag | Space: Reveal | Q: Quit")

# Main game loop
def main():
    global cursor, game_over, win
    
    # Initialize game
    place_mines()
    
    old_settings = setup_terminal()
    
    try:
        while not game_over and not win:
            draw_board()
            
            # Get input
            key = get_key()
            if key:
                key = key.upper()
                # Move cursor
                if key == 'W' and cursor[0] > 0:
                    cursor[0] -= 1
                elif key == 'S' and cursor[0] < ROWS - 1:
                    cursor[0] += 1
                elif key == 'A' and cursor[1] > 0:
                    cursor[1] -= 1
                elif key == 'D' and cursor[1] < COLS - 1:
                    cursor[1] += 1
                # Flag cell
                elif key == 'F':
                    r, c = cursor
                    if (r, c) in flagged:
                        flagged.remove((r, c))
                    elif (r, c) not in revealed:
                        flagged.add((r, c))
                # Reveal cell
                elif key == ' ':
                    reveal(cursor[0], cursor[1])
                # Quit
                elif key == 'Q':
                    return
            
            # Small delay
            import time
            time.sleep(0.05)
        
        # Game over or win
        draw_board()
        
        if win:
            print("You win! All safe cells revealed.")
        elif game_over:
            print("Game over! You hit a mine.")
            
            # Reveal all mines
            for r, c in mines:
                board[r][c] = 'X'
                revealed.add((r, c))
            
        print("Press any key to exit...")
        input()
        
    finally:
        restore_terminal(old_settings)

if __name__ == "__main__":
    main()
EOL

echo "Creating setup helper script..."
cat > "$BASE_DIR/install_modules.sh" << 'EOL'
#!/bin/bash

# Install required Python modules
echo "Checking Python setup..."

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Installing pip3..."
    curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py
    python3 get-pip.py
    rm get-pip.py
fi

# Try to install the windows-curses module (may work on some systems)
echo "Installing Python modules..."
pip3 install windows-curses 2>/dev/null || echo "Note: windows-curses not available (normal on Linux)"

# Create a test script to verify curses
cat > /tmp/test_curses.py << 'PYEOF'
#!/usr/bin/env python3
import sys
try:
    import curses
    print("SUCCESS: Curses module is available")
    sys.exit(0)
except ImportError as e:
    print(f"ERROR: Curses module is not available: {e}")
    sys.exit(1)
PYEOF

# Run the test
python3 /tmp/test_curses.py
if [ $? -eq 0 ]; then
    echo "Curses is available - games should work properly"
else
    echo "Curses is not available - games will use fallback mode"
fi

# Clean up
rm /tmp/test_curses.py
EOL

# Set permissions
echo "Setting permissions..."
chmod +x "$BASE_DIR/ssh_wrapper.sh"
chmod +x "$BASE_DIR/main_menu.sh"
chmod +x "$BASE_DIR/install_modules.sh"
chmod +x "$GAMES_DIR/snake/welcome.sh"
chmod +x "$GAMES_DIR/snake/snake.py"
chmod +x "$GAMES_DIR/snake/simple_snake.py"
chmod +x "$GAMES_DIR/minesweeper/welcome.sh"
chmod +x "$GAMES_DIR/minesweeper/minesweeper.py"
chmod +x "$GAMES_DIR/minesweeper/simple_minesweeper.py"

# Fix ownership
echo "Setting ownership..."
chown -R games:games "$BASE_DIR"

# Update the shell for the games user
echo "Setting login shell for games user..."
usermod -s "$BASE_DIR/ssh_wrapper.sh" games

# Install Python modules
echo "Installing Python modules..."
/bin/bash "$BASE_DIR/install_modules.sh"

echo "==== Setup Complete ===="
echo "Players can connect via: ssh games@ssh.karthik.lol"
echo "Password: games"