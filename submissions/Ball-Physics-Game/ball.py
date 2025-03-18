import pygame
import sys
import math
from pygame.locals import *
import random
from typing import List, Tuple
from pygame import gfxdraw

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
GRAVITY = 0.5
FRICTION = 0.95
BALL_RADIUS = 20
BOUNCE_FACTOR = 0.7
POWERUP_TYPES = ['SPEED', 'JUMP', 'GRAVITY', 'INVINCIBILITY']
POWERUP_COLORS = {
    'SPEED': (255, 165, 0),  # Orange
    'JUMP': (147, 112, 219),  # Purple
    'GRAVITY': (0, 255, 255),  # Cyan
    'INVINCIBILITY': (255, 215, 0)  # Gold
}
POWERUP_DURATION = 5000  # 5 seconds in milliseconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Set up the window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Ball Physics Game')
clock = pygame.time.Clock()

# Game elements
class Ball:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.particles: List[dict] = []
        self.active_powerups: dict = {}
        self.base_color = color
        
    def update(self):
        # Apply gravity
        if not self.on_ground:
            self.vel_y += GRAVITY
        
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Apply friction
        self.vel_x *= FRICTION
        
        # Check for small velocities and stop them
        if abs(self.vel_x) < 0.1:
            self.vel_x = 0
            
        # Check for ground collision
        if self.y + self.radius > WINDOW_HEIGHT:
            self.y = WINDOW_HEIGHT - self.radius
            self.vel_y = -self.vel_y * BOUNCE_FACTOR
            
            # Set on_ground flag if ball is moving very slowly
            if abs(self.vel_y) < 1:
                self.on_ground = True
                self.vel_y = 0
        else:
            self.on_ground = False
            
        # Check for wall collisions
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vel_x = -self.vel_x * BOUNCE_FACTOR
        elif self.x + self.radius > WINDOW_WIDTH:
            self.x = WINDOW_WIDTH - self.radius
            self.vel_x = -self.vel_x * BOUNCE_FACTOR
    
    def draw(self):
        # Draw a glow effect
        for i in range(10, 0, -1):
            alpha = int(255 * (i / 10))
            color = (*self.color, alpha)
            surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.gfxdraw.filled_circle(surface, self.radius, self.radius, self.radius, color)
            screen.blit(surface, (int(self.x) - self.radius, int(self.y) - self.radius))
        
        # Draw the ball
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def apply_powerup(self, powerup_type: str):
        self.active_powerups[powerup_type] = pygame.time.get_ticks()
        if powerup_type == 'SPEED':
            self.vel_x *= 1.5
        elif powerup_type == 'JUMP':
            self.vel_y = -15
        elif powerup_type == 'GRAVITY':
            global GRAVITY
            GRAVITY = 0.25
        elif powerup_type == 'INVINCIBILITY':
            self.color = (255, 215, 0)  # Change color to indicate invincibility
            
    def update_powerups(self):
        current_time = pygame.time.get_ticks()
        expired_powerups = []
        
        for powerup_type, start_time in self.active_powerups.items():
            if current_time - start_time > POWERUP_DURATION:
                expired_powerups.append(powerup_type)
                if powerup_type == 'GRAVITY':
                    global GRAVITY
                    GRAVITY = 0.5
                    
        for powerup in expired_powerups:
            del self.active_powerups[powerup]
            
    def add_particles(self, count: int):
        for _ in range(count):
            particle = {
                'x': self.x,
                'y': self.y,
                'vel_x': random.uniform(-2, 2),
                'vel_y': random.uniform(-2, 2),
                'lifetime': 255
            }
            self.particles.append(particle)
            
    def update_particles(self):
        for particle in self.particles[:]:
            particle['x'] += particle['vel_x']
            particle['y'] += particle['vel_y']
            particle['lifetime'] -= 5
            
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
                
    def draw_particles(self):
        for particle in self.particles:
            alpha = max(0, min(255, particle['lifetime']))
            color = (*self.color, alpha)
            surface = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(surface, color, (2, 2), 2)
            screen.blit(surface, (particle['x'] - 2, particle['y'] - 2))

