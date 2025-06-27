@echo off
REM Quick build script for Windows
REM Just double-click this file or run: build.bat

echo 🛰️  TermiCast Build Script (Windows)
echo ===================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not found
    echo    Install it from https://python.org
    echo    Make sure to check "Add Python to PATH" during install
    pause
    exit /b 1
)

echo ✅ Python found

REM Install dependencies
echo 📦 Installing dependencies...
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    echo    Try running: pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✅ Dependencies installed

REM Build the executable
echo 🔨 Building executable...
python build_executable.py

if errorlevel 0 (
    echo.
    echo 🎉 Build complete!
    echo 📍 Your executable is in: dist\
    echo 🚀 Run it with: dist\termicast.exe
    pause
) else (
    echo ❌ Build failed - check the output above
    pause
    exit /b 1
) 