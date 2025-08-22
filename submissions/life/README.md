# Life - Terminal Productivity Suite

A terminal-based productivity application that combines a Focus Timer, Habit Tracker, and Task Manager to help you stay organized and productive.

## Features

### Focus Timer
- Set custom timers for focused work sessions
- Start, pause, and reset functionality
- Visual countdown display
- Notification when timer completes

### Habit Tracker
- Create and track daily habits
- Automatic daily reset of habit status
- Visual completion indicators
- Persistent storage of habits

### Task Manager
- Create tasks with due dates
- Calendar view for task visualization
- Task completion tracking
- Date validation and error handling

## Installation

1. Ensure you have Python 3.7 or higher installed:
   ```bash
   python --version
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/terminalCraft.git
   cd terminalCraft
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:
   ```bash
   python main.py
   ```

2. Navigate the interface:
   - Use click to choose options
   - Press to select an option
   - Press "back" to go back
   - Click on the different interface elements

### Focus Timer
1. Select "Focus Timer" from the main menu
2. Enter the desired duration in minutes
3. Click "Start" to begin the timer
4. Use "Pause" to temporarily stop
5. Use "Reset" to clear the timer

### Habit Tracker
1. Select "Habit Tracker" from the main menu
2. Enter a habit name in the input field
3. Click "Add Habit" to create it
4. Use "Mark as Completed" to track progress
5. Use "Delete Habit" to remove unwanted habits

### Task Manager
1. Select "Task Manager" from the main menu
2. Enter a task name and due date (YYYY-MM-DD)
3. Click "Add Task" to create it
4. Use "Complete Task" to mark as done
5. Use "Delete Task" to remove tasks
6. Navigate months using "Previous Month" and "Next Month"

## Data Storage

All data is stored in the `data/` directory:
- `tasks.json`: Task Manager data
- `habits.json`: Habit Tracker data

## Requirements

- Python 3.7+
- textual
- rich

## Development

The project structure is organized as follows:
```
terminalCraft/
├── main.py              # Main application entry point
├── requirements.txt     # Project dependencies
├── data/               # Data storage directory
└── src/                # Source code
    ├── focus_timer.py  # Focus Timer implementation
    ├── habit_tracker.py # Habit Tracker implementation
    └── task_manager.py # Task Manager implementation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Acknowledgments

- Built with [Textual](https://github.com/Textualize/textual)
- Styled with [Rich](https://github.com/Textualize/rich)
