#!/usr/bin/env python3
"""
Wave on String Simulation - Terminal ASCII Version
A physics simulation of wave propagation on a string with interactive controls.
"""
import numpy as np
import time
import sys
import os
import threading
import queue
from datetime import datetime
import math
try:
    import msvcrt
except ImportError:
    msvcrt = None
from enum import Enum
from dataclasses import dataclass
class WaveMode(Enum):
    MANUAL = "manual"
    OSCILLATE = "oscillate"
    PULSE = "pulse"
class BoundaryCondition(Enum):
    FIXED_END = "fixed"
    LOOSE_END = "loose"
    NO_END = "no_end"
class DampingLevel(Enum):
    NONE = "none"
    LOTS = "lots"
class TensionLevel(Enum):
    LOW = "low"
    HIGH = "high"
@dataclass
class SimulationParams:
    """Parameters for the wave simulation"""
    mode: WaveMode = WaveMode.PULSE
    amplitude: float = 1.25  
    pulse_width: float = 0.50  
    damping: DampingLevel = DampingLevel.NONE
    tension: TensionLevel = TensionLevel.HIGH
    boundary: BoundaryCondition = BoundaryCondition.FIXED_END
    show_rulers: bool = True
    show_timer: bool = True
    show_reference_line: bool = True
    slow_motion: bool = False
    string_length: float = 10.0  
    num_points: int = 80  
    dt: float = 0.01  
class TerminalDisplay:
    """Handle terminal display and input"""
    def __init__(self):
        self.width = 80
        self.height = 25
        self.input_queue = queue.Queue()
        self.input_thread = None
        self.running = False
        self.last_frame = []  
        self.buffer = []      
    def clear_screen(self):
        """Clear the terminal screen with minimal flicker"""
        if os.name == 'nt':
            sys.stdout.write('\033[2J\033[H')
            sys.stdout.flush()
        else:
            sys.stdout.write('\033[2J\033[H')
            sys.stdout.flush()
    def move_cursor_home(self):
        """Move cursor to home position without clearing"""
        sys.stdout.write('\033[H')
        sys.stdout.flush()
    def enable_optimizations(self):
        """Enable terminal optimizations for smoother display"""
        if os.name == 'nt':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                handle = kernel32.GetStdHandle(-11)  
                mode = ctypes.c_ulong()
                kernel32.GetConsoleMode(handle, ctypes.byref(mode))
                mode.value |= 0x0004  
                kernel32.SetConsoleMode(handle, mode)
            except:
                pass
    def render_frame_diff(self, new_frame_lines):
        """Render only the differences between frames to reduce flicker"""
        if not self.last_frame:
            self.move_cursor_home()
            for line in new_frame_lines:
                sys.stdout.write(line + '\n')
            sys.stdout.flush()
            self.last_frame = new_frame_lines[:]
            return
        if len(new_frame_lines) == len(self.last_frame) and all(
            new == old for new, old in zip(new_frame_lines, self.last_frame)
        ):
            return  
        self.move_cursor_home()
        for i, (new_line, old_line) in enumerate(zip(new_frame_lines, self.last_frame)):
            if new_line != old_line:
                sys.stdout.write(f'\033[{i+1};1H')  
                sys.stdout.write('\033[K')  
                sys.stdout.write(new_line)
        if len(new_frame_lines) > len(self.last_frame):
            for i in range(len(self.last_frame), len(new_frame_lines)):
                sys.stdout.write(f'\033[{i+1};1H')
                sys.stdout.write(new_frame_lines[i])
        elif len(new_frame_lines) < len(self.last_frame):
            for i in range(len(new_frame_lines), len(self.last_frame)):
                sys.stdout.write(f'\033[{i+1};1H')
                sys.stdout.write('\033[K')  
        sys.stdout.flush()
        self.last_frame = new_frame_lines[:]
    def hide_cursor(self):
        """Hide the terminal cursor"""
        sys.stdout.write('\033[?25l')
        sys.stdout.flush()
    def show_cursor(self):
        """Show the terminal cursor"""
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()
    def get_input_non_blocking(self):
        """Get keyboard input without blocking"""
        if os.name == 'nt' and msvcrt:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\x00' or key == b'\xe0':  
                    key = msvcrt.getch()  
                    return None  
                try:
                    return key.decode('utf-8', errors='ignore')
                except:
                    return None
        else:
            try:
                import select
                if select.select([sys.stdin], [], [], 0)[0]:
                    return sys.stdin.read(1)
            except:
                pass
        return None
    def start_input_thread(self):
        """Start the input handling thread"""
        self.running = True
        self.input_thread = threading.Thread(target=self._input_worker)
        self.input_thread.daemon = True
        self.input_thread.start()
    def _input_worker(self):
        """Worker thread for handling input"""
        while self.running:
            try:
                key = self.get_input_non_blocking()
                if key:
                    self.input_queue.put(key)
                time.sleep(0.01)
            except:
                break
    def stop_input_thread(self):
        """Stop the input handling thread"""
        self.running = False
        if self.input_thread:
            self.input_thread.join(timeout=0.5)
