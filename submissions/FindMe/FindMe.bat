@echo off
setlocal enabledelayedexpansion

:: Configuration
set "TEMP_RESULTS=%temp%\findme_results.txt"
set "TEMP_SELECTED=%temp%\findme_selected.txt"

:MAIN_MENU
cls
echo ________________________________________________________________________________
echo.
echo                                F I N D M E
echo                           Author: Nader Sayed
echo ________________________________________________________________________________
echo.
echo                            1. Search by Name
echo                            2. Search by Type
echo                            3. Search by Size
echo                            4. Advanced Search
echo                            5. Exit
echo.
set /p "CHOICE=Select option (1-5): "

if "%CHOICE%"=="1" goto SEARCH_NAME
if "%CHOICE%"=="2" goto SEARCH_TYPE
if "%CHOICE%"=="3" goto SEARCH_SIZE
if "%CHOICE%"=="4" goto SEARCH_ADVANCED
if "%CHOICE%"=="5" exit /b
goto MAIN_MENU

:SEARCH_NAME
cls
echo ________________________________________________________________________________
echo.
echo                          S E A R C H   B Y   N A M E
echo ________________________________________________________________________________
echo.
set /p "LOCATION=Enter search location (e.g., C:\, %USERPROFILE%): "
set /p "NAME=Enter file name or part of name: "
echo Searching... Please wait...

dir /a-d /s /b "%LOCATION%\*%NAME%*" 2>nul > "%TEMP_RESULTS%"
goto SHOW_RESULTS

:SEARCH_TYPE
cls
echo ________________________________________________________________________________
echo.
echo                          S E A R C H   B Y   T Y P E
echo ________________________________________________________________________________
echo.
set /p "LOCATION=Enter search location: "
echo.
echo                            1. Files only
echo                            2. Directories only
echo.
set /p "TYPE_CHOICE=Select type (1-2): "

if "%TYPE_CHOICE%"=="1" (
    dir /a-d /s /b "%LOCATION%\*" 2>nul > "%TEMP_RESULTS%"
) else if "%TYPE_CHOICE%"=="2" (
    dir /ad /s /b "%LOCATION%\*" 2>nul > "%TEMP_RESULTS%"
) else (
    goto SEARCH_TYPE
)
goto SHOW_RESULTS

:SEARCH_SIZE
cls
echo ________________________________________________________________________________
echo.
echo                          S E A R C H   B Y   S I Z E
echo ________________________________________________________________________________
echo.
set /p "LOCATION=Enter search location: "
echo.
echo                        Examples: +1M (>1MB), -500K (<500KB)
set /p "SIZE=Enter size filter: "

echo Searching... This may take a while...
dir /a-d /s /b "%LOCATION%\*" 2>nul > "%TEMP_RESULTS%"

:: Size filtering (basic implementation)
if "%SIZE%" neq "" (
    type nul > "%TEMP_SELECTED%"
    for /f "delims=" %%f in ('type "%TEMP_RESULTS%"') do (
        for /f "tokens=3" %%s in ('dir /-c "%%f" ^| findstr /r /c:" [0-9][0-9]* *[0-9]"') do (
            set "filesize=%%s"
            set "filesize=!filesize:,=!"
            
            if "%SIZE:~0,1%"=="+" (
                set "limit=%SIZE:~1%"
                if !filesize! geq !limit! echo %%f >> "%TEMP_SELECTED%"
            ) else if "%SIZE:~0,1%"=="-" (
                set "limit=%SIZE:~1%"
                if !filesize! leq !limit! echo %%f >> "%TEMP_SELECTED%"
            ) else (
                set "limit=%SIZE%"
                if !filesize! equ !limit! echo %%f >> "%TEMP_SELECTED%"
            )
        )
    )
    move /y "%TEMP_SELECTED%" "%TEMP_RESULTS%" >nul
)
goto SHOW_RESULTS

:SEARCH_ADVANCED
cls
echo ________________________________________________________________________________
echo.
echo                        A D V A N C E D   S E A R C H
echo ________________________________________________________________________________
echo.
set /p "LOCATION=Enter search location: "
set /p "NAME=Enter name/part (leave blank for all): "
echo.
echo                            1. Files only
echo                            2. Directories only
echo                            3. Both
echo.
set /p "TYPE_CHOICE=Select type (1-3): "
set /p "SIZE=Enter size filter (optional): "

