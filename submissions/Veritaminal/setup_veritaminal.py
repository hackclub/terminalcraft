#!/usr/bin/env python3
"""
Veritaminal Setup Script

This script sets up Veritaminal for first use, creating a virtual environment
and installing dependencies.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def print_colored(text, color_code):
    """Print colored text."""
    print(f"\033[{color_code}m{text}\033[0m")

def print_header(text):
    """Print a header."""
    print_colored("\n" + "=" * 60, "34")
    print_colored(text.center(60), "33;44")
    print_colored("=" * 60 + "\n", "34")

def check_python_version():
    """Check if Python version is adequate."""
    print("Checking Python version...")
    if sys.version_info < (3, 8):
        print_colored("Error: Python 3.8 or higher is required.", "31")
        sys.exit(1)
    print_colored(f"Found Python {sys.version.split()[0]}", "32")

def create_virtual_env():
    """Create a virtual environment for the game."""
    print("Setting up a virtual environment...")
    
    venv_path = Path(".venv")
    if venv_path.exists():
        response = input("Virtual environment already exists. Recreate? (y/n): ")
        if response.lower() == 'y':
            shutil.rmtree(venv_path)
        else:
            print("Using existing virtual environment.")
            return

    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print_colored("Virtual environment created successfully.", "32")
    except subprocess.CalledProcessError:
        print_colored("Error creating virtual environment.", "31")
        sys.exit(1)

def install_dependencies():
    """Install required packages."""
    print("Installing dependencies...")
    
    # Determine the path to the Python executable in the virtual environment
    if platform.system() == "Windows":
        pip_path = Path(".venv") / "Scripts" / "pip.exe"
    else:
        pip_path = Path(".venv") / "bin" / "pip"
    
    try:
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print_colored("Dependencies installed successfully.", "32")
    except subprocess.CalledProcessError:
        print_colored("Error installing dependencies.", "31")
        sys.exit(1)

def make_scripts_executable():
    """Make the shell scripts executable on Unix systems."""
    if platform.system() != "Windows":
        print("Making scripts executable...")
        try:
            os.chmod("veritaminal.sh", 0o755)
            print_colored("Scripts are now executable.", "32")
        except Exception as e:
            print_colored(f"Warning: Could not make scripts executable: {e}", "33")

def setup_run_guidance():
    """Print guidance on how to run the game."""
    system = platform.system()
    
    print_header("SETUP COMPLETE")
    print("To run Veritaminal, use one of the following methods:\n")
    
    if system == "Windows":
        print("1. Double-click on 'veritaminal.bat'")
        print("2. Run from command prompt: veritaminal.bat")
        print("3. Directly with Python: python run_game.py")
    else:
        print("1. Use the shell script: ./veritaminal.sh")
        print("2. Directly with Python: python3 run_game.py")
    
    print("\nIf you want to install as a package:")
    print("pip install -e .")
    print("Then run with: veritaminal\n")

def setup_api_key():
    """Help set up the API key."""
    print_header("API KEY SETUP")
    
    print("Veritaminal needs a Google Gemini API key to function.")
    print("You can get a key from: https://aistudio.google.com/apikey\n")
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("An .env file already exists.")
        response = input("Do you want to update your API key? (y/n): ")
        if response.lower() != 'y':
            return

    key = input("Enter your Gemini API key: ").strip()
    
    if not key:
        print_colored("No API key provided. You'll need to add it later to .env", "33")
        return
    
    try:
        with open(".env", "w") as f:
            f.write(f"GEMINI_API_KEY={key}\n")
        print_colored("API key saved to .env file.", "32")
    except Exception as e:
        print_colored(f"Error saving API key: {e}", "31")
        print("You'll need to manually create an .env file with: GEMINI_API_KEY=your_key")

def main():
    """Run the setup process."""
    print_header("VERITAMINAL SETUP")
    
    check_python_version()
    create_virtual_env()
    install_dependencies()
    make_scripts_executable()
    setup_api_key()
    setup_run_guidance()

if __name__ == "__main__":
    main()
