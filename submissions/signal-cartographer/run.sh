#!/bin/bash
# Linux/macOS launcher for The Signal Cartographer

echo "=========================================="
echo "  The Signal Cartographer: Echoes from the Void"
echo "=========================================="
echo "Initializing AetherTap..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3.7 or higher."
    exit 1
fi

# Check Python version is 3.7+
python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Error: Python 3.7 or higher is required."
    python3 --version
    exit 1
fi

# Check terminal size
COLS=$(tput cols 2>/dev/null || echo 80)
LINES=$(tput lines 2>/dev/null || echo 24)

if [ "$COLS" -lt 80 ] || [ "$LINES" -lt 24 ]; then
    echo "Warning: Terminal size should be at least 80x24 for optimal experience."
    echo "Current size: ${COLS}x${LINES}"
    echo "Please resize your terminal if the interface appears corrupted."
    echo ""
fi

echo "Starting Signal Cartographer..."
echo "Press Ctrl+C to exit."
echo ""

python3 main.py
