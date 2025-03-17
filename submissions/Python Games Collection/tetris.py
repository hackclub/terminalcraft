import pygame
import random
from pygame import Rect

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 200

PLAY_AREA_LEFT = (SCREEN_WIDTH - SIDEBAR_WIDTH - GRID_WIDTH * GRID_SIZE) // 2
PLAY_AREA_TOP = (SCREEN_HEIGHT - GRID_HEIGHT * GRID_SIZE) // 2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)       # I piece
BLUE = (0, 0, 255)         # J piece
ORANGE = (255, 165, 0)     # L piece
YELLOW = (255, 255, 0)     # O piece
GREEN = (0, 255, 0)        # S piece
PURPLE = (128, 0, 128)     # T piece
RED = (255, 0, 0)          # Z piece

SHAPES = [
    [[0, 0], [0, 1], [1, 0], [1, 1]],      # O
    [[0, 0], [0, 1], [0, 2], [0, 3]],      # I
    [[0, 0], [0, 1], [0, 2], [1, 2]],      # L
    [[1, 0], [1, 1], [1, 2], [0, 2]],      # J
    [[0, 0], [1, 0], [1, 1], [2, 1]],      # S
    [[0, 1], [1, 1], [2, 1], [1, 0]],      # T
    [[0, 1], [1, 1], [1, 0], [2, 0]]       # Z
]

SHAPE_COLORS = [YELLOW, CYAN, ORANGE, BLUE, GREEN, PURPLE, RED]

class Tetrimino:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0

    def rotate(self):
        
        positions = self.get_positions()
        center_x = sum(pos[0] for pos in positions) / len(positions)
        center_y = sum(pos[1] for pos in positions) / len(positions)
        
        rotated = []
        for pos in self.shape:
            
            x = pos[1]
            y = -pos[0]
            rotated.append([x, y])
        
        return rotated

    def get_positions(self):
        positions = []
        for pos in self.shape:
            positions.append([self.x + pos[0], self.y + pos[1]])
        return positions