if "%NAME%"=="" set "NAME=*"
if "%TYPE_CHOICE%"=="1" set "DIR_OPT=/a-d"
if "%TYPE_CHOICE%"=="2" set "DIR_OPT=/ad"
if "%TYPE_CHOICE%"=="3" set "DIR_OPT="

echo Searching... This may take several minutes...
dir %DIR_OPT% /s /b "%LOCATION%\%NAME%" 2>nul > "%TEMP_RESULTS%"

:: Apply size filter if specified
if "%SIZE%" neq "" (
    type nul > "%TEMP_SELECTED%"
    for /f "delims=" %%f in ('type "%TEMP_RESULTS%"') do (
        for /f "tokens=3" %%s in ('dir /-c "%%f" ^| findstr /r /c:" [0-9][0-9]* *[0-9]"') do (
            set "filesize=%%s"
            set "filesize=!filesize:,=!"
            
            if "%SIZE:~0,1%"=="+" (
                set "limit=%SIZE:~1%"
                if !filesize! geq !limit! echo %%f >> "%TEMP_SELECTED%"
            ) else if "%SIZE:~0,1%"=="-" (
                set "limit=%SIZE:~1%"
                if !filesize! leq !limit! echo %%f >> "%TEMP_SELECTED%"
            ) else (
                set "limit=%SIZE%"
                if !filesize! equ !limit! echo %%f >> "%TEMP_SELECTED%"
            )
        )
    )
    move /y "%TEMP_SELECTED%" "%TEMP_RESULTS%" >nul
)
goto SHOW_RESULTS

:SHOW_RESULTS
cls
set "RESULT_COUNT=0"
for /f %%a in ('type "%TEMP_RESULTS%" ^| find /c /v ""') do set "RESULT_COUNT=%%a"

if %RESULT_COUNT% equ 0 (
    echo No results found matching your criteria
    timeout /t 3 >nul
    goto MAIN_MENU
)

echo ________________________________________________________________________________
echo.
echo                        S E A R C H   R E S U L T S
echo ________________________________________________________________________________
echo.
echo Found %RESULT_COUNT% items
echo.

:: Display first 20 results with numbers
set "DISPLAY_COUNT=0"
for /f "delims=" %%f in ('type "%TEMP_RESULTS%"') do (
    set /a DISPLAY_COUNT+=1
    echo [!DISPLAY_COUNT!] %%~nxf - %%~dpf
    if !DISPLAY_COUNT! equ 20 goto SELECT_ACTION
)

:SELECT_ACTION
echo.
echo                            1. Open a file
echo                            2. Open containing folder
echo                            3. New search
echo                            4. Exit
echo.
set /p "ACTION=Select action (1-4): "

if "%ACTION%"=="1" goto OPEN_FILE
if "%ACTION%"=="2" goto OPEN_FOLDER
if "%ACTION%"=="3" goto MAIN_MENU
if "%ACTION%"=="4" exit /b
goto SELECT_ACTION

:OPEN_FILE
echo.
set /p "FILE_NUM=Enter file number to open: "
set "CURRENT_INDEX=0"
for /f "delims=" %%f in ('type "%TEMP_RESULTS%"') do (
    set /a CURRENT_INDEX+=1
    if !CURRENT_INDEX! equ %FILE_NUM% (
        start "" "%%f"
        goto SELECT_ACTION
    )
)
echo Invalid file number
goto OPEN_FILE

:OPEN_FOLDER
echo.
set /p "FILE_NUM=Enter file number to open folder: "
set "CURRENT_INDEX=0"
for /f "delims=" %%f in ('type "%TEMP_RESULTS%"') do (
    set /a CURRENT_INDEX+=1
    if !CURRENT_INDEX! equ %FILE_NUM% (
        explorer /select,"%%f"
        goto SELECT_ACTION
    )
)
echo Invalid file number
goto OPEN_FOLDER

:END
del "%TEMP_RESULTS%" 2>nul
del "%TEMP_SELECTED%" 2>nul
exit /b
