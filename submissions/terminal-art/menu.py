#!/usr/bin/env python3
import curses
import os
import subprocess
import sys
import platform
PROGRAMS = [
    {"name": "Basic Video Simulation", "file": "video_terminal.py", "description": "A simple wave-like animation using ASCII characters."},
    {"name": "Matrix Effect", "file": "matrix_terminal.py", "description": "A simulation of the famous \"digital rain\" effect from The Matrix movie."},
    {"name": "Fire Effect", "file": "fire_terminal.py", "description": "A simulation of fire using ASCII characters and colors."},
    {"name": "Dancing Man", "file": "dancing_man.py", "description": "A simulation of a dancing stick figure with disco lights."},
    {"name": "Bouncing Ball", "file": "bouncing_ball.py", "description": "A physics-based simulation of bouncing balls with trails."},
    {"name": "Dance and Bounce", "file": "dance_and_bounce.py", "description": "A combined simulation featuring both the dancing man and bouncing balls."},
    {"name": "Starfield", "file": "starfield.py", "description": "A simulation of flying through space with stars moving toward you."},
    {"name": "Rain", "file": "rain.py", "description": "A simulation of rain falling with splashes when raindrops hit the ground."},
    {"name": "Conway's Game of Life", "file": "game_of_life.py", "description": "An implementation of Conway's Game of Life cellular automaton with interactive controls."},
    {"name": "Fireworks Display", "file": "fireworks.py", "description": "A colorful fireworks simulation with rising rockets and particle explosions."},
    {"name": "Digital Clock", "file": "digital_clock.py", "description": "A customizable digital clock with ASCII art digits and various display options."},
    {"name": "Snake Game", "file": "snake_game.py", "description": "A classic snake game where you control a snake to eat food and grow longer."},
    {"name": "Typing Test", "file": "typing_test.py", "description": "A typing speed and accuracy test with WPM (words per minute) calculation."},
]
def draw_menu(screen, selected_idx, start_idx, max_visible):
    """Draw the menu with the current selection."""
    height, width = screen.getmaxyx()
    visible_count = min(max_visible, len(PROGRAMS))
    title = "TERMINAL VIDEO SIMULATIONS MENU"
    screen.addstr(1, (width - len(title)) // 2, title, curses.A_BOLD)
    instructions = "Use UP/DOWN arrows to navigate, ENTER to select, Q to quit"
    screen.addstr(3, (width - len(instructions)) // 2, instructions)
    for i in range(visible_count):
        idx = (start_idx + i) % len(PROGRAMS)
        program = PROGRAMS[idx]
        y_pos = i + 5
        if idx == selected_idx:
            attr = curses.A_REVERSE | curses.A_BOLD
        else:
            attr = curses.A_NORMAL
        menu_text = f"{idx + 1}. {program['name']}"
        screen.addstr(y_pos, 4, menu_text, attr)
        if idx == selected_idx:
            desc_text = f"> {program['description']}"
            if len(desc_text) > width - 8:
                desc_text = desc_text[:width - 11] + "..."
            screen.addstr(y_pos + 1, 6, desc_text, curses.A_DIM)
    if len(PROGRAMS) > visible_count:
        scrollbar_height = int((visible_count / len(PROGRAMS)) * visible_count)
        scrollbar_pos = int((start_idx / len(PROGRAMS)) * visible_count)
        for i in range(visible_count):
            if scrollbar_pos <= i < scrollbar_pos + scrollbar_height:
                screen.addstr(i + 5, width - 2, "█")
            else:
                screen.addstr(i + 5, width - 2, "│")
    footer = "Press 'q' to quit"
    screen.addstr(height - 2, (width - len(footer)) // 2, footer)
def run_program(program_file):
    """Run the selected program."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    program_path = os.path.join(current_dir, program_file)
    if not os.path.exists(program_path):
        return f"Error: {program_file} not found!"
    try:
        python_exe = sys.executable
        result = subprocess.run([python_exe, program_path], capture_output=True, text=True)
        if result.returncode != 0:
            return f"Program exited with error code {result.returncode}\n{result.stderr}"
        return "Program completed successfully."
    except Exception as e:
        return f"Error running program: {str(e)}"
def main(screen):
    """Main function."""
    curses.curs_set(0)  
    curses.start_color()
    curses.use_default_colors()
    screen.keypad(True)  
    selected_idx = 0
    start_idx = 0
    max_visible = 10  
    running = True
    status_message = ""
    while running:
        screen.clear()
        height, width = screen.getmaxyx()
        draw_menu(screen, selected_idx, start_idx, max_visible)
        if status_message:
            if len(status_message) > width - 4:
                status_message = status_message[:width - 7] + "..."
            screen.addstr(height - 4, 2, status_message, curses.A_BOLD)
        screen.refresh()
        key = screen.getch()
        if key == ord('q') or key == ord('Q'):
            running = False
        elif key == curses.KEY_UP:
            selected_idx = (selected_idx - 1) % len(PROGRAMS)
            if selected_idx < start_idx:
                start_idx = selected_idx
            elif selected_idx >= start_idx + max_visible:
                start_idx = selected_idx - max_visible + 1
        elif key == curses.KEY_DOWN:
            selected_idx = (selected_idx + 1) % len(PROGRAMS)
            if selected_idx < start_idx:
                start_idx = selected_idx
            elif selected_idx >= start_idx + max_visible:
                start_idx = selected_idx - max_visible + 1
        elif key == curses.KEY_ENTER or key == 10 or key == 13:  
            screen.clear()
            screen.addstr(0, 0, f"Running {PROGRAMS[selected_idx]['name']}...")
            screen.refresh()
            curses.endwin()
            program_file = PROGRAMS[selected_idx]['file']
            print(f"\nRunning {program_file}...\n")
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                program_path = os.path.join(current_dir, program_file)
                python_exe = sys.executable
                subprocess.call([python_exe, program_path])
                print(f"\nReturned from {program_file}. Press any key to continue...")
                input()
                status_message = f"Returned from {PROGRAMS[selected_idx]['name']}"
            except Exception as e:
                status_message = f"Error: {str(e)}"
            screen = curses.initscr()
            curses.noecho()
            curses.cbreak()
            screen.keypad(True)
            curses.curs_set(0)
def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import curses
        return True
    except ImportError:
        if platform.system() == "Windows":
            print("The 'windows-curses' package is required to run this program.")
            print("Please install it using: pip install windows-curses")
        else:
            print("The 'curses' package is required to run this program.")
        return False
if __name__ == "__main__":
    if check_dependencies():
        try:
            curses.wrapper(main)
        except KeyboardInterrupt:
            print("\nExiting...")
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")