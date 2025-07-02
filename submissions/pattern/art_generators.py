import time
import random
import math
from abc import ABC, abstractmethod
from rich.live import Live
from rich.text import Text
import numpy as np
from scipy.spatial import cKDTree
import colorsys
class BaseGenerator(ABC):
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
    @abstractmethod
    def run(self):
        """
        This method should contain the main loop for the art generation
        and should handle KeyboardInterrupt to exit gracefully.
        """
        pass
class MatrixGenerator(BaseGenerator):
    def __init__(self, width: int, height: int, speed: float = 0.05, tail_length: int = 15):
        super().__init__(width, height)
        self.speed = speed
        self.tail_length = tail_length
        self.columns = [0] * self.width
        self.characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    def generate_frame(self):
        text = Text()
        grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        for i in range(self.width):
            if self.columns[i] > 0:
                head_y = self.columns[i] - 1
                if 0 <= head_y < self.height:
                    grid[head_y][i] = random.choice(self.characters)
                for j in range(1, self.tail_length):
                    tail_y = head_y - j
                    if 0 <= tail_y < self.height:
                        if grid[tail_y][i] == ' ':
                            grid[tail_y][i] = random.choice(self.characters)
                erase_y = head_y - self.tail_length
                if 0 <= erase_y < self.height:
                    grid[erase_y][i] = ' '
            if self.columns[i] > 0:
                self.columns[i] += 1
            if self.columns[i] > self.height + self.tail_length:
                self.columns[i] = 0
            elif self.columns[i] == 0 and random.random() < 0.02:
                self.columns[i] = 1
        for y in range(self.height):
            for x in range(self.width):
                char = grid[y][x]
                if char != ' ':
                    is_head = (self.columns[x] > 0 and y == self.columns[x] - 1)
                    style = "bold bright_green" if is_head else "green"
                    text.append(char, style=style)
                else:
                    text.append(' ')
            if y < self.height - 1:
                text.append("\n")
        return text
    def run(self):
        try:
            with Live(self.generate_frame(), screen=True, transient=True, refresh_per_second=20) as live:
                while True:
                    time.sleep(self.speed)
                    live.update(self.generate_frame())
        except KeyboardInterrupt:
            pass
class MandelbrotGenerator(BaseGenerator):
    """Generates a continuous zoom into the Mandelbrot set with smooth coloring."""
    def __init__(self, width: int, height: int, max_iter=50, zoom_speed=0.97):
        super().__init__(width, height)
        self.max_iter = max_iter
        self.zoom_speed = zoom_speed
        self.hotspots = [
            (-0.743643887037151, 0.131825904205330), 
            (-1.7499, 0.0), 
            (0.285, 0.01), 
            (-0.8, 0.156), 
            (-0.7269, 0.1889), 
            (0.45, 0.1428) 
        ]
        self.color_palettes = [
            [(0, 7, 100), (32, 107, 203), (237, 255, 255), (255, 170, 0), (0, 2, 0)],
            [(255,0,0), (255,255,0), (0,255,0), (0,255,255), (0,0,255), (255,0,255)],
            [(0,0,0), (255,255,255), (0,0,0)],
        ]
        self.current_palette_index = 0
        self.current_hotspot_index = 0
        self.cx, self.cy = self.hotspots[self.current_hotspot_index]
        self.zoom = 2.0
    def _interpolate_color(self, v, palette):
        v = v % 1
        idx = int(v * (len(palette) - 1))
        frac = v * (len(palette) - 1) - idx
        c1 = palette[idx]
        c2 = palette[idx + 1]
        r = int(c1[0] + (c2[0] - c1[0]) * frac)
        g = int(c1[1] + (c2[1] - c1[1]) * frac)
        b = int(c1[2] + (c2[2] - c1[2]) * frac)
        return f"#{r:02x}{g:02x}{b:02x}"
    def generate_frame(self) -> Text:
        text = Text(no_wrap=True)
        self.zoom *= self.zoom_speed
        if self.zoom < 1e-9:
            self.current_hotspot_index = (self.current_hotspot_index + 1) % len(self.hotspots)
            self.current_palette_index = (self.current_palette_index + 1) % len(self.color_palettes)
            self.cx, self.cy = self.hotspots[self.current_hotspot_index]
            self.zoom = 2.0
        x = np.linspace(self.cx - self.zoom, self.cx + self.zoom, self.width)
        y = np.linspace(self.cy - self.zoom * (self.height / self.width), self.cy + self.zoom * (self.height / self.width), self.height)
        c = x[:, np.newaxis] + 1j * y[np.newaxis, :]
        z = np.zeros_like(c)
        m = np.full(c.shape, self.max_iter, dtype=float)
        for i in range(self.max_iter):
            z = z*z + c
            escaped = np.abs(z) > 2
            mask = escaped & (m == self.max_iter)
            log_zn = np.log(np.abs(z[mask]))
            nu = np.log(log_zn / np.log(2)) / np.log(2)
            m[mask] = i + 1 - nu
            z[escaped] = 2 
        palette = self.color_palettes[self.current_palette_index]
        for row in m.T:
            for val in row:
                if val == self.max_iter:
                    color = "#000000"
                else:
                    color = self._interpolate_color(val / self.max_iter, palette)
                text.append('█', style=color)
            text.append('\n')
        return text
    def run(self):
        try:
            with Live(self.generate_frame(), screen=True, transient=True, refresh_per_second=10) as live:
                while True:
                    live.update(self.generate_frame())
        except KeyboardInterrupt:
            pass
