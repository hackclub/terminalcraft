#!/bin/bash
# Unix shell script to run Veritaminal on Linux and macOS

# Make sure the script fails on any error
set -e

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not found in your PATH. Please install Python 3.8 or higher."
    exit 1
fi

# Check for virtual environment and activate if present
if [ -f .venv/bin/activate ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Check if required packages are installed
if ! python3 -c "import colorama, prompt_toolkit" &> /dev/null; then
    echo "Installing required packages..."
    python3 -m pip install -r requirements.txt
fi

# Run the game with any provided arguments
python3 run_game.py "$@"

# If in virtual environment, deactivate
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi

exit 0