class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 25)
        self.reset_game()

    def reset_game(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.paused = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 0.5
        self.fall_time = 0
        self.fall_delay = 0.5

    def new_piece(self):
        
        shape = random.choice(SHAPES)
        
        return Tetrimino(GRID_WIDTH // 2 - 1, 0, shape)

    def valid_move(self, piece, x_offset=0, y_offset=0, rotated_shape=None):
        shape_to_check = rotated_shape if rotated_shape else piece.shape
        
        for pos in shape_to_check:
            x = piece.x + pos[0] + x_offset
            y = piece.y + pos[1] + y_offset
            
            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                return False
            if y >= 0 and self.grid[y][x] != 0:
                return False
        return True

    def lock_piece(self):
        for pos in self.current_piece.shape:
            x = self.current_piece.x + pos[0]
            y = self.current_piece.y + pos[1]
            if y >= 0:
                self.grid[y][x] = self.current_piece.color
        
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()

        if not self.valid_move(self.current_piece):
            self.game_over = True

    def clear_lines(self):
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(cell != 0 for cell in self.grid[y]):
                lines_to_clear.append(y)
        
        for line in lines_to_clear:
            
            self.grid.pop(line)
            
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])

        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            self.score += (100 * len(lines_to_clear)) * len(lines_to_clear)
        
            self.level = self.lines_cleared // 10 + 1
            self.fall_delay = max(0.1, 0.5 - (self.level - 1) * 0.05)

    def draw_grid(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
              
                rect = Rect(
                    PLAY_AREA_LEFT + x * GRID_SIZE,
                    PLAY_AREA_TOP + y * GRID_SIZE,
                    GRID_SIZE, GRID_SIZE
                )
                pygame.draw.rect(self.screen, GRAY, rect, 1)
          
                if self.grid[y][x] != 0:
                    pygame.draw.rect(self.screen, self.grid[y][x], rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)

    def draw_current_piece(self):
        for pos in self.current_piece.shape:
            x = self.current_piece.x + pos[0]
            y = self.current_piece.y + pos[1]
            if y >= 0:  
                rect = Rect(
                    PLAY_AREA_LEFT + x * GRID_SIZE,
                    PLAY_AREA_TOP + y * GRID_SIZE,
                    GRID_SIZE, GRID_SIZE
                )
                pygame.draw.rect(self.screen, self.current_piece.color, rect)
                pygame.draw.rect(self.screen, WHITE, rect, 1)

    def draw_next_piece(self):
        
        next_label = self.font.render("Next Piece:", True, WHITE)
        self.screen.blit(next_label, (SCREEN_WIDTH - SIDEBAR_WIDTH + 20, PLAY_AREA_TOP + 20))
        
        for pos in self.next_piece.shape:
            x = pos[0]
            y = pos[1]
            rect = Rect(
                SCREEN_WIDTH - SIDEBAR_WIDTH + 50 + x * GRID_SIZE,
                PLAY_AREA_TOP + 70 + y * GRID_SIZE,
                GRID_SIZE, GRID_SIZE
            )
            pygame.draw.rect(self.screen, self.next_piece.color, rect)
            pygame.draw.rect(self.screen, WHITE, rect, 1)

    def draw_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        
        self.screen.blit(score_text, (SCREEN_WIDTH - SIDEBAR_WIDTH + 20, PLAY_AREA_TOP + 180))
        self.screen.blit(level_text, (SCREEN_WIDTH - SIDEBAR_WIDTH + 20, PLAY_AREA_TOP + 220))
        self.screen.blit(lines_text, (SCREEN_WIDTH - SIDEBAR_WIDTH + 20, PLAY_AREA_TOP + 260))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.SysFont('Arial', 50)
        game_over_text = font.render("GAME OVER", True, WHITE)
        restart_text = self.font.render("Press R to restart", True, WHITE)
        
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

    def draw_pause(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.SysFont('Arial', 50)
        pause_text = font.render("PAUSED", True, WHITE)
        continue_text = self.font.render("Press P to continue", True, WHITE)
        
        self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

    def draw_controls(self):
        controls = [
            "Controls:",
            "← → : Move",
            "↑ : Rotate",
            "↓ : Soft Drop",
            "Space : Hard Drop",
            "P : Pause",
            "R : Restart"
        ]
        
        for i, text in enumerate(controls):
            control_text = self.font.render(text, True, WHITE)
            self.screen.blit(control_text, (SCREEN_WIDTH - SIDEBAR_WIDTH + 20, PLAY_AREA_TOP + 320 + i * 30))

    def draw_game_border(self):
        border_rect = Rect(
            PLAY_AREA_LEFT - 5,
            PLAY_AREA_TOP - 5,
            GRID_WIDTH * GRID_SIZE + 10,
            GRID_HEIGHT * GRID_SIZE + 10
        )
        pygame.draw.rect(self.screen, WHITE, border_rect, 5)

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_game_border()
        self.draw_grid()
        self.draw_current_piece()
        self.draw_next_piece()
        self.draw_score()
        self.draw_controls()
        
        if self.game_over:
            self.draw_game_over()
        elif self.paused:
            self.draw_pause()
            
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                elif self.paused:
                    if event.key == pygame.K_p:
                        self.paused = False
                else:
                    if event.key == pygame.K_LEFT:
                        if self.valid_move(self.current_piece, x_offset=-1):
                            self.current_piece.x -= 1
                    elif event.key == pygame.K_RIGHT:
                        if self.valid_move(self.current_piece, x_offset=1):
                            self.current_piece.x += 1
                    elif event.key == pygame.K_DOWN:
                        if self.valid_move(self.current_piece, y_offset=1):
                            self.current_piece.y += 1
                    elif event.key == pygame.K_UP:
                        rotated = self.current_piece.rotate()
                        if self.valid_move(self.current_piece, rotated_shape=rotated):
                            self.current_piece.shape = rotated
                    elif event.key == pygame.K_SPACE:
                        # Hard drop
                        while self.valid_move(self.current_piece, y_offset=1):
                            self.current_piece.y += 1
                        self.lock_piece()
                    elif event.key == pygame.K_p:
                        self.paused = True
                    elif event.key == pygame.K_r:
                        self.reset_game()
        return True

    def update(self, dt):
        if self.game_over or self.paused:
            return
            
        self.fall_time += dt
        if self.fall_time >= self.fall_delay:
            self.fall_time = 0
            if self.valid_move(self.current_piece, y_offset=1):
                self.current_piece.y += 1
            else:
                self.lock_piece()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0  # Convert milliseconds to seconds
            running = self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
