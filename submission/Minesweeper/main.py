import random
import re

"""
rules:
    1. 20x20 board with 40 mines
    2. Player clicks random square, if it is blank, all the blank ones and the first layer are revealed.
    3. Game continues
"""


class Board():
    def __init__(self, mines=40, rows=20, cols=20):
        self.mines = mines
        self.mines_left = mines
        self.mines_location = []
        self.rows = rows
        self.columns = cols
        self.dug = set() # if we dig at 0, 0, then self.dug = {(0,0)}
        self.visible_board, self.background_board = self.create_boards()
        self.label_board()

    def convert_visible_board_to_str(self, board=None):
        if not board:
            board = self.visible_board
        return_board = ""
        i = 0
        return_board += "# | "
        for j in range(self.columns):
            return_board += str(j) + " | "
        return_board += "\n--------------------------------------------------------------------------------\n"
        for row in board:
            return_board += str(i) + " | "
            for col in row:
                return_board += col + " | "
            return_board += "\n--------------------------------------------------------------------------------\n"
            i += 1
        return return_board

    def print_board(self, board=None):
        print(self.convert_visible_board_to_str(board))

    def create_boards(self):
        visible_board = []
        background_board = []
        mines = self.mines

        for row in range(self.rows):
            visible_board.append(['#'] * self.columns)

        for row in range(self.rows):
            background_board.append(['#'] * self.columns)

        while mines > 0:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.columns - 1)
            if background_board[row][col] == '*':
                continue
            background_board[row][col] = '*'
            mines -= 1
            self.mines_location.append((row, col))

        return visible_board, background_board

    def label_board(self):
        for row in range(self.rows):
            for col in range(self.columns):
                if self.background_board[row][col] != '*':
                    self.background_board[row][col] = str(self.get_num_neighbouring_mines(row, col))

    def get_num_neighbouring_mines(self, row, col):
        # top left: (row-1, col-1)
        # top middle: (row-1, col)
        # top right: (row-1, col+1)
        # left: (row, col-1)
        # right: (row, col+1)
        # bottom left: (row+1, col-1)
        # bottom middle: (row+1, col)
        # bottom right: (row+1, col+1)
        num_neighbouring_mines = 0
        board = self.background_board
        if row > 0:
            if col > 0:
                if board[row-1][col-1] == '*': #* Top Left Check
                    num_neighbouring_mines += 1
            if board[row-1][col] == "*": #* Top Middle Check
                num_neighbouring_mines += 1
            if col < self.columns - 1:
                if board[row-1][col+1] == "*": #* Top Right Check
                    num_neighbouring_mines += 1

        if col > 0:
            if board[row][col-1] == "*": #* Left Check
                num_neighbouring_mines += 1
        if col < self.columns - 1:
            if board[row][col+1] == "*": #* Right Check
                num_neighbouring_mines += 1

        if row < self.rows - 1:
            if board[row+1][col-1] == "*": #* Bottom Left Check
                num_neighbouring_mines += 1
            if board[row+1][col] == "*": #* Bottom Middle Check
                num_neighbouring_mines += 1
            if col < self.columns - 1:
                if board[row+1][col+1] == "*": #* Bottom Right Check
                    num_neighbouring_mines += 1

        return num_neighbouring_mines

    def dig(self, row, col):
        # dig at that location!
        # return True if successful dig, False if bomb dug

        # a few scenarios:
        # hit a bomb -> game over
        # dig at location with neighbouring bombs -> finish dig
        # dig at location with no neighbouring bombs -> recursively dig neighbors!

        self.dug.add((row, col)) # keep track that we dug here

        try:
            if self.background_board[row][col] == '*':
                return False
            elif int(self.background_board[row][col]) > 0:
                return True
        except ValueError:
            pass

        # self.board[row][col] == 0
        for r in range(max(0, row-1), min(self.rows-1, row+1)+1):
            for c in range(max(0, col-1), min(self.rows-1, col+1)+1):
                if (r, c) in self.dug:
                    continue # don't dig where you've already dug
                self.dig(r, c)

        # if our initial dig didn't hit a bomb, we *shouldn't* hit a bomb here
        return True

    def update_board(self):
        for coord in self.dug:
            self.visible_board[coord[0]][coord[1]] = self.background_board[coord[0]][coord[1]]

    def __str__(self):
        self.update_board()
        board = self.visible_board
        return_board = ""
        i = 0
        return_board += "# | "
        for j in range(self.columns):
            return_board += str(j) + " | "
        return_board += "\n--------------------------------------------------------------------------------\n"
        for row in board:
            return_board += str(i) + " | "
            for col in row:
                return_board += col + " | "
            return_board += "\n--------------------------------------------------------------------------------\n"
            i += 1
        return return_board

def run():
    board = Board(mines=7, rows=10, cols=10)

    # Step 2: show the user the board and ask for where they want to dig
    # Step 3a: if location is a bomb, show game over message
    # Step 3b: if location is not a bomb, dig recursively until each square is at least
    #          next to a bomb
    # Step 4: repeat steps 2 and 3a/b until there are no more places to dig -> VICTORY!
    safe = True

    while len(board.dug) < board.rows * board.columns - board.mines:
        print(board)
        # 0,0 or 0, 0 or 0,    0
        user_input = re.split(',(\\s)*', input("Where would you like to dig? Input as row,col: "))  # '0, 3'
        col, row = int(user_input[0]), int(user_input[-1])
        if row < 0 or row >= board.rows or col < 0 or col >= board.columns:
            print("Invalid location. Try again.")
            continue

        # if it's valid, we dig
        safe = board.dig(row, col)
        if not safe:
            # dug a bomb ahhhhhhh
            break # (game over rip)

    # 2 ways to end loop, lets check which one
    if safe:
        print("CONGRATULATIONS!!!! YOU ARE VICTORIOUS!")
    else:
        print("SORRY GAME OVER :(")
        # let's reveal the whole board!
        board.print_board(board.background_board)

