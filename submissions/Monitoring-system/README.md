# System Resource Monitor

A simple terminal-based system resource monitor written in Python that works across Windows, Linux, and macOS.

## Features

- Enhanced visual UI with boxed sections and colors
- CPU usage and information
- Memory usage
- Network statistics
- Top processes by CPU usage
- Cross-platform compatibility
- Error handling for reliable operation
- Terminal size adaptation

## Screenshots

```
╭ SYSTEM RESOURCE MONITOR ────────────────────────────────────╮
│ Time: 2025-03-01 15:30:45 | Platform: Windows 10 | Python: 3.10.4 │
│                                                              │
╰──────────────────────────────────────────────────────────────╯

╭ CPU ────────────────────────────────────────────────────────╮
│ Usage: [████████████████████░░░░░░░░░░░░] 64.5%             │
│ Logical Cores: 8 | Physical Cores: 4                        │
│ Frequency: Current: 3600.00 MHz                             │
╰──────────────────────────────────────────────────────────────╯

╭ MEMORY ─────────────────────────────────────────────────────╮
│ Usage: [██████████████░░░░░░░░░░░░░░░░░░] 45.2%             │
│ Total: 16.00 GB | Used: 7.23 GB | Available: 8.77 GB        │
╰──────────────────────────────────────────────────────────────╯
```

## Download and Installation

You have multiple options to download and install the System Resource Monitor:

### Option 1: Direct Download

1. Download the zip package from the releases section
2. Extract the zip file
3. Install dependencies: `pip install -r requirements.txt`
4. Run the script: `python system_monitor.py`

### Option 2: Install with pip

```bash
# Install dependencies
pip install psutil colorama

# Copy the system_monitor.py file to your preferred location
# Run the monitor
python system_monitor.py
```

### Option 3: Create an executable (Windows)

```bash
# Install PyInstaller
pip install pyinstaller

# Run the package script
python package.py
```

Then select option 1 to create an executable. The executable will be created in the `dist` folder.

## Usage

- Run the monitor: `python system_monitor.py`
- The interface will update automatically every 2 seconds
- Press `Ctrl+C` to exit the program

## Platform Support

The monitor has been tested and works on:
- Windows 10/11
- Linux (Ubuntu, Debian, etc.)
- macOS

## Requirements

- Python 3.6+
- psutil
- colorama (optional, for colored output)

## Troubleshooting

If you encounter any issues:

1. Make sure you have the latest version of psutil installed:
   ```
   pip install --upgrade psutil
   ```

2. If box characters don't display correctly, try using a terminal that supports Unicode or set a compatible font.

3. For platform-specific issues:
   - Windows: Run as administrator if monitoring system processes
   - Linux: You may need to install additional dependencies: `sudo apt-get install python3-dev`
   - macOS: You may need to install Command Line Tools: `xcode-select --install`