class Platform:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
    
    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
    
    def check_collision(self, ball):
        # Check if ball intersects with platform
        dx = ball.x - max(self.rect.left, min(ball.x, self.rect.right))
        dy = ball.y - max(self.rect.top, min(ball.y, self.rect.bottom))
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < ball.radius:
            # Collision detected, determine which side
            
            # Top collision
            if ball.y < self.rect.top and ball.vel_y > 0:
                ball.y = self.rect.top - ball.radius
                ball.vel_y = -ball.vel_y * BOUNCE_FACTOR
                if abs(ball.vel_y) < 1:
                    ball.on_ground = True
                    ball.vel_y = 0
                    
            # Bottom collision
            elif ball.y > self.rect.bottom and ball.vel_y < 0:
                ball.y = self.rect.bottom + ball.radius
                ball.vel_y = -ball.vel_y * BOUNCE_FACTOR
                
            # Left collision
            elif ball.x < self.rect.left and ball.vel_x > 0:
                ball.x = self.rect.left - ball.radius
                ball.vel_x = -ball.vel_x * BOUNCE_FACTOR
                
            # Right collision
            elif ball.x > self.rect.right and ball.vel_x < 0:
                ball.x = self.rect.right + ball.radius
                ball.vel_x = -ball.vel_x * BOUNCE_FACTOR

class Goal:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.active = True
    
    def draw(self):
        if self.active:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
    
    def check_collision(self, ball):
        if not self.active:
            return False
        
        distance = math.sqrt((ball.x - self.x)**2 + (ball.y - self.y)**2)
        if distance < ball.radius + self.radius:
            self.active = False
            return True
        return False

class PowerUp:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.radius = 15
        self.type = random.choice(POWERUP_TYPES)
        self.color = POWERUP_COLORS[self.type]
        self.active = True
        self.bob_offset = 0
        self.bob_speed = 0.05
        
    def update(self):
        self.bob_offset = math.sin(pygame.time.get_ticks() * self.bob_speed) * 5
        
    def draw(self):
        if self.active:
            y_pos = self.y + self.bob_offset
            pygame.draw.circle(screen, self.color, (int(self.x), int(y_pos)), self.radius)
            
    def check_collision(self, ball: Ball) -> bool:
        if not self.active:
            return False
            
        distance = math.sqrt((ball.x - self.x)**2 + (ball.y - self.y)**2)
        if distance < ball.radius + self.radius:
            self.active = False
            return True
        return False

class MovingPlatform(Platform):
    def __init__(self, x, y, width, height, color, move_range: int, speed: float, vertical: bool = False):
        super().__init__(x, y, width, height, color)
        self.start_pos = (x, y)
        self.move_range = move_range
        self.speed = speed
        self.vertical = vertical
        self.progress = 0
        
    def update(self):
        self.progress = (self.progress + self.speed) % (2 * math.pi)
        offset = math.sin(self.progress) * self.move_range
        
        if self.vertical:
            self.rect.y = self.start_pos[1] + offset
        else:
            self.rect.x = self.start_pos[0] + offset

# Create game objects
ball = Ball(100, 100, BALL_RADIUS, RED)

