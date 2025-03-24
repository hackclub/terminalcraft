#!/bin/bash
PACKAGE_NAME='FindMe'
REPO_ROOT='https://github.com/Nadoooor/FindMe'
EXECUTABLE_FILE='FindMe.sh'

# Check for required tools
unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    *)          machine="UNKNOWN:${unameOut}"
esac

echo "Detected OS: ${machine}"

if [ "$machine" = "Mac" ]; then
    if ! command -v toilet &> /dev/null; then
        brew install figlet toilet || exit 1
    fi
    if ! command -v dialog &> /dev/null; then
        brew install dialog || exit 1
    fi
    if ! command -v boxes &> /dev/null; then
        brew install boxes || exit 1
    fi
    if ! command -v lolcat &> /dev/null; then
        brew install lolcat || exit 1
    fi
elif [ "$machine" = "Linux" ]; then
    if ! command -v toilet &> /dev/null; then
        sudo apt-get install -y figlet toilet || exit 1
    fi
    if ! command -v dialog &> /dev/null; then
        sudo apt-get install -y dialog || exit 1
    fi
    if ! command -v boxes &> /dev/null; then
        sudo apt-get install -y boxes || exit 1
    fi
    if ! command -v lolcat &> /dev/null; then
        sudo apt-get install -y lolcat || exit 1
    fi
fi

# Main loop
while true; do
    clear
    if command -v toilet &> /dev/null; then
        toilet -f ivrit 'FindMe' | boxes -d cat -a hc -p h8 | lolcat
    else
        echo "=== FindMe ==="
    fi

    echo "Author: Nader Sayed"
    echo "Ctrl + C to exit"
    sleep 1

    # Display dialog menu
    loca=$(dialog --menu 'choose where to find' 0 0 4 '/' 'Find in the root dir' '/home' 'Find in the home dir for all users' "/home/$(whoami)" 'Find in the current user home dir' 'Exit' 'Exit the program' 2>&1 >/dev/tty)
    if [[ $loca == "Exit" ]]; then
        break
    fi

    clear
    if [[ -z "$loca" ]]; then
        echo "No location selected. Returning to the beginning..."
        continue
    fi

    # Display find method selection
    find_method=$(dialog --checklist 'Choose the methods that you want to use to find the file.' 0 0 7 "-name" 'Search by the name of the file' off "-type" 'select the file type (file ,dir)' off "-size" 'search for files (+n)greater or (-n)smaller then.' off "-iname" 'Searches for files with a specific name,regardless of case.' off "-readable" 'A file that you can read its content' off "-writable" 'A file that you can edit and change its content' off "-executable" 'A file that the sofware can run as a program.' off 2>&1 >/dev/tty)
    clear

    if [[ -z "$find_method" ]]; then
        echo "Canceled..."
        continue
    fi

    # Build the find command
    find_command="find \"$loca\""
    if [[ $find_method == *"-name"* ]]; then
        file_name=$(dialog --inputbox "Enter the file name." 0 0 2>&1 >/dev/tty)
        if [[ -z "$file_name" ]]; then
            dialog --msgbox "File name cannot be empty." 0 0
            continue
        fi
        find_command+=" -name \"$file_name\" 2>/dev/null"
    fi
    if [[ $find_method == *"-type"* ]]; then
        file_type=$(dialog --inputbox "Enter the file type (f for file or d for dir)." 0 0 2>&1 >/dev/tty)
        find_command+=" -type \"$file_type\" 2>/dev/null"
    fi
    if [[ $find_method == *"-size"* ]]; then
        file_size=$(dialog --inputbox "Enter the file size (+num to search more than the num or -num to search less than the num or num  ex.5M megabyte or 5k kilobyte)." 0 0 2>&1 >/dev/tty)
        find_command+=" -size \"$file_size\" 2>/dev/null"
    fi
    if [[ $find_method == *"-iname"* ]]; then
        file_iname=$(dialog --inputbox "Enter the file name (Neglecting the capital and small letters)." 0 0 2>&1 >/dev/tty)
        find_command+=" -iname \"$file_iname\" 2>/dev/null"
    fi
    if [[ $find_method == *"-readable"* ]]; then
        find_command+=" -readable 2>/dev/null"
    fi
    if [[ $find_method == *"-writable"* ]]; then
        find_command+=" -writable 2>/dev/null"
    fi
    if [[ $find_method == *"-executable"* ]]; then
        find_command+=" -executable 2>/dev/null"
    fi

    # Execute the find command
    results=$(eval "$find_command")
    dialog --msgbox "$results" 20 80
    clear
done
