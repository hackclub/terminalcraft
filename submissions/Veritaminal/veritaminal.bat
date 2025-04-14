@echo off
REM Windows batch script to run Veritaminal

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not found in your PATH. Please install Python 3.8 or higher.
    exit /b 1
)

REM Check for virtual environment and activate if present
if exist .venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Check if required packages are installed
python -c "import colorama, prompt_toolkit" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installing required packages...
    python -m pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo Failed to install required packages.
        exit /b 1
    )
)

REM Run the game
python run_game.py %*

REM If in virtual environment, deactivate
if defined VIRTUAL_ENV (
    deactivate
)

exit /b 0
