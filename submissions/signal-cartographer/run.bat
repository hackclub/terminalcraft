@echo off
REM Windows launcher for The Signal Cartographer

echo ==========================================
echo   The Signal Cartographer: Echoes from the Void
echo ==========================================
echo Initializing AetherTap...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is required but not installed.
    echo Please install Python 3.7 or higher from python.org
    pause
    exit /b 1
)

REM Check Python version (basic check)
python -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)" >nul 2>&1
if errorlevel 1 (
    echo Error: Python 3.7 or higher is required.
    python --version
    pause
    exit /b 1
)

echo Starting Signal Cartographer...
echo Press Ctrl+C to exit.
echo.

python main.py

if errorlevel 1 (
    echo.
    echo Game exited with an error. Check the output above.
    pause
)
