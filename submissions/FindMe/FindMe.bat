@echo off
:MAIN_MENU
cls
echo =====================================
echo           F I N D M E
echo =====================================
echo 1. Search in C:\ (Root)
echo 2. Search in User Profiles (C:\Users)
echo 3. Search in Current Directory
echo 4. Custom Location
echo 5. Exit
echo =====================================
set /p choice="Choose where to search [1-5]: "

if "%choice%"=="1" (
    set search_location=C:\
    goto SEARCH_OPTIONS
)
if "%choice%"=="2" (
    set search_location=C:\Users
    goto SEARCH_OPTIONS
)
if "%choice%"=="3" (
    set search_location=%~dp0
    goto SEARCH_OPTIONS
)
if "%choice%"=="4" (
    set /p search_location="Enter full path (e.g., D:\Documents): "
    goto SEARCH_OPTIONS
)
if "%choice%"=="5" exit /b

echo Invalid choice! Press any key to try again...
pause >nul
goto MAIN_MENU

:SEARCH_OPTIONS
cls
echo =====================================
echo    SEARCHING IN: %search_location%
echo =====================================
echo 1. Search by Name (e.g., *.txt)
echo 2. Search by Type (Files/Folders)
echo 3. Search by Size
echo 4. Back to Main Menu
echo =====================================
set /p search_choice="Select search method [1-4]: "

if "%search_choice%"=="1" goto SEARCH_NAME
if "%search_choice%"=="2" goto SEARCH_TYPE
if "%search_choice%"=="3" goto SEARCH_SIZE
if "%search_choice%"=="4" goto MAIN_MENU

echo Invalid choice! Press any key to try again...
pause >nul
goto SEARCH_OPTIONS

:SEARCH_NAME
set /p file_name="Enter file name/pattern (e.g., *.docx): "
echo Searching for "%file_name%" in %search_location%...
dir /s /b "%search_location%\%file_name%" 2>nul
if errorlevel 1 echo No files found matching "%file_name%"
pause
goto SEARCH_OPTIONS

:SEARCH_TYPE
echo 1. Files Only
echo 2. Folders Only
set /p type_choice="Select type [1-2]: "

if "%type_choice%"=="1" (
    echo Searching for FILES in %search_location%...
    dir /s /b /a-d "%search_location%" 2>nul
)
if "%type_choice%"=="2" (
    echo Searching for FOLDERS in %search_location%...
    dir /s /b /ad "%search_location%" 2>nul
)
pause
goto SEARCH_OPTIONS

:SEARCH_SIZE
set /p size="Enter minimum size in bytes (e.g., 1048576 for 1MB): "
echo Searching for files > %size% bytes in %search_location%...
for /r "%search_location%" %%F in (*) do (
    if %%~zF gtr %size% echo %%F - %%~zF bytes
)
pause
goto SEARCH_OPTIONS