class DigitalRainGenerator(BaseGenerator):
    """A Matrix-style animation with layered, fading Katakana characters."""
    class Droplet:
        def __init__(self, x, height, is_foreground):
            self.x = x
            self.y = random.uniform(-height, 0)
            self.is_foreground = is_foreground
            self.speed = random.uniform(4, 10) if is_foreground else random.uniform(1, 5)
            self.length = random.randint(10, height - 5)
            self.katakana = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
            self.characters = [random.choice(self.katakana) for _ in range(self.length)]
        def update(self, dt):
            self.y += self.speed * dt
    def __init__(self, width: int, height: int, num_droplets=100):
        super().__init__(width, height)
        self.droplets = []
        for i in range(num_droplets):
            x = random.randint(0, width - 1)
            self.droplets.append(self.Droplet(x, height, is_foreground=i < (num_droplets // 2)))
        self.last_time = time.time()
    def generate_frame(self) -> Text:
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        grid = [[(' ', None) for _ in range(self.width)] for _ in range(self.height)]
        for droplet in sorted(self.droplets, key=lambda d: d.is_foreground):
            droplet.update(dt)
            if droplet.y - droplet.length > self.height:
                droplet.y = random.uniform(-droplet.length, 0)
            for i in range(droplet.length):
                y = int(droplet.y - i)
                if 0 <= y < self.height:
                    if random.random() < 0.05:
                        droplet.characters[i] = random.choice(droplet.katakana)
                    char = droplet.characters[i]
                    life_ratio = i / droplet.length
                    if droplet.is_foreground:
                        if i == 0:
                            style = "bold bright_white"
                        elif life_ratio < 0.3:
                            style = "bright_green"
                        elif life_ratio < 0.7:
                            style = "green"
                        else:
                            style = "dark_green"
                    else: 
                        if life_ratio < 0.5:
                            style = "green"
                        else:
                            style = "dark_green"
                    grid[y][droplet.x] = (char, style)
        text = Text(no_wrap=True)
        for y in range(self.height):
            for x in range(self.width):
                char, style = grid[y][x]
                if style:
                    text.append(char, style=style)
                else:
                    text.append(' ')
            if y < self.height - 1:
                text.append('\n')
        return text
    def run(self):
        try:
            with Live(self.generate_frame(), screen=True, transient=True, refresh_per_second=30) as live:
                while True:
                    live.update(self.generate_frame())
        except KeyboardInterrupt:
            pass
class VoronoiGenerator(BaseGenerator):
    """An animated diagram where cells dynamically shift and change with gradients."""
    class Seed:
        def __init__(self, width, height):
            self.x = random.uniform(0, width)
            self.y = random.uniform(0, height)
            self.vx = random.uniform(-3, 3)
            self.vy = random.uniform(-1.5, 1.5)
            self.base_r = random.randint(64, 200)
            self.base_g = random.randint(64, 200)
            self.base_b = random.randint(64, 200)
            self.color = f"#{self.base_r:02x}{self.base_g:02x}{self.base_b:02x}"
            self.phase = random.uniform(0, 2 * math.pi)
            self.pulsation_speed = random.uniform(1, 3)
        def update(self, dt, width, height):
            self.x += self.vx * dt * 10
            self.y += self.vy * dt * 10
            if self.x <= 0: self.x = 0; self.vx *= -1
            elif self.x >= width: self.x = width - 1; self.vx *= -1
            if self.y <= 0: self.y = 0; self.vy *= -1
            elif self.y >= height: self.y = height - 1; self.vy *= -1
            self.phase += dt * self.pulsation_speed
            brightness = (math.sin(self.phase) + 1) / 2  
            brightness = 0.5 + brightness * 0.5  
            r = int(self.base_r * brightness)
            g = int(self.base_g * brightness)
            b = int(self.base_b * brightness)
            self.color = f"#{r:02x}{g:02x}{b:02x}"
    def __init__(self, width: int, height: int, num_seeds=20):
        super().__init__(width, height)
        self.seeds = [self.Seed(width, height) for _ in range(num_seeds)]
        self.last_time = time.time()
        x_coords = np.arange(self.width)
        y_coords = np.arange(self.height)
        self.grid = np.dstack(np.meshgrid(x_coords, y_coords)).reshape(-1, 2)
    def generate_frame(self) -> Text:
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        for seed in self.seeds:
            seed.update(dt, self.width, self.height)
        seed_positions = np.array([[s.x, s.y] for s in self.seeds])
        tree = cKDTree(seed_positions)
        dist, indices = tree.query(self.grid, k=1)
        indices_grid = indices.reshape(self.height, self.width)
        dist_grid = dist.reshape(self.height, self.width)
        char_grid = [['█' for _ in range(self.width)] for _ in range(self.height)]
        style_grid = [['' for _ in range(self.width)] for _ in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                seed_index = indices_grid[y, x]
                seed = self.seeds[seed_index]
                distance = dist_grid[y, x]
                brightness = max(0.1, 1.0 - distance / 25.0)
                r, g, b = int(seed.color[1:3], 16), int(seed.color[3:5], 16), int(seed.color[5:7], 16)
                r = min(255, int(r * brightness))
                g = min(255, int(g * brightness))
                b = min(255, int(b * brightness))
                style_grid[y][x] = f"#{r:02x}{g:02x}{b:02x}"
        for seed in self.seeds:
            sx, sy = int(seed.x), int(seed.y)
            if 0 <= sx < self.width and 0 <= sy < self.height:
                char_grid[sy][sx] = 'o'
                style_grid[sy][sx] = "bold bright_white"
        text = Text(no_wrap=True)
        for y in range(self.height):
            for x in range(self.width):
                text.append(char_grid[y][x], style=style_grid[y][x])
            if y < self.height - 1:
                text.append('\n')
        return text
    def run(self):
        try:
            with Live(self.generate_frame(), screen=True, transient=True, refresh_per_second=30) as live:
                while True:
                    live.update(self.generate_frame())
        except KeyboardInterrupt:
            pass
class KaleidoscopeGenerator(BaseGenerator):
    """A simulation of a kaleidoscope with reflecting, fading, color-cycling particles."""
    class Particle:
        def __init__(self, width, height):
            self.quadrant_width = width // 2
            self.quadrant_height = height // 2
            self.x = random.uniform(0, self.quadrant_width)
            self.y = random.uniform(0, self.quadrant_height)
            self.vx = random.uniform(-5, 5)
            self.vy = random.uniform(-2.5, 2.5)
            self.char = random.choice(['*', '•', 'o', '·', '+'])
            self.hue = random.random()
            self.color_speed = random.uniform(0.05, 0.2)
        def update(self, dt):
            self.x += self.vx * dt
            self.y += self.vy * dt
            self.hue = (self.hue + dt * self.color_speed) % 1.0
            if self.x <= 0: self.x = 0; self.vx *= -1
            elif self.x >= self.quadrant_width - 1: self.x = self.quadrant_width - 1; self.vx *= -1
            if self.y <= 0: self.y = 0; self.vy *= -1
            elif self.y >= self.quadrant_height - 1: self.y = self.quadrant_height - 1; self.vy *= -1
    def __init__(self, width: int, height: int, num_particles=25, trail_length=15):
        super().__init__(width, height)
        self.particles = [self.Particle(width, height) for _ in range(num_particles)]
        self.trail_length = trail_length
        self.grid = [[(' ', 0.0, 0) for _ in range(width)] for _ in range(height)]
        self.last_time = time.time()
    def generate_frame(self) -> Text:
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        for y in range(self.height):
            for x in range(self.width):
                char, hue, life = self.grid[y][x]
                if life > 0:
                    self.grid[y][x] = (char, hue, life - 1)
        for p in self.particles:
            p.update(dt)
            w2 = self.width - 1
            h2 = self.height - 1
            px, py = int(p.x), int(p.y)
            points = [
                (px, py), (w2 - px, py),
                (px, h2 - py), (w2 - px, h2 - py)
            ]
            for x, y in points:
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.grid[y][x] = (p.char, p.hue, self.trail_length)
        text = Text(no_wrap=True)
        for y in range(self.height):
            for x in range(self.width):
                char, hue, life = self.grid[y][x]
                if life > 0:
                    brightness = life / self.trail_length
                    rgb = colorsys.hls_to_rgb(hue, 0.5 * brightness + 0.2, 1.0)
                    color = f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"
                    text.append(char, style=color)
                else:
                    text.append(' ')
            if y < self.height - 1:
                text.append('\n')
        return text
    def run(self):
        try:
            with Live(self.generate_frame(), screen=True, transient=True, refresh_per_second=45) as live:
                while True:
                    live.update(self.generate_frame())
        except KeyboardInterrupt:
            pass
class DayNightCycleGenerator(BaseGenerator):
    """A simulation of a day-to-night transition with sun, moon, and stars."""
    def __init__(self, width: int, height: int, cycle_speed=0.05):
        super().__init__(width, height)
        self.cycle_speed = cycle_speed
        self.time_of_day = 0.0  
        self.sky_colors = [
            (0.0, (5, 5, 20)),      
            (0.2, (25, 25, 80)),    
            (0.3, (255, 150, 50)),  
            (0.4, (100, 150, 255)), 
            (0.5, (135, 206, 250)), 
            (0.6, (100, 150, 255)), 
            (0.7, (255, 150, 50)),  
            (0.8, (25, 25, 80)),    
            (1.0, (5, 5, 20)),      
        ]
        self.stars = [
            (random.randint(0, width-1), random.randint(0, int(height*0.8)), random.uniform(0.1, 1.0))
            for _ in range(100)
        ]
        self.last_time = time.time()
    def _interpolate_rgb(self, t, c1, c2):
        return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))
    def get_sky_color(self, time_of_day):
        for i in range(len(self.sky_colors) - 1):
            t1, c1 = self.sky_colors[i]
            t2, c2 = self.sky_colors[i+1]
            if t1 <= time_of_day < t2:
                segment_t = (time_of_day - t1) / (t2 - t1)
                return self._interpolate_rgb(segment_t, c1, c2)
        return self.sky_colors[-1][1]
    def generate_frame(self) -> Text:
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        self.time_of_day = (self.time_of_day + dt * self.cycle_speed) % 1.0
        grid = [[(' ', '') for _ in range(self.width)] for _ in range(self.height)]
        sky_base_color = self.get_sky_color(self.time_of_day)
        for y in range(self.height):
            brightness = 0.7 + 0.3 * (y / self.height)
            r = int(sky_base_color[0] * brightness)
            g = int(sky_base_color[1] * brightness)
            b = int(sky_base_color[2] * brightness)
            color = f"#{r:02x}{g:02x}{b:02x}"
            for x in range(self.width):
                grid[y][x] = ('█', color)
        sky_angle = self.time_of_day * 2 * math.pi
        sun_y_norm = math.sin(sky_angle)
        if sun_y_norm < 0.1: 
            for x, y, brightness in self.stars:
                if random.random() < 0.005: 
                    continue
                star_brightness = int(150 + 105 * brightness * abs(sun_y_norm))
                color = f"rgb({star_brightness},{star_brightness},{star_brightness})"
                grid[y][x] = ('.', color)
        celestial_x = int((self.width / 2) + (self.width * 0.45) * math.cos(sky_angle))
        celestial_y = int((self.height * 0.8) - (self.height * 0.7) * sun_y_norm)
        if sun_y_norm > 0: 
            if 0 <= celestial_y < self.height and 0 <= celestial_x < self.width:
                grid[celestial_y][celestial_x] = ('●', 'yellow')
        else: 
            if 0 <= celestial_y < self.height and 0 <= celestial_x < self.width:
                grid[celestial_y][celestial_x] = ('○', 'bright_white')
        text = Text(no_wrap=True)
        for y in range(self.height):
            for x in range(self.width):
                char, style = grid[y][x]
                text.append(char, style=style)
            if y < self.height - 1:
                text.append('\n')
        return text
    def run(self):
        try:
            with Live(self.generate_frame(), screen=True, transient=True, refresh_per_second=20) as live:
                while True:
                    live.update(self.generate_frame())
        except KeyboardInterrupt:
            pass
class ForestSimulationGenerator(BaseGenerator):
    """A refined, tranquil scene of a forest with swaying trees and falling leaves."""
    class Tree:
        def __init__(self, x, y_base, max_height):
            self.x = x
            self.y_base = y_base
            self.canopy_height = random.randint(int(max_height*0.2), int(max_height*0.5))
            self.trunk_height = self.y_base - self.canopy_height
            self.canopy_width = random.randint(5, 9)
            depth = (self.y_base / max_height)
            trunk_brightness = 0.5 + (depth * 0.5)
            self.trunk_color = f"#{int(139*trunk_brightness):02x}{int(69*trunk_brightness):02x}{int(19*trunk_brightness):02x}"
            leaf_brightness = 0.4 + (depth * 0.6)
            self.leaf_color = f"#{int(34*leaf_brightness):02x}{int(139*leaf_brightness):02x}{int(34*leaf_brightness):02x}"
            self.sway_offset = random.uniform(0, 2 * math.pi)
            self.sway_speed = random.uniform(0.3, 0.8)
            self.sway_amount = random.uniform(0.5, 2.0)
    class Leaf:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.vx = random.uniform(-1.5, 1.5)  
            self.vy = random.uniform(0.8, 2.0)  
            self.char = random.choice(['.', '*'])
            self.color = random.choice(["#DAA520", "#B8860B", "#D2691E"])
            self.life = random.uniform(3, 7)
            self.wave_amplitude = random.uniform(2.0, 5.0)
            self.wave_frequency = random.uniform(0.5, 1.5)
            self.wave_phase = random.uniform(0, 2 * math.pi)
        def update(self, dt):
            self.life -= dt
            wave_effect = math.sin(self.y * self.wave_frequency + self.wave_phase) * self.wave_amplitude * dt
            self.x += self.vx * dt + wave_effect
            self.y += self.vy * dt
    def __init__(self, width: int, height: int, num_trees=15):
        super().__init__(width, height)
        self.leaves = []
        self.last_time = time.time()
        self.time = 0
        trees = []
        min_dist = 3
        for _ in range(num_trees):
            for _ in range(100): 
                x = random.randint(0, width - 1)
                y_base = random.randint(int(height * 0.6), height - 2)
                if all(abs(t.x - x) >= min_dist or abs(t.y_base - y_base) >= int(height*0.1) for t in trees):
                    trees.append(self.Tree(x, y_base, height))
                    break
        self.trees = sorted(trees, key=lambda t: t.y_base) 
    def generate_frame(self) -> Text:
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        self.time += dt
        grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        styles = [['' for _ in range(self.width)] for _ in range(self.height)]
        for x in range(self.width):
            grid[self.height-1][x] = '▀'
            if random.random() < 0.1:
                styles[self.height-1][x] = "#005A00"
            else:
                styles[self.height-1][x] = "#006400"
        for tree in self.trees:
            sway = math.sin(self.time * tree.sway_speed + tree.sway_offset) * tree.sway_amount
            for y in range(tree.trunk_height, tree.y_base):
                if 0 <= tree.x < self.width:
                    grid[y][tree.x] = '┃'
                    styles[y][tree.x] = tree.trunk_color
            for dy in range(tree.canopy_height):
                y = tree.trunk_height + dy
                current_width = int(tree.canopy_width * (1 - (dy / tree.canopy_height) ** 1.5))
                sway_effect = sway * (dy / tree.canopy_height)
                for dx in range(-current_width // 2, current_width // 2 + 1):
                    x = tree.x + dx + int(sway_effect)
                    if 0 <= x < self.width and 0 <= y < self.height -1 and grid[y][x] == ' ':
                        grid[y][x] = 'Y'
                        styles[y][x] = tree.leaf_color
        if random.random() < 0.3:
            tree = random.choice(self.trees)
            spawn_x = tree.x + random.randint(-tree.canopy_width // 2, tree.canopy_width // 2)
            spawn_y = tree.trunk_height + random.randint(0, tree.canopy_height)
            self.leaves.append(self.Leaf(spawn_x, spawn_y))
        for leaf in self.leaves[:]:
            leaf.update(dt)
            if leaf.life <= 0 or leaf.y >= self.height - 1:
                self.leaves.remove(leaf)
                continue
            lx, ly = int(leaf.x), int(leaf.y)
            if 0 <= lx < self.width and 0 <= ly < self.height -1 and grid[ly][lx] == ' ':
                grid[ly][lx] = leaf.char
                styles[ly][lx] = leaf.color
        text = Text(no_wrap=True)
        for y in range(self.height):
            for x in range(self.width):
                text.append(grid[y][x], style=styles[y][x])
            if y < self.height - 1:
                text.append('\n')
        return text
    def run(self):
        try:
            with Live(self.generate_frame(), screen=True, transient=True, refresh_per_second=20) as live:
                while True:
                    live.update(self.generate_frame())
        except KeyboardInterrupt:
            pass
class GameOfLifeGenerator(BaseGenerator):
    """A classic implementation of Conway's Game of Life."""
    def __init__(self, width: int, height: int, density: float = 0.25):
        super().__init__(width, height)
        self.grid_width = width - 1
        self.grid = np.random.choice([0, 1], size=(int(self.height), int(self.grid_width)), p=[1 - density, density])
        self.cell_char = '■'
        self.live_color = "#7CFC00"  
    def generate_frame(self) -> Text:
        new_grid = np.copy(self.grid)
        for r in range(self.height):
            for c in range(self.grid_width):
                live_neighbors = int(
                    self.grid[(r - 1) % self.height, (c - 1) % self.grid_width] +
                    self.grid[(r - 1) % self.height, c] +
                    self.grid[(r - 1) % self.height, (c + 1) % self.grid_width] +
                    self.grid[r, (c - 1) % self.grid_width] +
                    self.grid[r, (c + 1) % self.grid_width] +
                    self.grid[(r + 1) % self.height, (c - 1) % self.grid_width] +
                    self.grid[(r + 1) % self.height, c] +
                    self.grid[(r + 1) % self.height, (c + 1) % self.grid_width]
                )
                if self.grid[r, c] == 1 and (live_neighbors < 2 or live_neighbors > 3):
                    new_grid[r, c] = 0  
                elif self.grid[r, c] == 0 and live_neighbors == 3:
                    new_grid[r, c] = 1  
        self.grid = new_grid
        text_str = ""
        for row in self.grid:
            for cell in row:
                if cell == 1:
                    text_str += self.cell_char
                else:
                    text_str += ' '
            text_str += '\n'
        return Text(text_str.rstrip('\n'), no_wrap=True, style=self.live_color)
    def run(self):
        try:
            with Live(self.generate_frame(), screen=True, transient=True, refresh_per_second=10) as live:
                while True:
                    live.update(self.generate_frame())
        except KeyboardInterrupt:
            pass
class RandomWalkersGenerator(BaseGenerator):
    """A simple simulation of random walkers leaving trails."""
    def __init__(self, width: int, height: int, num_walkers: int = 1):
        super().__init__(width, height)
        self.walkers = []
        for _ in range(num_walkers):
            self.walkers.append({
                "x": self.width // 2,
                "y": self.height // 2,
                "char": "@",
                "color": "white"
            })
        self.grid_chars = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.grid_styles = [['' for _ in range(self.width)] for _ in range(self.height)]
    def generate_frame(self) -> Text:
        for walker in self.walkers:
            walker['x'] += random.choice([-1, 0, 1])
            walker['y'] += random.choice([-1, 0, 1])
            walker['x'] = max(0, min(self.width - 1, walker['x']))
            walker['y'] = max(0, min(self.height - 1, walker['y']))
            self.grid_chars[walker['y']][walker['x']] = walker['char']
            self.grid_styles[walker['y']][walker['x']] = walker['color']
        text = Text(no_wrap=True)
        for y in range(self.height):
            for x in range(self.width):
                text.append(self.grid_chars[y][x], style=self.grid_styles[y][x])
            if y < self.height - 1:
                text.append("\n")
        return text
    def run(self):
        try:
            with Live(self.generate_frame(), screen=True, transient=True, refresh_per_second=30) as live:
                while True:
                    live.update(self.generate_frame())
        except KeyboardInterrupt:
            pass
class RainGenerator(BaseGenerator):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.drops = []
    def generate_frame(self):
        if random.random() < 0.5:
            self.drops.append({'x': random.randint(0, self.width - 1), 'y': 0})
        for drop in self.drops:
            drop['y'] += 1
        self.drops = [drop for drop in self.drops if drop['y'] < self.height]
        grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        for drop in self.drops:
            grid[drop['y']][drop['x']] = '|'
        text = ""
        for row in grid:
            text += "".join(row) + "\n"
        return Text(text.rstrip())
    def run(self):
        try:
            with Live(self.generate_frame(), screen=True, transient=True, refresh_per_second=30) as live:
                while True:
                    live.update(self.generate_frame())
        except KeyboardInterrupt:
            pass
class SpinningCubeGenerator(BaseGenerator):
    """A rotating 3D cube rendered in ASCII characters."""
    def __init__(self, width: int, height: int, size: int = 10, rotation_speed: float = 1.0):
        super().__init__(width, height)
        self.size = size
        self.rotation_speed = rotation_speed
        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0
        self.points = np.array([
            [-1, -1, -1],
            [1, -1, -1],
            [1, 1, -1],
            [-1, 1, -1],
            [-1, -1, 1],
            [1, -1, 1],
            [1, 1, 1],
            [-1, 1, 1]
        ]) * self.size
        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]
    def rotate(self, points, angle_x, angle_y, angle_z):
        rotation_x = np.array([
            [1, 0, 0],
            [0, np.cos(angle_x), -np.sin(angle_x)],
            [0, np.sin(angle_x), np.cos(angle_x)]
        ])
        rotation_y = np.array([
            [np.cos(angle_y), 0, np.sin(angle_y)],
            [0, 1, 0],
            [-np.sin(angle_y), 0, np.cos(angle_y)]
        ])
        rotation_z = np.array([
            [np.cos(angle_z), -np.sin(angle_z), 0],
            [np.sin(angle_z), np.cos(angle_z), 0],
            [0, 0, 1]
        ])
        rotated_points = np.dot(points, rotation_x)
        rotated_points = np.dot(rotated_points, rotation_y)
        rotated_points = np.dot(rotated_points, rotation_z)
        return rotated_points
    def project(self, points):
        projected_points = []
        for p in points:
            distance = 5
            z = 1 / (distance - p[2] / self.size)
            x = int(p[0] * z * 2.5 + self.width / 2)
            y = int(p[1] * z + self.height / 2)
            projected_points.append((x, y))
        return projected_points
    def generate_frame(self) -> Text:
        self.angle_x += 0.01 * self.rotation_speed
        self.angle_y += 0.01 * self.rotation_speed
        self.angle_z += 0.01 * self.rotation_speed
        rotated_points = self.rotate(self.points, self.angle_x, self.angle_y, self.angle_z)
        projected_points = self.project(rotated_points)
        grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        for edge in self.edges:
            p1 = projected_points[edge[0]]
            p2 = projected_points[edge[1]]
            self.draw_line(grid, p1[0], p1[1], p2[0], p2[1])
        text = Text(no_wrap=True)
        for y in range(self.height):
            for x in range(self.width):
                text.append(grid[y][x])
            if y < self.height - 1:
                text.append('\n')
        return text
    def draw_line(self, grid, x1, y1, x2, y2):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        while True:
            if 0 <= x1 < self.width and 0 <= y1 < self.height:
                grid[y1][x1] = '■'
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
    def run(self):
        try:
            with Live(self.generate_frame(), screen=True, transient=True, refresh_per_second=60) as live:
                while True:
                    live.update(self.generate_frame())
        except KeyboardInterrupt:
            pass
class SeaWavesGenerator(BaseGenerator):
    """An improved simulation of ocean waves with a dynamic weather cycle."""
    class Wave:
        def __init__(self, base_amplitude, wavelength, speed, phase):
            self.base_amplitude = base_amplitude
            self.wavelength = wavelength
            self.speed = speed
            self.phase = phase
            self.amplitude = 0 
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self.time = 0
        self.last_time = time.time()
        self.storminess_phase = 0
        self.storminess_speed = 0.1 
        self.waves = [
            self.Wave(self.height * 0.1, self.width * 0.8, 1.0, 0.5),
            self.Wave(self.height * 0.05, self.width * 0.4, 2.0, 1.5),
            self.Wave(self.height * 0.02, self.width * 0.2, 4.0, 2.0),
        ]
        self.foam_particles = [] 
    def _interpolate_color(self, color1, color2, factor):
        return tuple(int(c1 + (c2 - c1) * factor) for c1, c2 in zip(color1, color2))
    def generate_frame(self) -> Text:
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        self.time += dt
        self.storminess_phase += dt * self.storminess_speed
        storminess = (math.sin(self.storminess_phase) + 1) / 2
        for wave in self.waves:
            wave.amplitude = wave.base_amplitude * (0.5 + storminess * 1.5)
        grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        styles = [['' for _ in range(self.width)] for _ in range(self.height)]
        wave_chars = [' ', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        calm_sky = (135, 206, 250) 
        stormy_sky = (70, 80, 90)   
        sky_color = self._interpolate_color(calm_sky, stormy_sky, storminess)
        sky_style = f"rgb({sky_color[0]},{sky_color[1]},{sky_color[2]})"
        for x in range(self.width):
            y_total = self.height * 0.6 
            for wave in self.waves:
                y_total += wave.amplitude * math.sin(
                    (2 * math.pi / wave.wavelength) * x + self.time * wave.speed + wave.phase
                )
            y_int = int(y_total)
            for y in range(y_int):
                if 0 <= y < self.height:
                    styles[y][x] = sky_style
            if 0 <= y_int < self.height:
                for y in range(y_int, self.height):
                    depth_factor = (y - y_int) / (self.height - y_int + 1)
                    calm_water = (0, 105, 148)
                    stormy_water = (25, 45, 70)
                    water_color = self._interpolate_color(calm_water, stormy_water, storminess)
                    r,g,b = self._interpolate_color(water_color, (173, 216, 230), depth_factor * 0.6)
                    styles[y][x] = f"rgb({r},{g},{b})"
                    grid[y][x] = '█'
                char_index = min(7, int((y_total - y_int) * 8))
                grid[y_int][x] = wave_chars[char_index]
                crest_height_factor = 0.4 + (1-storminess) * 0.2
                if y_total < self.height * crest_height_factor:
                    styles[y_int][x] = "bright_white"
                    if random.random() < 0.5 * storminess:
                        self.foam_particles.append([x, y_int, random.uniform(0.5, 2)])
                else:
                    styles[y_int][x] = styles[y_int+1][x] if y_int + 1 < self.height else ""
        for foam in self.foam_particles[:]:
            foam[2] -= dt 
            if foam[2] <= 0:
                self.foam_particles.remove(foam)
                continue
            fx, fy = int(foam[0]), int(foam[1])
            if 0 <= fx < self.width and 0 <= fy < self.height and grid[fy][fx] == ' ':
                grid[fy][fx] = '~'
                styles[fy][fx] = "#FFFFFF"
        text = Text(no_wrap=True)
        for y in range(self.height):
            for x in range(self.width):
                text.append(grid[y][x], style=styles[y][x])
            if y < self.height - 1:
                text.append('\n')
        return text
    def run(self):
        try:
            with Live(self.generate_frame(), screen=True, transient=True, refresh_per_second=30) as live:
                while True:
                    live.update(self.generate_frame())
        except KeyboardInterrupt:
            pass
class Particle:
    """A single particle with position, velocity, and life."""
    def __init__(self, x, y, angle, speed, life):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = life
        self.initial_life = life
        self.char = random.choice(['*', '⁂', '·', '.'])
class ParticleExplosionGenerator(BaseGenerator):
    """Generates rhythmic explosions of particles from the screen's center."""
    def __init__(self, width: int, height: int, gravity: float = 0.08, explosion_rate: float = 1.5):
        super().__init__(width, height)
        self.particles = []
        self.gravity = gravity
        self.explosion_rate = explosion_rate
        self.last_explosion_time = time.time()
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.color_palette = ["bright_white", "yellow", "gold1", "orange1", "dark_orange", "red", "dark_red"]
    def create_explosion(self):
        """Create a burst of new particles from the center."""
        num_particles = random.randint(80, 150)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.5, 2.5) if random.random() > 0.1 else random.uniform(2.5, 5)
            life = random.randint(30, 60)
            self.particles.append(Particle(self.center_x, self.center_y, angle, speed, life))
    def generate_frame(self) -> Text:
        """Update particle physics and generate the text for the next frame."""
        if time.time() - self.last_explosion_time > self.explosion_rate:
            self.create_explosion()
            self.last_explosion_time = time.time()
        grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        for p in self.particles[:]:
            p.x += p.vx
            p.y += p.vy
            p.vy += self.gravity
            p.life -= 1
            if p.life <= 0:
                self.particles.remove(p)
                continue
            if random.random() < 0.1:
                p.char = random.choice(['*', '⁂', '·', '.'])
            px, py = int(p.x), int(p.y)
            if 0 <= px < self.width and 0 <= py < self.height:
                life_ratio = p.life / p.initial_life
                if grid[py][px] is None or life_ratio > grid[py][px][1]:
                    grid[py][px] = (p.char, life_ratio)
        text = Text()
        for y in range(self.height):
            for x in range(self.width):
                cell = grid[y][x]
                if cell:
                    char, life_ratio = cell
                    color_index = min(len(self.color_palette) - 1, int(life_ratio * len(self.color_palette)))
                    style = self.color_palette[color_index]
                    if life_ratio > 0.8:
                        style = f"bold {style}"
                    text.append(char, style=style)
                else:
                    text.append(' ')
            if y < self.height - 1:
                text.append("\n")
        return text
    def run(self):
        self.create_explosion()
        try:
            with Live(self.generate_frame(), screen=True, transient=True, refresh_per_second=30) as live:
                while True:
                    time.sleep(0.03)
                    live.update(self.generate_frame())
        except KeyboardInterrupt:
            pass