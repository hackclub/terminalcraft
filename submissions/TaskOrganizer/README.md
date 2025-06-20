# Task Organizer

Task Organizer is a terminal-based tool that helps you plan, organize, and visualize your daily tasks as a time-blocked ASCII schedule. You can add, edit, and reorder tasks interactively, and save your schedule for future use.

## Features
- Add tasks with custom durations (e.g., 30m, 1h, 1h30m)
- Edit or reorder tasks using keyboard controls
- Visualize your schedule as an ASCII timeline
- Save and load your schedule from disk

## How to Run
1. **Run the binaries** 
    - For Windows: `main.exe`
    - For Linux: `./main.bin`
2. **Run the source code**:
    1.**Install dependencies:**
      - Python 3.7 or higher
      - Install required packages:
        ```bash
        pip install rich keyboard
        ```

    2.**Run the program:**
        ```bash
        python main.py
        ```

3. **Follow the prompts:**
   - Add tasks and durations as prompted
   - Use arrow keys and spacebar to reorder tasks
   - Press 'a' to add, 'e' to edit, and 'Esc' to finish

4. **Output:**
   - Your schedule will be saved as `schedule.txt` (ASCII format)
   - Optionally, you can save and load a schedule using the provided functions

## Keyboard Controls
- **Arrow keys:** Move cursor or selected task
- **Spacebar:** Pick up/drop a task for reordering
- **a:** Add a new task
- **e:** Edit the selected task
- **Esc:** Finish and save your schedule

## Why I created this?
I always wanted something to quickly plan the thing I need to do for the day. I am not realy good at using a mouse - I always click the wrong thing. So, a schedule app that uses only keyboard made my life much easier.

# Dependencies
On Windows: rich and keyboard
On Linux: rich