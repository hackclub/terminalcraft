@echo off
title TerminalOS Launcher
color 0B

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║              🖥️  TerminalOS               ║  
echo  ║           Windows Launcher               ║
echo  ╚══════════════════════════════════════════╝
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! 
    echo Please install Python 3.8+ from python.org
    echo.
    pause
    exit /b 1
)

REM Run TerminalOS launcher
python start_terminalos.py %*

if errorlevel 1 (
    echo.
    echo ❌ TerminalOS failed to start
    pause
)