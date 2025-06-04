import copy

blinky = ["Β", "β"]
pinky = ["Φ", "φ"]
inky = ["Ν", "ν"] # The greek letter Iota looked too much like the map which is why I had to use Nu
clyde = ["$", "€"] # Lore: Clyde is different from everyone else that's why his symbol is special 
class Board:
    def __init__(self):
        self.map_size = (31, 28)
        self.frames = 0
        self.pacman_map = [
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
            ["|", "*", "*", "*", "*", "*", "*", "*", "*", "*", "|", "|", "*", "*", "*", "*", "|", "|", "*", "*", "*", "*", "*", "*", "*", "*", "*", "|"],
            ["|", "*", "|", "-", "-", "-", "-", "-", "|", "*", "|", "|", "*", "-", "-", "*", "|", "|", "*", "|", "-", "-", "-", "-", "-", "|", "*", "|"],
            ["|", "*", "|", "-", "-", "-", "-", "-", "|", "*", "-", "-", "*", "|", "|", "*", "-", "-", "*", "|", "-", "-", "-", "-", "-", "|", "*", "|"],
            ["|", "*", "*", "*", "|", "|", "*", "*", "*", "*", "*", "*", "*", "|", "|", "*", "*", "*", "*", "*", "*", "*", "|", "|", "*", "*", "*", "|"],
            ["-", "-", "-", "*", "|", "|", "*", "-", "-", "*", "|", "-", "-", "-", "-", "-", "-", "|", "*", "-", "-", "*", "|", "|", "*", "-", "-", "-"],
            [" ", " ", "|", "*", "|", "|", "*", "|", "|", "*", "|", "-", "-", "-", "-", "-", "-", "|", "*", "|", "|", "*", "|", "|", "*", "|", " ", " "],
            ["-", "-", "-", "*", "-", "-", "*", "|", "|", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "|", "|", "*", "-", "-", "*", "-", "-", "-"],
            ["*", "*", "*", "*", "*", "*", "*", "|", "|", "*", "|", "-", "-", "-", "-", "-", "-", "|", "*", "|", "|", "*", "*", "*", "*", "*", "*", "*"],
            ["-", "-", "-", "*", "|", "-", "-", "|", "|", "*", "|", "-", "-", "-", "-", "-", "-", "|", "*", "|", "|", "-", "-", "|", "*", "-", "-", "-"],
            [" ", " ", "|", "*", "|", "-", "-", "-", "|", "*", "|", "-", "-", "-", "-", "-", "-", "|", "*", "|", "-", "-", "-", "|", "*", "|", " ", " "],
            [" ", " ", "|", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "B", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "|", " ", " "],
            [" ", " ", "|", "*", "-", "-", "*", "-", "-", "*", "|", "-", "-", " ", " ", "-", "-", "|", "*", "-", "-", "*", "-", "-", "*", "|", " ", " "],
            ["-", "-", "-", "*", "|", "|", "*", "|", "|", "*", "|", " ", " ", " ", " ", " ", " ", "|", "*", "|", "|", "*", "|", "|", "*", "-", "-", "-"],
            ["|", "*", "*", "*", "|", "|", "*", "|", "|", "*", "|", " ", " ", " ", " ", " ", " ", "|", "*", "|", "|", "*", "|", "|", "*", "*", "*", "|"],
            ["|", "*", "|", "-", "-", "|", "*", "|", "|", "*", "|", " ", "P", "I", "C", " ", " ", "|", "*", "|", "|", "*", "|", "-", "-", "|", "*", "|"],
            ["|", "*", "|", "-", "-", "|", "*", "-", "-", "*", "|", "-", "-", "-", "-", "-", "-", "|", "*", "-", "-", "*", "|", "-", "-", "|", "*", "|"],
            ["|", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "|"],
            ["-", "-", "-", "*", "-", "-", "*", "-", "-", "*", "|", "-", "-", "-", "-", "-", "-", "|", "*", "-", "-", "*", "-", "-", "*", "-", "-", "-"],
            [" ", " ", "|", "*", "|", "|", "*", "|", "|", "*", "|", "-", "-", "-", "-", "-", "-", "|", "*", "|", "|", "*", "|", "|", "*", "|", " ", " "],
            [" ", " ", "|", "*", "|", "|", "*", "|", "|", "*", "*", "*", "*", "|", "|", "*", "*", "*", "*", "|", "|", "*", "|", "|", "*", "|", " ", " "],
            [" ", " ", "|", "*", "|", "|", "*", "|", "-", "-", "-", "|", "*", "|", "|", "*", "|", "-", "-", "-", "|", "*", "|", "|", "*", "|", " ", " "],
            ["-", "-", "-", "*", "|", "|", "*", "|", "-", "-", "-", "|", "*", "-", "-", "*", "|", "-", "-", "-", "|", "*", "|", "|", "*", "-", "-", "-"],
            ["|", "*", "*", "*", "|", "|", "*", "*", "*", "*", "*", "*", "*", "0", "*", "*", "*", "*", "*", "*", "*", "*", "|", "|", "*", "*", "*", "|"],
            ["|", "*", "|", "-", "-", "-", "-", "-", "-", "|", "*", "|", "-", "-", "-", "-", "|", "*", "|", "-", "-", "-", "-", "-", "-", "|", "*", "|"],
            ["|", "*", "|", "-", "-", "-", "-", "-", "-", "|", "*", "|", "-", "-", "-", "-", "|", "*", "|", "-", "-", "-", "-", "-", "-", "|", "*", "|"],
            ["|", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "|", "|", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "|"],
            ["|", "*", "|", "-", "-", "|", "*", "|", "-", "-", "-", "|", "*", "|", "|", "*", "|", "-", "-", "-", "|", "*", "|", "-", "-", "|", "*", "|"],
            ["|", "*", "|", "-", "-", "|", "*", "|", "-", "-", "-", "|", "*", "-", "-", "*", "|", "-", "-", "-", "|", "*", "|", "-", "-", "|", "*", "|"],
            ["|", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "|"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
        ]
        self.actual_map = copy.deepcopy(self.pacman_map)
        self.score = 0
        self.pac = PacMan()
        self.blinky = Blinky()
        self.pinky = Pinky()
        self.inky = Inky()
        self.clyde = Clyde()
        self.ghosts = [self.blinky, self.pinky, self.inky, self.clyde]
        self.ghost_can_start = [True, False, False, False]
        self.spawn()
        self.ghosts_set_state(0)
    
    def ghosts_set_state(self, state):
        # 0 = scatter, 1 = chase, 2 = frightened, 3 = eaten
        for ghost in self.ghosts:
            ghost.state = state
    
    def check_for_win(self):
        flag = False
        for i in self.actual_map:
            for j in i:
                if j in ["0", "ᗣ", "ᗢ", "ᗧ", "ᗤ"]:
                    flag = True
        if flag == False:
            return "LOSS"
        for i in self.actual_map:
            for j in i:
                if j == "*" or j == "O":
                    return False
        return True
    
    def switch_states(self):
        # As it was in OG Pacman
        if self.frames < 30*7:
            self.ghosts_set_state(0)
        elif self.frames < 30*7+30*20:
            self.ghosts_set_state(1)
        elif self.frames < 30*7+30*20+30*7:
            self.ghosts_set_state(0)
        elif self.frames < 30*7+30*20+30*7+30*20:
            self.ghosts_set_state(1)
        elif self.frames < 30*7+30*20+30*7+30*20+30*5:
            self.ghosts_set_state(0)
        elif self.frames < 30*7+30*20+30*7+30*20+30*5+30*20:
            self.ghosts_set_state(1)
        elif self.frames < 30*7+30*20+30*7+30*20+30*5+30*20+30*5:
            self.ghosts_set_state(0)
        else:
            self.ghosts_set_state(1)
    
    def spawn(self):
        for i in range(len(self.actual_map)):
            for j in range(len(self.actual_map[i])):
                if self.actual_map[i][j] == "I":
                    self.inky.pos = copy.deepcopy(self.blinky.pos)
                    self.actual_map[i][j] = " "
                elif self.actual_map[i][j] == "P":
                    self.pinky.pos = copy.deepcopy(self.blinky.pos)
                    self.actual_map[i][j] = " "
                elif self.actual_map[i][j] == "B":
                    self.blinky.pos = [i, j]
                    self.actual_map[i][j] = " "
                elif self.actual_map[i][j] == "0":
                    self.pac.pos = [i, j]
                    self.actual_map[i][j] = self.pac.pacman[self.pac.direction]
                elif self.actual_map[i][j] == "C":
                    self.clyde.pos = copy.deepcopy(self.blinky.pos)
                    self.actual_map[i][j] = " "
    
    def ghost_move(self, ghost, info):
        if ghost.is_eaten:
            ghost_eaten_move()
            return
        c_position = info[0]
        t_position = info[1]
        self.actual_map[c_position[0]][c_position[1]] = ghost.last_pos_tile
        ghost.pos = copy.deepcopy(t_position)
        if self.actual_map[ghost.pos[0]][ghost.pos[1]] not in ["Β", "β", "Φ", "φ", "Ν", "ν", "$", "€"]:
            ghost.last_pos_tile = self.actual_map[ghost.pos[0]][ghost.pos[1]]
        self.actual_map[t_position[0]][t_position[1]] = ghost.sprite[0]
    
    def calculate_pinky_target(self, dist=4):
        pos = self.pac.pos
        direction = self.pac.direction
        if direction <= 1: # Travelling down
            return [pos[0] + dist, pos[1]]
        elif direction == 2: # Travelling up
            return [pos[0] - dist, pos[1]]
        elif direction == 3: # Travelling right
            return [pos[0], pos[1] + dist]
        elif direction == 4: # Travelling left
            return [pos[0], pos[1] - dist]
    
    def calculate_inky_target(self):
        offset = self.calculate_pinky_target(2)
        pacPos = self.pac.pos
        blinky = self.blinky.pos
        flipped_vector = [offset[0] - pacPos[0], offset[1] - pacPos[1]]
        flipped_vector[0] *= -1; flipped_vector[1] *= -1;
        return [pacPos[0] + flipped_vector[0], pacPos[1] + flipped_vector[1]]
    
    def move(self):
        #! TODO: UPDATE SCORE!
        walls = ["|", "-", " "] # The characters that represent walls
        position = self.pac.pos.copy()
        n_direction = self.pac.n_direction
        if n_direction == 3:
            if position[1] == self.map_size[1]-1:
                self.pac.direction = 3
            elif self.pacman_map[position[0]][position[1] + 1] not in walls:
                self.pac.direction = 3
        elif n_direction == 4:
            if position[1] == 0:
                self.pac.direction = 4
            elif self.pacman_map[position[0]][position[1] - 1] not in walls:
                self.pac.direction = 4
        elif n_direction == 1:
            if self.pacman_map[position[0] + 1][position[1]] not in walls:
                self.pac.direction = 1
        else:
            if self.pacman_map[position[0] - 1][position[1]] not in walls:
                self.pac.direction = 2
        
        direction = self.pac.direction
        
        # Travelling left or right
        if direction == 3:
            # Travelling right
            if position[1] == self.map_size[1]-1:
                self.pac.pos[1] = 0
                self.actual_map[position[0]][position[1]] = " "
                self.actual_map[position[0]][0] = self.pac.pacman[3]
            else:
                if self.pacman_map[position[0]][position[1] + 1] not in walls:
                    self.pac.pos[1] += 1
                    self.actual_map[position[0]][position[1]] = " "
                    self.actual_map[position[0]][position[1] + 1] = self.pac.pacman[3]
        elif direction == 4:
            # Travelling left
            if position[1] == 0:
                self.pac.pos[1] = self.map_size[1]-1
                self.actual_map[position[0]][position[1]] = " "
                self.actual_map[position[0]][(self.map_size[1]-1)] = self.pac.pacman[3]
            else:
                if self.pacman_map[position[0]][position[1] - 1] not in walls:
                    self.pac.pos[1] -= 1
                    self.actual_map[position[0]][position[1]] = " "
                    self.actual_map[position[0]][position[1] - 1] = self.pac.pacman[4]
        # Travelling up or down
        elif direction == 1:
            # Travelling down
            if self.pacman_map[position[0] + 1][position[1]] not in walls:
                self.pac.pos[0] += 1
                self.actual_map[position[0]][position[1]] = " "
                self.actual_map[position[0] + 1][position[1]] = self.pac.pacman[1]
        elif direction == 2:
            # Travelling up
            if self.pacman_map[position[0] - 1][position[1]] not in walls:
                self.pac.pos[0] -= 1
                self.actual_map[position[0]][position[1]] = " "
                self.actual_map[position[0] - 1][position[1]] = self.pac.pacman[2]
    
    def update(self):
        # Move pacman
        self.frames += 1
        self.switch_states()
        if self.frames % 3 == 0:
            self.move()
        for ghost in self.ghosts:
            # Move ghosts
            if self.frames % 3 == 0:
                if ghost == self.blinky:
                    self.ghost_move(ghost, ghost.get_movement(self.pacman_map, self.pac.pos))
                elif ghost == self.pinky and self.ghost_can_start[1] == True:
                    self.ghost_move(ghost, ghost.get_movement(self.pacman_map, self.calculate_pinky_target()))
                elif ghost == self.inky and self.ghost_can_start[2] == True:
                    self.ghost_move(ghost, ghost.get_movement(self.pacman_map, self.calculate_inky_target()))
                elif ghost == self.clyde and self.ghost_can_start[3] == True:
                    self.ghost_move(ghost, ghost.get_movement(self.pacman_map, self.pac.pos))
        win = self.check_for_win()
        if win == True:
            return True
        elif win == "LOSS":
            return "LOSS"
        if self.frames == 30:
            self.ghost_can_start[1] = True
        elif self.frames == 120:
            self.ghost_can_start[2] = True
        elif self.frames == 220:
            self.ghost_can_start[3] = True
    
    def __str__(self):
        # Print the map
        out = ""
        for i in self.actual_map:
            for j in i:
                out += j + " "
            out += "\n"
        return out


class PacMan:
    def __init__(self):
        self.pacman = ["0", "ᗣ", "ᗢ", "ᗧ", "ᗤ"]
        self.direction = 0 # The index of the appropriate sprite in the pacman list
        self.n_direction = -1 # The next direction
        self.pos = []


class Blinky:
    def __init__(self):
        self.sprite = ["Β", "β"]
        # self.target_pos = [] # The next position
        self.pos = [0,0]
        self.state = 1 # 0 = scatter, 1 = chase, 2 = frightened, 3 = eaten
        self.is_eaten = False
        self.directions = ["D", "U", "R", "L"]
        self.facing = 0 # The index of the direction it can't turn to
        self.last_pos_tile = "*"
        self.scatter_pos = [0, 31]
    
    def update_facing(self, direction):
        if direction == "D":
            self.facing = 1
        elif direction == "U":
            self.facing = 0
        elif direction == "R":
            self.facing = 3
        elif direction == "L":
            self.facing = 2
    
    def get_movement(self, actual_map, target_pos):
        if self.state == 0:
            target_pos = self.scatter_pos
        m = copy.deepcopy(actual_map)
        walls = ["|", "-", " "]
        position = self.pos
        tilePos = []
        valid_directions = []
        info = [self.pos, []]
        min_distance = 999999
        for i in range(len(self.directions)):
            if i != self.facing:
                if i == 2:
                    if self.pos[1] == 27:
                        valid_directions.append("R")
                        tilePos.append([self.pos[0], 0])
                    elif m[position[0]][position[1] + 1] not in walls:
                        valid_directions.append("R")
                        tilePos.append([position[0], (position[1] + 1)])   
                elif i == 3:
                    if self.pos[1] == 0:
                        valid_directions.append("L")
                        tilePos.append([self.pos[0], 27])
                    elif m[position[0]][position[1] - 1] not in walls:
                        valid_directions.append("L")
                        tilePos.append([self.pos[0], position[1] - 1])
                elif i == 1:
                    if m[position[0] + 1][position[1]] not in walls:
                        valid_directions.append("U")
                        tilePos.append([position[0] + 1, position[1]])
                else:
                    if m[position[0] - 1][position[1]] not in walls:
                        valid_directions.append("D")
                        tilePos.append([position[0] - 1, position[1]])
        if len(tilePos) == 1:
            info[1] = tilePos[0]
            self.update_facing(valid_directions[0])
            return info
        for i in range(len(tilePos)):
            distance = (tilePos[i][0] - target_pos[0])**2 + (tilePos[i][1] - target_pos[1])**2
            distance = distance**0.5
            if distance < min_distance:
                min_distance = distance
                self.update_facing(valid_directions[i])
                info[1] = tilePos[i]
        return info


class Pinky:
    def __init__(self):
        self.sprite = ["Φ", "φ"]
        # self.target_pos = [] # The next position
        self.pos = [0,0]
        self.state = 1 # 0 = scatter, 1 = chase, 2 = frightened, 3 = eaten
        self.is_eaten = False
        self.directions = ["D", "U", "R", "L"]
        self.facing = 0 # The index of the direction it can't turn to
        self.last_pos_tile = "*"
        self.scatter_pos = [0, 0]
    
    def update_facing(self, direction):
        if direction == "D":
            self.facing = 1
        elif direction == "U":
            self.facing = 0
        elif direction == "R":
            self.facing = 3
        elif direction == "L":
            self.facing = 2
    
    def get_movement(self, actual_map, target_pos):
        if self.state == 0:
            target_pos = self.scatter_pos
        m = copy.deepcopy(actual_map)
        walls = ["|", "-", " "]
        position = self.pos
        tilePos = []
        valid_directions = []
        info = [self.pos, []]
        min_distance = 999999
        for i in range(len(self.directions)):
            if i != self.facing:
                if i == 2:
                    if self.pos[1] == 27:
                        valid_directions.append("R")
                        tilePos.append([self.pos[0], 0])
                    elif m[position[0]][position[1] + 1] not in walls:
                        valid_directions.append("R")
                        tilePos.append([position[0], (position[1] + 1)])   
                elif i == 3:
                    if self.pos[1] == 0:
                        valid_directions.append("L")
                        tilePos.append([self.pos[0], 27])
                    elif m[position[0]][position[1] - 1] not in walls:
                        valid_directions.append("L")
                        tilePos.append([self.pos[0], position[1] - 1])
                elif i == 1:
                    if m[position[0] + 1][position[1]] not in walls:
                        valid_directions.append("U")
                        tilePos.append([position[0] + 1, position[1]])
                else:
                    if m[position[0] - 1][position[1]] not in walls:
                        valid_directions.append("D")
                        tilePos.append([position[0] - 1, position[1]])
        if len(tilePos) == 1:
            info[1] = tilePos[0]
            self.update_facing(valid_directions[0])
            return info
        for i in range(len(tilePos)):
            distance = (tilePos[i][0] - target_pos[0])**2 + (tilePos[i][1] - target_pos[1])**2
            distance = distance**0.5
            if distance < min_distance:
                min_distance = distance
                self.update_facing(valid_directions[i])
                info[1] = tilePos[i]
        return info


class Inky:
    def __init__(self):
        self.sprite = ["Ν", "ν"]
        # self.target_pos = [] # The next position
        self.pos = [0,0]
        self.state = 1 # 0 = scatter, 1 = chase, 2 = frightened, 3 = eaten
        self.is_eaten = False
        self.directions = ["D", "U", "R", "L"]
        self.facing = 0 # The index of the direction it can't turn to
        self.last_pos_tile = "*"
        self.scatter_pos = [31, 0]
    # 404: Code not found
    def update_facing(self, direction):
        if direction == "D":
            self.facing = 1
        elif direction == "U":
            self.facing = 0
        elif direction == "R":
            self.facing = 3
        elif direction == "L":
            self.facing = 2
    
    def get_movement(self, actual_map, target_pos):
        if self.state == 0:
            target_pos = self.scatter_pos
        m = copy.deepcopy(actual_map)
        walls = ["|", "-", " "]
        position = self.pos
        tilePos = []
        valid_directions = []
        info = [self.pos, []]
        min_distance = 999999
        for i in range(len(self.directions)):
            if i != self.facing:
                if i == 2:
                    if self.pos[1] == 27:
                        valid_directions.append("R")
                        tilePos.append([self.pos[0], 0])
                    elif m[position[0]][position[1] + 1] not in walls:
                        valid_directions.append("R")
                        tilePos.append([position[0], (position[1] + 1)])   
                elif i == 3:
                    if self.pos[1] == 0:
                        valid_directions.append("L")
                        tilePos.append([self.pos[0], 27])
                    elif m[position[0]][position[1] - 1] not in walls:
                        valid_directions.append("L")
                        tilePos.append([self.pos[0], position[1] - 1])
                elif i == 1:
                    if m[position[0] + 1][position[1]] not in walls:
                        valid_directions.append("U")
                        tilePos.append([position[0] + 1, position[1]])
                else:
                    if m[position[0] - 1][position[1]] not in walls:
                        valid_directions.append("D")
                        tilePos.append([position[0] - 1, position[1]])
        if len(tilePos) == 1:
            info[1] = tilePos[0]
            self.update_facing(valid_directions[0])
            return info
        for i in range(len(tilePos)):
            distance = (tilePos[i][0] - target_pos[0])**2 + (tilePos[i][1] - target_pos[1])**2
            distance = distance**0.5
            if distance < min_distance:
                min_distance = distance
                self.update_facing(valid_directions[i])
                info[1] = tilePos[i]
        return info


class Clyde:
    def __init__(self):
        self.sprite = ["$", "€"]
        # self.target_pos = [] # The next position
        self.pos = [0,0]
        self.state = 1 # 0 = scatter, 1 = chase, 2 = frightened, 3 = eaten
        self.is_eaten = False
        self.directions = ["D", "U", "R", "L"]
        self.facing = 0 # The index of the direction it can't turn to
        self.last_pos_tile = "*"
        self.scatter_pos = [28, 31]
    
    def update_facing(self, direction):
        if direction == "D":
            self.facing = 1
        elif direction == "U":
            self.facing = 0
        elif direction == "R":
            self.facing = 3
        elif direction == "L":
            self.facing = 2
    
    def get_movement(self, actual_map, target_pos):
        if self.state == 0:
            target_pos = self.scatter_pos
        distance = (self.pos[0] - target_pos[0])**2 + (self.pos[1] - target_pos[1])**2
        distance = distance**0.5
        if distance < 8:
            target_pos = self.scatter_pos
        m = copy.deepcopy(actual_map)
        walls = ["|", "-", " "]
        position = self.pos
        tilePos = []
        valid_directions = []
        info = [self.pos, []]
        min_distance = 999999
        for i in range(len(self.directions)):
            if i != self.facing:
                if i == 2:
                    if self.pos[1] == 27:
                        valid_directions.append("R")
                        tilePos.append([self.pos[0], 0])
                    elif m[position[0]][position[1] + 1] not in walls:
                        valid_directions.append("R")
                        tilePos.append([position[0], (position[1] + 1)])   
                elif i == 3:
                    if self.pos[1] == 0:
                        valid_directions.append("L")
                        tilePos.append([self.pos[0], 27])
                    elif m[position[0]][position[1] - 1] not in walls:
                        valid_directions.append("L")
                        tilePos.append([self.pos[0], position[1] - 1])
                elif i == 1:
                    if m[position[0] + 1][position[1]] not in walls:
                        valid_directions.append("U")
                        tilePos.append([position[0] + 1, position[1]])
                else:
                    if m[position[0] - 1][position[1]] not in walls:
                        valid_directions.append("D")
                        tilePos.append([position[0] - 1, position[1]])
        if len(tilePos) == 1:
            info[1] = tilePos[0]
            self.update_facing(valid_directions[0])
            return info
        for i in range(len(tilePos)):
            distance = (tilePos[i][0] - target_pos[0])**2 + (tilePos[i][1] - target_pos[1])**2
            distance = distance**0.5
            if distance < min_distance:
                min_distance = distance
                self.update_facing(valid_directions[i])
                info[1] = tilePos[i]
        return info


if __name__ == "__main__":
    import main
