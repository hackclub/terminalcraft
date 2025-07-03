# Welcome to TermFlow - Your Automated Shell

## What is TermFlow?

TermFlow is a terminal-based workflow automation tool that lets you build, save, load, and run sequences of shell commands interactively.  
It helps automate repetitive tasks without scripting by allowing you to create workflows step-by-step directly in your terminal.

---

## How to Run TermFlow

### Requirements

- Python 3.8 or newer  
- The Python package `rich` for terminal UI  

#### Install `rich`:

    pip install rich

### Running

1. Run termflow.py

2. Follow the on-screen prompts to add, list, run, save, and load workflows.

---

## Dependencies

- [Python 3.8+](https://www.python.org/downloads/)  
- [Rich library](https://github.com/Textualize/rich) for rich terminal formatting  

Install with:

    pip install rich

---

## Why I Created TermFlow

I built TermFlow to help simplify and speed up command-line workflows without needing to write complex scripts.  
It’s designed for developers, sysadmins, and anyone who often runs repeated sequences of commands in the terminal.  
TermFlow makes automation approachable and sharable, boosting productivity and saving me a butt ton of time.

---

## Pre-built Linux Binaries

This project is currently a Python script that requires Python and dependencies to run.  
To distribute a standalone binary for Linux (and other platforms), you can use tools like:

- **PyInstaller**  

Build a single executable by running these commands:

    pip install pyinstaller
    pyinstaller --onefile termflow.py

This creates a `dist/termflow` executable you can share.

### Brief steps:

1. Install PyInstaller  
2. Run the above commands  
3. Test the executable on a clean Linux machine to ensure no dependencies are missing  
4. Distribute the executable to users who don’t need Python installed

For Windows and macOS, PyInstaller supports those platforms as well, but cross-compiling requires additional setup.

---

## Source Code

The source code is contained in the single file `termflow.py` included in this folder.

---

## License

Feel free to use, modify, and share TermFlow under the MIT License!