class WaveSimulation:
    def __init__(self, params: SimulationParams):
        self.params = params
        self.running = False
        self.paused = False
        self.current_time = 0.0
        self.display = TerminalDisplay()
        self._frame_skip_counter = 0
        self._skip_expensive_ops = False
        self._last_energy = 0.0
        self._last_freq = 0.0
        self._calc_counter = 0
        self.x = np.linspace(0, params.string_length, params.num_points)
        self.dx = self.x[1] - self.x[0]
        self.y = np.zeros(params.num_points)  
        self.y_prev = np.zeros(params.num_points)  
        self.y_next = np.zeros(params.num_points)  
        self.wave_speed = 1.5 if params.tension == TensionLevel.HIGH else 0.8
        self.damping_coeff = 0.05 if params.damping == DampingLevel.LOTS else 0.0
        self.manual_amplitude = 0.0
        self.initialize_wave()
    def initialize_wave(self):
        """Initialize the wave with a small starting displacement"""
        if self.params.mode == WaveMode.PULSE:
            for i in range(min(10, len(self.y))):
                x_pos = i / len(self.y)
                initial_pulse = 0.1 * self.params.amplitude * np.exp(-(x_pos * 20) ** 2)
                self.y[i] = initial_pulse
                self.y_prev[i] = initial_pulse
    def generate_source(self) -> float:
        """Generate the source signal based on the mode"""
        if self.params.mode == WaveMode.MANUAL:
            return self.manual_amplitude
        elif self.params.mode == WaveMode.OSCILLATE:
            frequency = 1.0 / (2 * self.params.pulse_width)  
            return self.params.amplitude * np.sin(2 * np.pi * frequency * self.current_time)
        elif self.params.mode == WaveMode.PULSE:
            pulse_duration = self.params.pulse_width * 3  
            if self.current_time <= pulse_duration:
                t_normalized = self.current_time / pulse_duration
                gaussian = np.exp(-((t_normalized - 0.5) / 0.2) ** 2)
                sine_component = np.sin(2 * np.pi * t_normalized * 2)
                return self.params.amplitude * gaussian * sine_component
            else:
                return 0.0
        return 0.0
    def apply_boundary_conditions(self):
        """Apply boundary conditions to the wave"""
        if self.params.boundary == BoundaryCondition.FIXED_END:
            self.y_next[0] = 0
            self.y_next[-1] = 0
        elif self.params.boundary == BoundaryCondition.LOOSE_END:
            self.y_next[0] = self.y_next[1]
            self.y_next[-1] = self.y_next[-2]
        else:  
            if len(self.y) > 2:
                self.y_next[0] = self.y[0] - (self.wave_speed * self.params.dt / self.dx) * (self.y[1] - self.y[0])
                self.y_next[-1] = self.y[-1] - (self.wave_speed * self.params.dt / self.dx) * (self.y[-1] - self.y[-2])
    def update_wave(self):
        """Update the wave using the finite difference method"""
        courant = (self.wave_speed * self.params.dt / self.dx)
        if courant > 0.5:
            self.params.dt = 0.4 * self.dx / self.wave_speed
        for i in range(1, len(self.y) - 1):
            d2y_dx2 = (self.y[i+1] - 2*self.y[i] + self.y[i-1]) / (self.dx**2)
            dy_dt = (self.y[i] - self.y_prev[i]) / self.params.dt
            d2y_dt2 = (self.wave_speed**2) * d2y_dx2 - self.damping_coeff * dy_dt
            self.y_next[i] = (2*self.y[i] - self.y_prev[i] + 
                             (self.params.dt**2) * d2y_dt2)
            self.y_next[i] = np.clip(self.y_next[i], -self.params.amplitude * 3, self.params.amplitude * 3)
        source_amplitude = self.generate_source()
        if self.params.boundary != BoundaryCondition.FIXED_END:
            self.y_next[0] = source_amplitude
        elif source_amplitude != 0:
            if len(self.y) > 5:
                self.y_next[2] = source_amplitude * 0.8
        self.apply_boundary_conditions()
        self.y_prev[:] = self.y[:]
        self.y[:] = self.y_next[:]
    def render_wave(self):
        """Render the wave as ASCII art with smooth curves using dots - optimized version"""
        output = []
        output.append("=" * 80)
        output.append("                    WAVE ON STRING SIMULATION")
        output.append("=" * 80)
        output.append("")
        param_line1 = f"Mode: {self.params.mode.value.upper():<10} "
        param_line1 += f"Amplitude: {self.params.amplitude:>5.2f} "
        param_line1 += f"Pulse Width: {self.params.pulse_width:>5.2f}s"
        param_line2 = f"Damping: {self.params.damping.value.upper():<8} "
        param_line2 += f"Tension: {self.params.tension.value.upper():<6} "
        param_line2 += f"Boundary: {self.params.boundary.value.replace('_', ' ').upper():<10}"
        output.append(param_line1)
        output.append(param_line2)
        output.append("")
        if self.params.show_timer:
            timer_line = f"Time: {self.current_time:6.2f}s"
            if self.paused:
                timer_line += " [PAUSED]"
            output.append(timer_line)
            output.append("")
        wave_height = 15  
        display_width = 65  
        wave_chars = [' ', ',', '.', 'o', '*', '#']  
        zero_char = '-'
        amplitude = self.params.amplitude
        row_spacing = amplitude * 2 / (wave_height - 1)
        threshold_base = amplitude / (wave_height - 1)
        for row in range(wave_height):
            line_parts = []
            if self.params.show_rulers:
                if row == 0:
                    line_parts.append(f"{amplitude:4.1f}|")
                elif row == wave_height // 2:
                    line_parts.append(" 0.0|")
                elif row == wave_height - 1:
                    line_parts.append(f"{-amplitude:4.1f}|")
                else:
                    line_parts.append("    |")
            y_level = amplitude * (1 - 2 * row / (wave_height - 1))
            is_zero_line = abs(y_level) < 0.1
            row_chars = []
            num_points = min(display_width, len(self.y))
            for i in range(num_points):
                wave_val = self.y[i]
                distance = abs(wave_val - y_level)
                if distance < threshold_base * 0.3:
                    abs_wave = abs(wave_val)
                    if abs_wave > 0.8 * amplitude:
                        char = '#'
                    elif abs_wave > 0.4 * amplitude:
                        char = '*'
                    elif abs_wave > 0.1 * amplitude:
                        char = 'o'
                    elif abs_wave > 0.05:
                        char = '.'
                    else:
                        char = zero_char if self.params.show_reference_line and is_zero_line else ' '
                elif distance < threshold_base * 0.7:
                    if abs(wave_val) > 0.03:
                        char = '.' if abs(wave_val) > 0.1 else ','
                    else:
                        char = zero_char if self.params.show_reference_line and is_zero_line else ' '
                else:
                    char = zero_char if self.params.show_reference_line and is_zero_line else ' '
                row_chars.append(char)
            line_parts.append(''.join(row_chars))
            if self.params.show_rulers:
                line_parts.append("|")
            output.append(''.join(line_parts))
        output.append("")
        if self.params.show_rulers:
            ruler_parts = ["    +"]
            for i in range(0, display_width, max(1, display_width // 8)):
                pos = (i / display_width) * self.params.string_length
                ruler_parts.append(f"{pos:4.1f}---")
            ruler_parts.append("+")
            ruler_line = ''.join(ruler_parts)[:80]
            output.append(ruler_line)
        output.append("")
        controls = [
            "CONTROLS:",
            "  SPACE: Pause/Resume    R: Restart    Q: Quit",
            "  M: Cycle Mode          A/S: Amplitude +/-     F/G: Frequency +/-",
            "  W/E: Pulse Width +/-   D: Toggle Damping      T: Toggle Tension",
            "  B: Cycle Boundary      L: Toggle Slow Motion  U: Rulers On/Off",
            "  I/K: Manual Control    Z: Zero Wave           X: Add Disturbance",
            "  V: Toggle Reference    C: Clear History       P/O: Save/Load Preset"
        ]
        output.extend(controls)
        if self.params.mode == WaveMode.MANUAL:
            output.append(f"  Manual Amplitude: {self.manual_amplitude:5.2f}")
        max_wave = np.max(np.abs(self.y)) if len(self.y) > 0 else 0
        if not hasattr(self, '_calc_counter'):
            self._calc_counter = 0
        self._calc_counter += 1
        wave_energy = self.calculate_wave_energy() if self._calc_counter % 5 == 0 else getattr(self, '_last_energy', 0)
        dominant_freq = self.calculate_dominant_frequency() if self._calc_counter % 10 == 0 else getattr(self, '_last_freq', 0)
        if self._calc_counter % 5 == 0:
            self._last_energy = wave_energy
        if self._calc_counter % 10 == 0:
            self._last_freq = dominant_freq
        output.append(f"  Max Amplitude: {max_wave:5.2f} | Energy: {wave_energy:8.2f} | Freq: {dominant_freq:5.2f} Hz")
        output.append(f"  Legend: # (peaks) * (high) o (medium) . (low) , (tiny) - (zero)")
        if hasattr(self, '_last_update_time'):
            fps = 1.0 / max(0.001, time.time() - self._last_update_time)
            output.append(f"  FPS: {fps:4.1f}")
        self._last_update_time = time.time()
        return "\n".join(output)
    def handle_input(self):
        """Handle keyboard input"""
        try:
            while not self.display.input_queue.empty():
                key = self.display.input_queue.get_nowait()
                if key.lower() == 'q':
                    self.running = False
                elif key == ' ':
                    self.paused = not self.paused
                elif key.lower() == 'r':
                    self.reset_simulation()
                elif key.lower() == 'm':
                    self.cycle_mode()
                elif key.lower() == 'a':
                    self.params.amplitude = min(3.0, self.params.amplitude + 0.1)
                elif key.lower() == 's':
                    self.params.amplitude = max(0.1, self.params.amplitude - 0.1)
                elif key.lower() == 'w':
                    self.params.pulse_width = min(2.0, self.params.pulse_width + 0.1)
                elif key.lower() == 'e':
                    self.params.pulse_width = max(0.1, self.params.pulse_width - 0.1)
                elif key.lower() == 'd':
                    self.params.damping = DampingLevel.LOTS if self.params.damping == DampingLevel.NONE else DampingLevel.NONE
                    self.damping_coeff = 0.05 if self.params.damping == DampingLevel.LOTS else 0.0
                elif key.lower() == 't':
                    self.params.tension = TensionLevel.HIGH if self.params.tension == TensionLevel.LOW else TensionLevel.LOW
                    self.wave_speed = 1.5 if self.params.tension == TensionLevel.HIGH else 0.8
                elif key.lower() == 'b':
                    self.cycle_boundary()
                elif key.lower() == 'l':
                    self.params.slow_motion = not self.params.slow_motion
                elif key.lower() == 'i':  
                    if self.params.mode == WaveMode.MANUAL:
                        self.manual_amplitude = min(self.params.amplitude, self.manual_amplitude + 0.1)
                elif key.lower() == 'k':  
                    if self.params.mode == WaveMode.MANUAL:
                        self.manual_amplitude = max(-self.params.amplitude, self.manual_amplitude - 0.1)
                elif key.lower() == 'f':
                    self.params.pulse_width = max(0.1, self.params.pulse_width - 0.05)
                elif key.lower() == 'g':
                    self.params.pulse_width = min(2.0, self.params.pulse_width + 0.05)
                elif key.lower() == 'u':
                    self.params.show_rulers = not self.params.show_rulers
                elif key.lower() == 'v':
                    self.params.show_reference_line = not self.params.show_reference_line
                elif key.lower() == 'z':
                    self.y.fill(0)
                    self.y_prev.fill(0)
                    self.y_next.fill(0)
                elif key.lower() == 'x':
                    self.add_disturbance()
                elif key.lower() == 'c':
                    self.y_prev[:] = self.y[:]
                elif key.lower() == 'p':
                    self.save_preset()
                elif key.lower() == 'o':
                    self.load_preset()
        except queue.Empty:
            pass
    def save_preset(self, name="default"):
        """Save current parameters as a preset"""
        preset = {
            'mode': self.params.mode.value,
            'amplitude': self.params.amplitude,
            'pulse_width': self.params.pulse_width,
            'damping': self.params.damping.value,
            'tension': self.params.tension.value,
            'boundary': self.params.boundary.value,
            'string_length': self.params.string_length
        }
        if not hasattr(self, 'presets'):
            self.presets = {}
        self.presets[name] = preset
    def load_preset(self, name="default"):
        """Load a saved preset"""
        if hasattr(self, 'presets') and name in self.presets:
            preset = self.presets[name]
            self.params.mode = WaveMode(preset['mode'])
            self.params.amplitude = preset['amplitude']
            self.params.pulse_width = preset['pulse_width']
            self.params.damping = DampingLevel(preset['damping'])
            self.params.tension = TensionLevel(preset['tension'])
            self.params.boundary = BoundaryCondition(preset['boundary'])
            self.params.string_length = preset['string_length']
            self.wave_speed = 1.5 if self.params.tension == TensionLevel.HIGH else 0.8
            self.damping_coeff = 0.05 if self.params.damping == DampingLevel.LOTS else 0.0
            self.reset_simulation()
    def cycle_mode(self):
        """Cycle through wave modes"""
        modes = [WaveMode.PULSE, WaveMode.OSCILLATE, WaveMode.MANUAL]
        current_idx = modes.index(self.params.mode)
        self.params.mode = modes[(current_idx + 1) % len(modes)]
        if self.params.mode != WaveMode.MANUAL:
            self.manual_amplitude = 0.0
    def cycle_boundary(self):
        """Cycle through boundary conditions"""
        boundaries = [BoundaryCondition.FIXED_END, BoundaryCondition.LOOSE_END, BoundaryCondition.NO_END]
        current_idx = boundaries.index(self.params.boundary)
        self.params.boundary = boundaries[(current_idx + 1) % len(boundaries)]
    def reset_simulation(self):
        """Reset the simulation to initial state"""
        self.current_time = 0.0
        self.y.fill(0)
        self.y_prev.fill(0)
        self.y_next.fill(0)
        self.manual_amplitude = 0.0
        self.paused = False
    def start_simulation(self):
        """Start the wave simulation with optimized rendering"""
        self.running = True
        self.display.enable_optimizations()
        self.display.hide_cursor()
        self.display.start_input_thread()
        frame_count = 0
        last_render_time = time.time()
        self.display.clear_screen()
        try:
            while self.running:
                current_time = time.time()
                self.handle_input()
                if not self.paused:
                    self.update_wave()
                    self.current_time += self.params.dt
                if self.params.slow_motion:
                    render_interval = 0.25  
                elif self.params.mode == WaveMode.MANUAL:
                    render_interval = 0.08  
                else:
                    render_interval = 0.12  
                if current_time - last_render_time >= render_interval:
                    wave_display = self.render_wave()
                    frame_lines = wave_display.split('\n')
                    self.display.render_frame_diff(frame_lines)
                    last_render_time = current_time
                frame_count += 1
                time.sleep(0.008)  
        except KeyboardInterrupt:
            self.running = False
        finally:
            self.display.stop_input_thread()
            self.display.show_cursor()
            print("\nSimulation ended.")
    def calculate_wave_energy(self):
        """Calculate the total wave energy"""
        kinetic_energy = 0.5 * np.sum((self.y - self.y_prev)**2) / (self.params.dt**2)
        potential_energy = 0.5 * (self.wave_speed**2) * np.sum(np.gradient(self.y, self.dx)**2)
        return kinetic_energy + potential_energy
    def calculate_dominant_frequency(self):
        """Calculate the dominant frequency in the wave"""
        if len(self.y) < 4:
            return 0.0
        zero_crossings = 0
        for i in range(1, len(self.y)):
            if (self.y[i-1] >= 0 and self.y[i] < 0) or (self.y[i-1] < 0 and self.y[i] >= 0):
                zero_crossings += 1
        if zero_crossings > 0:
            return zero_crossings / (2 * self.params.string_length / self.wave_speed)
        return 0.0
    def add_disturbance(self):
        """Add a random disturbance to the wave"""
        center = np.random.randint(len(self.y) // 4, 3 * len(self.y) // 4)
        width = 5
        amplitude = 0.2 * self.params.amplitude * np.random.uniform(-1, 1)
        for i in range(max(0, center - width), min(len(self.y), center + width)):
            distance = abs(i - center) / width
            pulse = amplitude * np.exp(-(distance * 3) ** 2)
            self.y[i] += pulse
            self.y_prev[i] += pulse * 0.8
def main():
    """Main function"""
    print("Wave on String Simulation - Terminal Version")
    print("Loading...")
    params = SimulationParams(
        mode=WaveMode.PULSE,
        amplitude=1.8,  
        pulse_width=0.4,  
        damping=DampingLevel.NONE,
        tension=TensionLevel.HIGH,
        boundary=BoundaryCondition.FIXED_END,
        show_rulers=True,
        show_timer=True,
        show_reference_line=True,
        slow_motion=False,
        string_length=8.0,  
        num_points=50,  
        dt=0.008  
    )
    print("Starting simulation in 2 seconds...")
    print("Use SPACE to pause, Q to quit, M to change modes")
    time.sleep(2)
    simulation = WaveSimulation(params)
    simulation.start_simulation()
if __name__ == "__main__":
    main()