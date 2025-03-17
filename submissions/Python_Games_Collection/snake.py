import pygame
import random
import os

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 20

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# Fonts
FONT = pygame.font.SysFont("comicsans", 40)
FONT_SMALL = pygame.font.SysFont("comicsans", 30)

# High score file
HIGH_SCORE_FILE = "snake_high_score.txt"

# Load high score
def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as file:
            return int(file.read())
    return 0

# Save high score
def save_high_score(score):
    with open(HIGH_SCORE_FILE, "w") as file:
        file.write(str(score))

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Clock for controlling FPS
clock = pygame.time.Clock()

# Snake and food
def draw_snake(snake):
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (*segment, CELL_SIZE, CELL_SIZE))

def draw_food(food):
    pygame.draw.rect(screen, RED, (*food, CELL_SIZE, CELL_SIZE))

def draw_score(score, high_score):
    score_text = FONT_SMALL.render(f"Score: {score}", True, YELLOW)
    high_score_text = FONT_SMALL.render(f"High Score: {high_score}", True, YELLOW)
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (WIDTH - high_score_text.get_width() - 10, 10))

def draw_game_over(score, high_score):
    screen.fill(BLACK)
    game_over_text = FONT.render("GAME OVER", True, CYAN)
    score_text = FONT_SMALL.render(f"Score: {score}", True, YELLOW)
    high_score_text = FONT_SMALL.render(f"High Score: {high_score}", True, YELLOW)
    restart_text = FONT_SMALL.render("Press R to Restart", True, YELLOW)
    quit_text = FONT_SMALL.render("Press Q to Quit", True, YELLOW)

    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2 + 40))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 80))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 120))

def main():
    snake = [[WIDTH // 2, HEIGHT // 2]]
    direction = (CELL_SIZE, 0)
    food = [random.randint(0, (WIDTH - CELL_SIZE) // CELL_SIZE) * CELL_SIZE,
            random.randint(0, (HEIGHT - CELL_SIZE) // CELL_SIZE) * CELL_SIZE]
    score = 0
    high_score = load_high_score()
    game_over = False
    paused = False

    while True:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if not game_over and not paused:
                    if event.key == pygame.K_UP and direction != (0, CELL_SIZE):
                        direction = (0, -CELL_SIZE)
                    if event.key == pygame.K_DOWN and direction != (0, -CELL_SIZE):
                        direction = (0, CELL_SIZE)
                    if event.key == pygame.K_LEFT and direction != (CELL_SIZE, 0):
                        direction = (-CELL_SIZE, 0)
                    if event.key == pygame.K_RIGHT and direction != (-CELL_SIZE, 0):
                        direction = (CELL_SIZE, 0)
                if game_over:
                    if event.key == pygame.K_r:
                        main()
                        return
                    if event.key == pygame.K_q:
                        pygame.quit()
                        return

        if not game_over and not paused:
            new_head = [snake[0][0] + direction[0], snake[0][1] + direction[1]]

            if (
                new_head[0] < 0 or new_head[0] >= WIDTH or
                new_head[1] < 0 or new_head[1] >= HEIGHT or
                new_head in snake
            ):
                game_over = True
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
                continue

            snake.insert(0, new_head)

            if new_head == food:
                score += 10
                food = [random.randint(0, (WIDTH - CELL_SIZE) // CELL_SIZE) * CELL_SIZE,
                        random.randint(0, (HEIGHT - CELL_SIZE) // CELL_SIZE) * CELL_SIZE]
            else:
                snake.pop()

        draw_snake(snake)
        draw_food(food)
        draw_score(score, high_score)

        if paused:
            pause_text = FONT.render("PAUSED", True, YELLOW)
            screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))

        if game_over:
            draw_game_over(score, high_score)

        pygame.display.flip()
        clock.tick(10)

if __name__ == "__main__":
    main()
