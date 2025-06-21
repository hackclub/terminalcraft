#!/usr/bin/env python3
import curses
import random
import time
import math
import os
class Particle:
    """A particle in a firework explosion."""
    def __init__(self, x, y, angle, speed, color, char='*', lifespan=20):
        self.x = x
        self.y = y
        self.angle = angle  
        self.speed = speed
        self.color = color
        self.char = char
        self.lifespan = lifespan
        self.age = 0
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.gravity = 0.05
    def update(self):
        """Update the particle's position and age."""
        self.x += self.dx
        self.y += self.dy
        self.dy += self.gravity  
        self.age += 1
        self.dx *= 0.97
        self.dy *= 0.97
        return self.age <= self.lifespan
    def draw(self, screen, height, width):
        """Draw the particle on the screen."""
        screen_x = int(self.x)
        screen_y = int(self.y)
        if 0 <= screen_x < width and 0 <= screen_y < height:
            brightness = 1.0 - (self.age / self.lifespan)
            if brightness > 0.7:
                attr = curses.A_BOLD
            elif brightness > 0.3:
                attr = curses.A_NORMAL
            else:
                attr = curses.A_DIM
            try:
                screen.addch(screen_y, screen_x, self.char, 
                           curses.color_pair(self.color) | attr)
            except curses.error:
                pass
class Firework:
    """A firework that explodes into particles."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = random.randint(width // 4, width * 3 // 4)
        self.y = height - 1
        self.target_y = random.randint(height // 8, height // 2)
        self.speed = random.uniform(0.3, 0.7)
        self.particles = []
        self.exploded = False
        self.color = random.randint(1, 7)  
    def update(self):
        """Update the firework's position and particles."""
        if not self.exploded:
            self.y -= self.speed
            if self.y <= self.target_y:
                self.explode()
        else:
            self.particles = [p for p in self.particles if p.update()]
        return self.exploded and not self.particles
    def explode(self):
        """Create an explosion of particles."""
        self.exploded = True
        num_particles = random.randint(20, 40)
        for i in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.3, 1.2)
            char = random.choice(['*', '+', '.', '•', '°'])
            lifespan = random.randint(15, 30)
            self.particles.append(Particle(
                self.x, self.y, angle, speed, self.color, char, lifespan
            ))
    def draw(self, screen):
        """Draw the firework on the screen."""
        if not self.exploded:
            try:
                screen.addch(int(self.y), int(self.x), '|', 
                           curses.color_pair(self.color) | curses.A_BOLD)
            except curses.error:
                pass
        else:
            for particle in self.particles:
                particle.draw(screen, self.height, self.width)
def initialize_screen():
    """Initialize the curses screen."""
    screen = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    colors = [curses.COLOR_RED, curses.COLOR_GREEN, curses.COLOR_YELLOW, 
              curses.COLOR_BLUE, curses.COLOR_MAGENTA, curses.COLOR_CYAN, 
              curses.COLOR_WHITE]
    for i, color in enumerate(colors, start=1):
        curses.init_pair(i, color, curses.COLOR_BLACK)
    curses.curs_set(0)  
    curses.noecho()
    curses.cbreak()
    screen.keypad(True)
    screen.timeout(50)  
    return screen
def cleanup_screen(screen):
    """Clean up the curses screen."""
    screen.keypad(False)
    curses.nocbreak()
    curses.echo()
    curses.endwin()
def get_terminal_size():
    """Get the terminal size."""
    return os.get_terminal_size()
def draw_ground(screen, height, width):
    """Draw the ground at the bottom of the screen."""
    for x in range(width):
        try:
            screen.addch(height - 1, x, '_', curses.color_pair(7))
        except curses.error:
            pass
def draw_stars(screen, height, width, num_stars=50):
    """Draw background stars."""
    for _ in range(num_stars):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 2)  
        char = random.choice(['.', '*', '+'])
        attr = random.choice([curses.A_DIM, curses.A_NORMAL])
        try:
            screen.addch(y, x, char, curses.color_pair(7) | attr)
        except curses.error:
            pass
def draw_info(screen, height, width, fireworks_count, launch_rate):
    """Draw information about the simulation."""
    info_text = [
        f"Fireworks: {fireworks_count} | Launch Rate: {launch_rate:.2f}/s",
        "Controls: Space=launch, +/-=rate, q=quit"
    ]
    for i, text in enumerate(info_text):
        try:
            screen.addstr(i, 0, text, curses.color_pair(7) | curses.A_BOLD)
        except curses.error:
            pass
def main(screen):
    """Main function."""
    try:
        width, height = get_terminal_size()
        width = min(width, 80)  
        height = min(height, 24)  
        fireworks = []
        launch_rate = 0.5  
        last_launch = time.time()
        running = True
        while running:
            screen.clear()
            draw_stars(screen, height, width)
            draw_ground(screen, height, width)
            current_time = time.time()
            if current_time - last_launch > 1.0 / launch_rate:
                fireworks.append(Firework(width, height))
                last_launch = current_time
            fireworks = [fw for fw in fireworks if not fw.update()]
            for firework in fireworks:
                firework.draw(screen)
            draw_info(screen, height, width, len(fireworks), launch_rate)
            screen.refresh()
            key = screen.getch()
            if key == ord('q'):
                running = False
            elif key == ord(' '):
                fireworks.append(Firework(width, height))
            elif key == ord('+') or key == ord('='):
                launch_rate = min(2.0, launch_rate + 0.1)  
            elif key == ord('-'):
                launch_rate = max(0.1, launch_rate - 0.1)  
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup_screen(screen)
if __name__ == "__main__":
    curses.wrapper(main)