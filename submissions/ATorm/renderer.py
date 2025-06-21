import math
import time
from typing import List
from colors import Colors, clear_screen, hide_cursor, show_cursor
from elements import Element, get_electron_shells, get_electron_configuration

class AtomRenderer:
    """Handles rendering of atomic structures"""
    
    def __init__(self, width: int = 100, height: int = 40): # IF USIMG SMALL SCREEN CHANGE THE INT TO 40 [FOR EXAMPLE IN TERMUX IT WOULD START FLICKERIMG when more than 40] 
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
        self.shell_colors = [
            Colors.SHELL_1, Colors.SHELL_2, Colors.SHELL_3, Colors.SHELL_4,
            Colors.SHELL_5, Colors.SHELL_6, Colors.SHELL_7
        ]
        self.frame_buffer = []  # For double buffering
    
    def create_grid(self) -> List[List[str]]:
        """Create empty rendering grid"""
        return [[' ' for _ in range(self.width)] for _ in range(self.height)]
    
    def draw_nucleus(self, grid: List[List[str]], element: Element, time_step: float = 0):
        """Draw simplified animated nucleus for stability"""
        neutrons = round(element.atomic_mass) - element.atomic_number
        nucleus_size = 3
        actual_size = nucleus_size
        
        for dy in range(-int(actual_size), int(actual_size) + 1):
            for dx in range(-int(actual_size), int(actual_size) + 1):
                x = self.center_x + dx
                y = self.center_y + dy
                distance = math.sqrt(dx*dx + dy*dy)
                
                if 0 <= x < self.width and 0 <= y < self.height and distance <= actual_size:
                    if distance <= 1:
                        # Core - simple alternating animation - blue nucleus
                        if int(time_step * 2) % 2 == 0:
                            grid[y][x] = f"{Colors.BLUE}{Colors.BOLD}●{Colors.RESET}"
                        else:
                            grid[y][x] = f"{Colors.BLUE}{Colors.BOLD}◉{Colors.RESET}"
                    elif distance <= 2:
                        # Proton layer - bright blue
                        grid[y][x] = f"{Colors.BRIGHT_BLUE}●{Colors.RESET}"
                    else:
                        # Neutron outer layer - cyan
                        grid[y][x] = f"{Colors.CYAN}●{Colors.RESET}"
    
    def draw_electron_shells_static(self, grid: List[List[str]], element: Element):
        """Draw enhanced static electron shells"""
        shells = get_electron_shells(element.atomic_number)
        
        for shell_idx, electron_count in enumerate(shells):
            color = self.shell_colors[shell_idx] if shell_idx < len(self.shell_colors) else Colors.ELECTRON
            radius = 8 + shell_idx * 4
            
            # shell
            for angle in [i * math.pi / 32 for i in range(64)]:
                x = int(self.center_x + radius * math.cos(angle))
                y = int(self.center_y + radius * math.sin(angle) * 0.85)
                if 0 <= x < self.width and 0 <= y < self.height:
                    if grid[y][x] == ' ':
                        if angle % (math.pi/4) < 0.2:
                            grid[y][x] = f"{color}{Colors.BOLD}·{Colors.RESET}"
                        else:
                            grid[y][x] = f"{color}·{Colors.RESET}"
            
            # electron alt symb
            electron_symbols = ['●', '◉', '⬢', '◆']
            for e in range(electron_count):
                angle = (2 * math.pi * e) / electron_count
                x = int(self.center_x + radius * math.cos(angle))
                y = int(self.center_y + radius * math.sin(angle) * 0.85)
                
                if 0 <= x < self.width and 0 <= y < self.height:
                    # symbol alt
                    symbol_idx = (shell_idx + e) % len(electron_symbols)
                    grid[y][x] = f"{Colors.BRIGHT_WHITE}{Colors.BOLD}{electron_symbols[symbol_idx]}{Colors.RESET}"
    
    def draw_electron_shells_animated(self, grid: List[List[str]], element: Element, time_step: float):
        """Draw animated electron shells with smooth, stable motion"""
        shells = get_electron_shells(element.atomic_number)
        
        for shell_idx, electron_count in enumerate(shells):
            color = self.shell_colors[shell_idx] if shell_idx < len(self.shell_colors) else Colors.ELECTRON
            radius = 8 + shell_idx * 4
            rotation_speed = 1.5 - shell_idx * 0.2  
            actual_radius = radius
            
            # circle
            for angle in [i * math.pi / 24 for i in range(48)]:
                x = int(self.center_x + actual_radius * math.cos(angle))
                y = int(self.center_y + actual_radius * math.sin(angle) * 0.85)
                if 0 <= x < self.width and 0 <= y < self.height:
                    if grid[y][x] == ' ':
                        grid[y][x] = f"{color}·{Colors.RESET}"
            
            # Placing elect
            for e in range(electron_count):
                base_angle = (2 * math.pi * e) / electron_count
                animated_angle = base_angle + time_step * rotation_speed
                
                # e pos
                x = int(self.center_x + actual_radius * math.cos(animated_angle))
                y = int(self.center_y + actual_radius * math.sin(animated_angle) * 0.85)
                
                if 0 <= x < self.width and 0 <= y < self.height:
                    # electrn
                    if int(time_step * 3) % 2 == 0:
                        grid[y][x] = f"{Colors.BRIGHT_WHITE}{Colors.BOLD}●{Colors.RESET}"
                    else:
                        grid[y][x] = f"{Colors.BRIGHT_WHITE}{Colors.BOLD}◉{Colors.RESET}"
                        
                trail_angle = animated_angle - 0.4
                trail_x = int(self.center_x + actual_radius * math.cos(trail_angle))
                trail_y = int(self.center_y + actual_radius * math.sin(trail_angle) * 0.85)
                
                if 0 <= trail_x < self.width and 0 <= trail_y < self.height:
                    if grid[trail_y][trail_x] == ' ':
                        grid[trail_y][trail_x] = f"{Colors.WHITE}{Colors.DIM}·{Colors.RESET}"
    
    def build_frame_buffer(self, element: Element, animated: bool = False, time_step: float = 0):
        """Build complete frame in buffer to reduce flickering"""
        buffer = []
        
        # Header
        mode = "Animated" if animated else "Static"
        if animated:
            
            buffer.append(f"{Colors.INFO}Press Ctrl+C to stop animation{Colors.RESET}")
        else:
            buffer.append(f"{Colors.BOLD}{Colors.HEADER}⚛️  {element.name} ({element.symbol}){Colors.RESET}")
        
        buffer.append("") 
        
        # Create grid
        grid = self.create_grid()
        self.draw_nucleus(grid, element, time_step)
        if animated:
            self.draw_electron_shells_animated(grid, element, time_step)
        else:
            self.draw_electron_shells_static(grid, element)
        
        # Add grid to buffer
        for row in grid:
            buffer.append(''.join(row))
        
        # Footer
        neutrons = round(element.atomic_mass) - element.atomic_number
        shells = get_electron_shells(element.atomic_number)
        electron_config = get_electron_configuration(element.atomic_number)
        
        buffer.append("") 
        buffer.append("") 
        buffer.append(f"{Colors.BOLD}{Colors.HEADER}⚛️  {element.name} ({element.symbol}){Colors.RESET}")
        buffer.append(f"{Colors.INFO}Protons: {Colors.PROTON}{element.atomic_number}{Colors.RESET} | Neutrons: {Colors.NEUTRON}{neutrons}{Colors.RESET} | Electrons: {Colors.ELECTRON}{element.atomic_number}{Colors.RESET}")
        
        # Shell display
        shell_line = f"{Colors.INFO}Shells: {Colors.RESET}"
        for i, count in enumerate(shells):
            color = self.shell_colors[i] if i < len(self.shell_colors) else Colors.ELECTRON
            shell_names = ['K', 'L', 'M', 'N', 'O', 'P', 'Q']
            shell_name = shell_names[i] if i < len(shell_names) else f"S{i+1}"
            shell_line += f"{color}{shell_name}:{count}{Colors.RESET}"
            if i < len(shells) - 1:
                shell_line += " | "
        buffer.append(shell_line)
        
        buffer.append(f"{Colors.INFO}Configuration: {Colors.BRIGHT_YELLOW}{electron_config}{Colors.RESET}")
        buffer.append(f"{Colors.INFO}Category: {Colors.HIGHLIGHT}{element.category}{Colors.RESET}")
        buffer.append(f"{Colors.INFO}Atomic Mass: {Colors.HIGHLIGHT}{element.atomic_mass}{Colors.RESET}")
        
        return buffer
    
    def render_frame_buffer(self, buffer: List[str]):
        """Render complete frame buffer with minimal flickering"""
        # Move to top-left and render entire frame at once
        print("\033[H", end="")
        output = "\n".join(buffer)
        print(output)
        print("\033[J", end="")  # Clear any remaining content
    
    def draw_static_atom(self, element: Element):
        """Draw an enhanced static atom structure"""
        clear_screen()
        buffer = self.build_frame_buffer(element, animated=False)
        self.render_frame_buffer(buffer)
    
    def draw_animated_frame(self, element: Element, time_step: float):
        """Draw a single frame with optimized rendering"""
        buffer = self.build_frame_buffer(element, animated=True, time_step=time_step)
        self.render_frame_buffer(buffer)
    
    def draw_animated_atom(self, element: Element):
        """Draw enhanced animated atom with minimal flickering"""
        print(f"\n{Colors.BOLD}{Colors.HIGHLIGHT}🚀 Initializing atomic visualization...{Colors.RESET}")
        print(f"{Colors.DIM}Press Ctrl+C to stop animation{Colors.RESET}")
        time.sleep(1)
        
        try:
            # Clear screen once and hide cursor
            clear_screen()
            hide_cursor()
            
            time_step = 0
            frame_count = 0
            
            while True:
                self.draw_animated_frame(element, time_step)
                time.sleep(0.12)
                time_step += 0.08
                if time_step > 50:
                    time_step = 0
                    
        except KeyboardInterrupt:
            show_cursor()
            clear_screen()
            print(f"{Colors.INFO}Thank you for exploring the atomic world! ⚛️{Colors.RESET}")