# Add this function to create level designs
def create_level(level_number):
    # Level designs
    level_designs = {
        1: {
            'platforms': [
                Platform(100, 400, 200, 20, GREEN),
                MovingPlatform(400, 300, 200, 20, GREEN, 100, 0.02),
                MovingPlatform(600, 500, 150, 20, GREEN, 80, 0.03, True),
                Platform(200, 200, 100, 20, GREEN),
                Platform(500, 150, 100, 20, GREEN)
            ],
            'goals': [
                Goal(150, 380, 10, YELLOW),
                Goal(500, 280, 10, YELLOW),
                Goal(700, 480, 10, YELLOW),
                Goal(250, 180, 10, YELLOW),
                Goal(550, 130, 10, YELLOW)
            ],
            'powerups': [
                PowerUp(300, 250),
                PowerUp(450, 400),
                PowerUp(650, 200)
            ]
        },
        2: {
            'platforms': [
                Platform(50, 450, 150, 20, GREEN),
                MovingPlatform(300, 350, 150, 20, GREEN, 120, 0.03),
                Platform(550, 300, 200, 20, GREEN),
                MovingPlatform(200, 250, 100, 20, GREEN, 80, 0.02, True),
                Platform(400, 180, 150, 20, GREEN),
                MovingPlatform(650, 400, 100, 20, GREEN, 100, 0.04, True)
            ],
            'goals': [
                Goal(100, 430, 10, YELLOW),
                Goal(350, 330, 10, YELLOW),
                Goal(650, 280, 10, YELLOW),
                Goal(220, 230, 10, YELLOW),
                Goal(450, 160, 10, YELLOW),
                Goal(700, 380, 10, YELLOW)
            ],
            'powerups': [
                PowerUp(250, 300),
                PowerUp(500, 250),
                PowerUp(350, 150),
                PowerUp(600, 400)
            ]
        },
        3: {
            'platforms': [
                Platform(100, 500, 100, 20, GREEN),
                Platform(250, 450, 100, 20, GREEN),
                MovingPlatform(400, 400, 100, 20, GREEN, 70, 0.03),
                MovingPlatform(250, 350, 100, 20, GREEN, 70, 0.02, True),
                Platform(400, 300, 100, 20, GREEN),
                MovingPlatform(550, 250, 100, 20, GREEN, 70, 0.025),
                Platform(400, 200, 100, 20, GREEN),
                MovingPlatform(250, 150, 100, 20, GREEN, 70, 0.035, True),
                Platform(100, 100, 100, 20, GREEN)
            ],
            'goals': [
                Goal(130, 480, 10, YELLOW),
                Goal(280, 430, 10, YELLOW),
                Goal(430, 380, 10, YELLOW),
                Goal(280, 330, 10, YELLOW),
                Goal(430, 280, 10, YELLOW),
                Goal(580, 230, 10, YELLOW),
                Goal(430, 180, 10, YELLOW),
                Goal(280, 130, 10, YELLOW),
                Goal(130, 80, 10, YELLOW)
            ],
            'powerups': [
                PowerUp(200, 450),
                PowerUp(350, 350),
                PowerUp(500, 250),
                PowerUp(350, 150),
                PowerUp(200, 50)
            ]
        }
    }
    
    # Return the design for the specified level or the last level if beyond available designs
    if level_number <= len(level_designs):
        return level_designs[level_number]
    else:
        # For levels beyond the defined ones, create a random level
        return create_random_level(level_number)

