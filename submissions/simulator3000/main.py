import curses
import math
import random
import time
import argparse
from enum import Enum

class BoundaryType(Enum):
    REFLECTIVE = 1
    PERIODIC = 2
    INFINITE = 3

class ForceType(Enum):
    GRAVITY = 1
    ELECTROSTATIC = 2
    SPRING = 3
    MAGNETIC = 4
    DRAG = 5

class Particle:
    def __init__(self, x, y, vx=0.0, vy=0.0, mass=1.0, charge=0.0, radius=0.5, color=1):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.vz = 0.0  
        self.ax = 0.0
        self.ay = 0.0
        self.mass = mass
        self.charge = charge
        self.radius = radius
        self.color = color
        self.fixed = False
        self.trails = []
        self.max_trail_length = 20

    def update(self, dt):
        if self.fixed:
            return
            

        self.vx += self.ax * dt
        self.vy += self.ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        self.trails.append((self.x, self.y))
        if len(self.trails) > self.max_trail_length:
            self.trails.pop(0)
        

        self.ax = 0.0
        self.ay = 0.0

    def apply_force(self, fx, fy):
        self.ax += fx / self.mass
        self.ay += fy / self.mass

class ParticleSimulator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.particles = []
        self.springs = []
        self.G = 0.1
        self.k = 5.0
        self.drag_coeff = 0.01
        self.magnetic_field = (0.0, 0.0, 1.0) 
        self.boundary_type = BoundaryType.REFLECTIVE
        self.enabled_forces = {
            ForceType.GRAVITY: True,
            ForceType.ELECTROSTATIC: True,
            ForceType.SPRING: True,
            ForceType.MAGNETIC: True,
            ForceType.DRAG: True
        }
        self.restituition = 0.9
        self.time_scale = 1.0
        self.show_trails = True
        self.show_stats = True
        self.paused = False
        
    def add_particle(self, particle):
        self.particles.append(particle)
        
    def add_spring(self, p1, p2, k, length):
        self.springs.append((p1, p2, k, length))
        
    def apply_boundary_conditions(self):
        for p in self.particles:
            if self.boundary_type == BoundaryType.REFLECTIVE:
                if p.x < p.radius:
                    p.x = p.radius
                    p.vx = -p.vx * self.restituition
                elif p.x > self.width - p.radius:
                    p.x = self.width - p.radius
                    p.vx = -p.vx * self.restituition
                    
                if p.y < p.radius:
                    p.y = p.radius
                    p.vy = -p.vy * self.restituition
                elif p.y > self.height - p.radius:
                    p.y = self.height - p.radius
                    p.vy = -p.vy * self.restituition
                    
            elif self.boundary_type == BoundaryType.PERIODIC:
                if p.x < 0:
                    p.x = self.width
                elif p.x > self.width:
                    p.x = 0
                    
                if p.y < 0:
                    p.y = self.height
                elif p.y > self.height:
                    p.y = 0
    
    def calculate_forces(self):
        for p in self.particles:
            p.ax = 0.0
            p.ay = 0.0
        
        if self.enabled_forces[ForceType.GRAVITY] or self.enabled_forces[ForceType.ELECTROSTATIC]:
            for i, p1 in enumerate(self.particles):
                for p2 in self.particles[i+1:]:
                    dx = p2.x - p1.x
                    dy = p2.y - p1.y
                    r = max(math.sqrt(dx*dx + dy*dy), 0.1)
                    
                    if self.enabled_forces[ForceType.GRAVITY]:
                        f_grav = self.G * p1.mass * p2.mass / (r*r)
                        fx = f_grav * dx / r
                        fy = f_grav * dy / r
                        p1.apply_force(fx, fy)
                        p2.apply_force(-fx, -fy)
                    
                    if self.enabled_forces[ForceType.ELECTROSTATIC] and p1.charge != 0 and p2.charge != 0:
                        f_elec = self.k * p1.charge * p2.charge / (r*r)
                        fx = f_elec * dx / r
                        fy = f_elec * dy / r
                        p1.apply_force(fx, fy)
                        p2.apply_force(-fx, -fy)
        
        if self.enabled_forces[ForceType.SPRING]:
            for p1, p2, k, length in self.springs:
                dx = p2.x - p1.x
                dy = p2.y - p1.y
                r_val = math.sqrt(dx*dx + dy*dy)
                if r_val < 0.01: 
                    r_val = 0.01
                f_spring = k * (r_val - length)
                fx = f_spring * dx / r_val
                fy = f_spring * dy / r_val
                p1.apply_force(fx, fy)
                p2.apply_force(-fx, -fy)
        
        if self.enabled_forces[ForceType.MAGNETIC]:
            Bx, By, Bz = self.magnetic_field
            for p in self.particles:
                if p.charge != 0:
                    fx = p.charge * (p.vy * Bz)  
                    fy = p.charge * (-p.vx * Bz) 
                    p.apply_force(fx, fy)
        
        if self.enabled_forces[ForceType.DRAG]:
            for p in self.particles:
                fx = -self.drag_coeff * p.vx
                fy = -self.drag_coeff * p.vy
                p.apply_force(fx, fy)
    
    def handle_collisions(self):
        for i, p1 in enumerate(self.particles):
            for p2 in self.particles[i+1:]:
                dx = p2.x - p1.x
                dy = p2.y - p1.y
                r = math.sqrt(dx*dx + dy*dy)
                min_dist = p1.radius + p2.radius
                
                if r < min_dist:
                    if r == 0:
                        nx, ny = random.random(), random.random()
                        r = 0.01
                    else:
                        nx, ny = dx/r, dy/r
                    
                    dvx = p2.vx - p1.vx
                    dvy = p2.vy - p1.vy
                    
                    vn = dvx*nx + dvy*ny
                    
                    if vn < 0:  
                        m1, m2 = p1.mass, p2.mass
                        j = -(1 + self.restituition) * vn / (1/m1 + 1/m2)
                        
                        p1.vx -= j * nx / m1
                        p1.vy -= j * ny / m1
                        p2.vx += j * nx / m2
                        p2.vy += j * ny / m2
                        
                        overlap = min_dist - r
                        p1.x -= overlap * nx / 2
                        p1.y -= overlap * ny / 2
                        p2.x += overlap * nx / 2
                        p2.y += overlap * ny / 2
    
    def update(self, dt):
        if self.paused:
            return
            
        self.calculate_forces()
        self.handle_collisions()
        
        for p in self.particles:
            p.update(dt * self.time_scale)
        
        self.apply_boundary_conditions()

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    for i in range(1, 8):
        curses.init_pair(i, i, -1)
    
    stdscr.nodelay(1)
    stdscr.timeout(10)
    
    height, width = stdscr.getmaxyx()
    sim = ParticleSimulator(width, height - 3)  
    
    for _ in range(20):
        x = random.uniform(0, width)
        y = random.uniform(0, height - 3)
        vx = random.uniform(-1, 1)
        vy = random.uniform(-1, 1)
        mass = random.uniform(0.5, 2.0)
        charge = random.choice([-1, 0, 1])
        color = random.randint(1, 7)
        sim.add_particle(Particle(x, y, vx, vy, mass, charge, color=color))
    
    for _ in range(5):
        if len(sim.particles) >= 2:
            p1, p2 = random.sample(sim.particles, 2)
            sim.add_spring(p1, p2, 0.5, math.hypot(p2.x-p1.x, p2.y-p1.y))
    
    status_win = curses.newwin(3, width, height-3, 0)
    
    last_time = time.time()
    while True:
        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key == ord(' '):
            sim.paused = not sim.paused
        elif key == ord('t'):
            sim.show_trails = not sim.show_trails
        elif key == ord('s'):
            sim.show_stats = not sim.show_stats
        elif key == ord('g'):
            sim.enabled_forces[ForceType.GRAVITY] = not sim.enabled_forces[ForceType.GRAVITY]
        elif key == ord('e'):
            sim.enabled_forces[ForceType.ELECTROSTATIC] = not sim.enabled_forces[ForceType.ELECTROSTATIC]
        elif key == ord('d'):
            sim.enabled_forces[ForceType.DRAG] = not sim.enabled_forces[ForceType.DRAG]
        elif key == ord('m'):
            sim.enabled_forces[ForceType.MAGNETIC] = not sim.enabled_forces[ForceType.MAGNETIC]
        elif key == ord('+'):
            sim.time_scale *= 1.1
        elif key == ord('-'):
            sim.time_scale /= 1.1
        elif key == ord('b'):
            current_index = list(BoundaryType).index(sim.boundary_type)
            next_index = (current_index + 1) % len(BoundaryType)
            sim.boundary_type = list(BoundaryType)[next_index]
        elif key == ord('a'):
            x = random.uniform(0, width)
            y = random.uniform(0, height - 3)
            sim.add_particle(Particle(x, y, color=random.randint(1, 7)))
        
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        sim.update(dt)
        
        stdscr.erase()
        for p in sim.particles:
            if sim.show_trails:
                for i, (trail_x, trail_y) in enumerate(p.trails):
                    if 0 <= trail_x < width and 0 <= trail_y < height - 3:
                        intensity = i / len(p.trails) * 7 + 1
                        stdscr.addch(int(trail_y), int(trail_x), '.', curses.color_pair(int(intensity)))
            
            if 0 <= p.x < width and 0 <= p.y < height - 3:
                stdscr.addch(int(p.y), int(p.x), '●', curses.color_pair(p.color))
        
        status_win.erase()
        status = f"Particles: {len(sim.particles)} | "
        status += f"Speed: {sim.time_scale:.1f}x | "
        status += f"Boundary: {sim.boundary_type.name} | "
        status += f"Forces: {'G' if sim.enabled_forces[ForceType.GRAVITY] else '_'}"
        status += f"{'E' if sim.enabled_forces[ForceType.ELECTROSTATIC] else '_'}"
        status += f"{'M' if sim.enabled_forces[ForceType.MAGNETIC] else '_'}"
        status += f"{'D' if sim.enabled_forces[ForceType.DRAG] else '_'}"
        status += f" | {'PAUSED' if sim.paused else 'RUNNING'}"
        
        status_win.addstr(0, 0, status)
        status_win.addstr(1, 0, "Controls: [q]uit [ ]ause [+/-]speed [b]oundary [t]rails [s]tats")
        status_win.addstr(2, 0, "Forces: [g]ravity [e]lectro [m]agnetic [d]rag [a]dd particle")
        status_win.refresh()
        
        stdscr.refresh()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Terminal Particle Simulator')
    parser.add_argument('--gravity', type=float, default=0.1, help='Gravitational constant')
    parser.add_argument('--k', type=float, default=5.0, help='Electrostatic constant')
    parser.add_argument('--drag', type=float, default=0.01, help='Drag coefficient')
    args = parser.parse_args()
    
    curses.wrapper(main)