def create_random_level(level_number):
    # More challenging random level based on level number
    platforms = []
    goals = []
    powerups = []
    
    # Add some platforms with increasing complexity
    num_platforms = min(5 + level_number, 15)  # More platforms for higher levels
    platform_speed = 0.02 + (level_number * 0.005)  # Faster movement in higher levels
    
    for i in range(num_platforms):
        is_moving = random.random() < 0.5 + (level_number * 0.05)  # More likely to be moving in higher levels
        is_vertical = random.random() < 0.4
        x = random.randint(50, WINDOW_WIDTH - 150)
        y = 100 + (i * (WINDOW_HEIGHT - 200) // num_platforms)
        width = random.randint(80, 200)
        
        if is_moving:
            move_range = random.randint(50, 150)
            if is_vertical:
                platforms.append(MovingPlatform(x, y, width, 20, GREEN, move_range, platform_speed, True))
            else:
                platforms.append(MovingPlatform(x, y, width, 20, GREEN, move_range, platform_speed, False))
        else:
            platforms.append(Platform(x, y, width, 20, GREEN))
            
        # Add a goal for each platform
        goal_x = x + random.randint(20, width - 20)
        goal_y = y - 20
        goals.append(Goal(goal_x, goal_y, 10, YELLOW))
    
    # Add powerups
    num_powerups = min(3 + level_number // 2, 7)
    for _ in range(num_powerups):
        x = random.randint(50, WINDOW_WIDTH - 50)
        y = random.randint(50, WINDOW_HEIGHT - 100)
        powerups.append(PowerUp(x, y))
    
    return {
        'platforms': platforms,
        'goals': goals,
        'powerups': powerups
    }

# Replace the platform, goal, and powerup creation with the load_level function call
def load_level(level_number):
    level_data = create_level(level_number)
    return level_data['platforms'], level_data['goals'], level_data['powerups']

# Game variables
current_level = 1  # Define current_level before using it
score = 0
game_active = True
level_complete = False
level_start_time = pygame.time.get_ticks()

# Initial level loading (at the start of the game)
platforms, goals, powerups = load_level(current_level)

# Text rendering function
def draw_text(text, size, x, y, color=WHITE):
    font = pygame.font.SysFont('Arial', size, bold=True)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    
    # Draw a background rectangle
    bg_rect = text_rect.inflate(20, 10)
    pygame.draw.rect(screen, BLACK, bg_rect)
    pygame.draw.rect(screen, WHITE, bg_rect, 2)
    
    screen.blit(text_surface, text_rect)

# Add a start menu
def start_menu():
    while True:
        screen.fill(BLACK)
        draw_text("Ball Physics Game", 48, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)
        draw_text("Press Enter to Start", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_RETURN:
                return

# Call start_menu() before the main game loop
start_menu()

# Main game loop
while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        
        # Jump if spacebar is pressed and ball is on ground
        if event.type == KEYDOWN:
            if event.key == K_SPACE and ball.on_ground:
                ball.vel_y = -12
                ball.on_ground = False
            
            # Reset level if R key is pressed
            if event.key == K_r:
                current_level = 1
                score = 0
                ball = Ball(100, 100, BALL_RADIUS, RED)
                
                # Reset to level 1
                platforms, goals, powerups = load_level(current_level)
                
                level_start_time = pygame.time.get_ticks()
                level_complete = False
                game_active = True
    
    # Get keyboard input for ball movement
    keys = pygame.key.get_pressed()
    if keys[K_LEFT]:
        ball.vel_x -= 0.5
    if keys[K_RIGHT]:
        ball.vel_x += 0.5
    
    # Update game state
    if game_active and not level_complete:
        ball.update()
        ball.update_powerups()
        ball.update_particles()
        
        # Add particles when moving
        if abs(ball.vel_x) > 1 or abs(ball.vel_y) > 1:
            ball.add_particles(1)
        
        # Update moving platforms
        for platform in platforms:
            if isinstance(platform, MovingPlatform):
                platform.update()
            platform.check_collision(ball)
        
        # Check powerup collisions
        for powerup in powerups:
            powerup.update()
            if powerup.check_collision(ball):
                ball.apply_powerup(powerup.type)
                ball.add_particles(20)  # Burst of particles on collection
        
        # Check goal collisions
        goals_active = False
        for goal in goals:
            if goal.check_collision(ball):
                score += 10
            if goal.active:
                goals_active = True
        
        # Check if level is complete
        if not goals_active:
            level_complete = True
            level_complete_time = pygame.time.get_ticks()
    
    # Check if ball falls off screen
    if ball.y > WINDOW_HEIGHT + 100:
        game_active = False
    
    # Draw everything
    screen.fill((30, 30, 30))  # Use a dark gray color as a placeholder
    
    # Draw platforms
    for platform in platforms:
        platform.draw()
    
    # Draw goals
    for goal in goals:
        goal.draw()
    
    # Draw power-ups
    for powerup in powerups:
        powerup.draw()
    
    # Draw ball
    ball.draw()
    
    # Draw particles
    ball.draw_particles()
    
    # Draw HUD
    draw_text(f"Score: {score}", 24, 700, 30)
    draw_text(f"Level: {current_level}", 24, 700, 60)
    
    if not game_active:
        draw_text("Game Over! Press R to restart", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    
    if level_complete:
        # Show level complete message for 3 seconds
        if pygame.time.get_ticks() - level_complete_time < 3000:
            draw_text("Level Complete!", 36, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        else:
            # Reset for next level
            current_level += 1
            ball = Ball(100, 100, BALL_RADIUS, RED)
            
            # Load new level layout
            platforms, goals, powerups = load_level(current_level)
            
            level_start_time = pygame.time.get_ticks()
            level_complete = False
    
    # Update the display
    pygame.display.flip()
    clock.tick(FPS)