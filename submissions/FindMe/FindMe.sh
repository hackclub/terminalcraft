#!/bin/bash
PACKAGE_NAME='FindMe'
EXECUTABLE_FILE='FindMe.sh'

# Check for required tools
unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
esac

echo "Detected OS: ${machine}"

if [ "$machine" = "Mac" ]; then
    if ! command -v figlet &> /dev/null; then
        brew install figlet || exit 1
    fi
    if ! command -v dialog &> /dev/null; then
        brew install gum || exit 1
    fi
    if ! command -v boxes &> /dev/null; then
        brew install boxes || exit 1
    fi
    if ! command -v lolcat &> /dev/null; then
        brew install lolcat || exit 1

    fi
elif [ "$machine" = "Linux" ]; then
    if ! command -v figlet &> /dev/null; then
        sudo apt-get install -y figlet  || exit 1
        if [[ $? -eq 1 ]]; then
        sudo dnf install figlet
        fi
    fi
    if ! command -v dialog &> /dev/null; then
        sudo apt-get install -y dialog || exit 1
        if [[ $? -eq 1 ]]; then
        sudo dnf install dialog
        fi
    fi
    if ! command -v boxes &> /dev/null; then
        sudo apt-get install -y boxes || exit 1
        if [[ $? -eq 1 ]]; then
        sudo dnf install boxes
        fi
    fi
    if ! command -v lolcat &> /dev/null; then
        sudo apt-get install -y lolcat || exit 1
        if [[ $? -eq 1 ]]; then
        sudo dnf install lolcat
        fi
    fi
    if ! command -v gum &> /dev/null; then
        sudo apt install gum
        if [[ $? -eq 1 ]]; then
        curl -LO https://github.com/charmbracelet/gum/releases/latest/download/gum_0.13.0_linux_amd64.rpm
        sudo rpm -i gum_*.rpm
        sudo dnf install gum 
        fi
    fi
fi

# Main loop
while true; do
    clear
    figlet -f ivrit 'eMdniF' | boxes -d cat -a hc -p h8 | lolcat
    if [[ $? -eq 1 ]]; then
    clear
    echo "====FindMe===="
    fi

    echo "Author: Nader Sayed"
    echo "Ctrl + C to exit"
    sleep 1

    # Display dialog menu
    if [ $machine = "Linux" ]; then
    loca=$(dialog --menu 'choose where to find' 0 0 3 '/' 'Find in the root dir' '/home' 'Find in the home dir for all users' "/home/$(whoami)" 'Find in the current user home dir'  'Exit' "Exit the program" 3>&1 1>&2 2>&3)
    if [[ $loca == "Exit" ]]; then
clear        
break
    fi

    clear
    if [[ -z "$loca" ]]; then
        echo "No location selected. Returning to the beginning..."
        continue
    fi

    # Display find method selection
    find_method=$(dialog --checklist 'Choose the methods that you want to use to find the file. (Press space to check them) ' 0 0 7 "-name" 'Search by the name of the file' off "-iname" 'Searches for files with a specific name,regardless of case.' off "-type" 'select the file type (file ,dir)' off "-size" 'search for files (+n)greater or (-n)smaller then.' off "-readable" 'A file that you can read its content' off "-writable" 'A file that you can edit and change its content' off "-executable" 'A file that the sofware can run as a program.' off 2>&1 >/dev/tty)
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
	file_name+="*"
        find_command+=" -name \"$file_name\" 2>/dev/null"
    fi

    if [[ $find_method == *"-iname"* ]]; then
        file_iname=$(dialog --inputbox "Enter the file name (Neglecting the capital and small letters)." 0 0 2>&1 >/dev/tty)
        if [[ -z "$file_iname" ]]; then
            dialog --msgbox "File name cannot be empty." 0 0
            continue
        fi
	file_iname+="*"
	find_command+=" -iname \"$file_iname\" 2>/dev/null"
    fi

    if [[ $find_method == *"-type"* ]]; then
        file_type=$(dialog --inputbox "Enter the file type (f for file or d for dir)." 0 0 2>&1 >/dev/tty)
	if [[ -z "$file_type" ]]; then
            dialog --msgbox "File type cannot be empty." 0 0
            continue
        fi

        find_command+=" -type \"$file_type\" 2>/dev/null"
    fi
    
    if [[ $find_method == *"-size"* ]]; then
        file_size=$(dialog --inputbox "Enter the file size (+num to search more than the num or -num to search less than the num or num  ex.5M megabyte or 5k kilobyte)." 0 0 2>&1 >/dev/tty)
        if [[ -z "$file_size" ]]; then
            dialog --msgbox "File size cannot be empty." 0 0
            continue
        fi

	find_command+=" -size \"$file_size\" 2>/dev/null"
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
    clear
    gum spin --spinner dot --title " Searching..." -- sleep 5
    

   



    # Execute the find command
    results=$(eval "$find_command")
    echo "$results" > /tmp/find_results.txt
    results_file="/tmp/find_results.txt"
    
    selected_file=$(mktemp)
    
    cat "$results_file" | while read -r path; do
    echo -e "\033]8;;file://$path\a$path\033]8;;\a"
    done | gum choose --no-limit --header="Select files to open (Enter to confirm)" > "$selected_file"
    
    # Open selected files
    while read -r path; do
        if [[ -e "$path" ]]; then
            case "$(uname -s)" in
                Darwin*)  # macOS
                    open -R "$path"  # Reveal in Finder
                    ;;
                Linux*)   # Linux
                    xdg-open "$(dirname "$path")" &  # Open containing folder
                    ;;
                *)
                    echo "Unsupported OS"
                    ;;
            esac
        else
            gum style --foreground 196 "Path not found: $path"
        fi
    done < "$selected_file"
    
    rm "$selected_file"

   
    clear


#============================================================================================================================================




    #MacOS section
    else 
    loca=$(gum choose --header="$(gum style --foreground 212 "WHERE TO SEARCH?")" \
        --cursor="→ " --selected.foreground=212 --limit=1 \
        "/ : Root directory" \
        "/Users : All users' home" \
        "/Library : The library directory" \
        "Exit : Quit program")

    # Handle selection
    case $loca in
        *Root*) loca="/" ;;
        *All*) loca="/Users" ;;
        *Library*) loca="/Library" ;;
        *Exit*) 
            gum confirm "Really exit?" && { clear; exit; } || continue
            ;;
        *) 
            gum style --foreground 196 "No location selected"
            sleep 1
            continue
            ;;
    esac

    # Method selection
    gum style --foreground 212 "SELECT SEARCH METHODS (SPACE to select, ENTER to confirm)"
    methods=$(gum choose --no-limit \
    "Name: Search by filename" \
    "Type: Search by file type" \
    "Size: Search by file size" \
    "Readable: Search readable files" \
    "Writable: Search writable files" \
    "Executable: Search executable files")

[[ -z "$methods" ]] && {
    gum style --foreground 196 "No methods selected"
    sleep 1
    continue
}

# Build find command
find_args=("$loca")
conditions_added=0


   if [[ "$methods" == *"Name"* ]]; then
   name=$(gum input --placeholder "Enter filename pattern (e.g., *.txt)" --prompt.foreground=212)
    neglect=$(gum choose --header="Do you want to neglect the captlaization" --cursor="→ " --limit=1 \
        "Yes" "No")
    [[ -n "$neglect" ]] && {
        name+="*"
        [[ "$neglect" == "Yes" ]] && find_args+=(-iname "$name")
        [[ "$neglect" == "No" ]] && find_args+=(-name "$name")
        ((conditions_added++))
    }
fi

if [[ "$methods" == *"Type"* ]]; then
    type=$(gum choose --header="SELECT FILE TYPE" --cursor="→ " --limit=1 \
        "File" "Directory")
    [[ -n "$type" ]] && {
        [[ "$type" == "File" ]] && find_args+=(-type f)
        [[ "$type" == "Directory" ]] && find_args+=(-type d)
        ((conditions_added++))
    }
fi


    if [[ "$methods" == *"Size"* ]]; then
        size=$(gum input --placeholder "Enter size (e.g., +1M, -500k)" --prompt.foreground=212)
        [[ -n "$size" ]] && {
            find_args+=(-size "$size")
            ((conditions_added++))
        }
    fi


    if [[ "$methods" == *"Readable"* ]]; then
            find_args+=(-readable)
            ((conditions_added++))

    fi

    if [[ "$methods" == *"Writable"* ]]; then
            find_args+=(-writable)
            ((conditions_added++))

    fi

    if [[ "$methods" == *"Executable"* ]]; then
            find_args+=(-executable)
            ((conditions_added++))

    fi



 # Execute search
    if (( conditions_added > 0 )); then
        gum spin --spinner dot --title " Searching..." -- sleep 1
        results=$(find "${find_args[@]}" 2> >(grep -v "Permission denied" >&2))

        if [[ -z "$results" ]]; then
            gum style --foreground 196 "No files found matching your criteria"
            sleep 2
        else
            echo "$results" > /tmp/find_results.txt
            results_file="/tmp/find_results.txt"
    
    # Create a temporary file for selected items
            selected_file=$(mktemp)
    
    # Display results with gum choose (for interactive selection)
    cat "$results_file" | while read -r path; do
        # Make paths clickable (terminal escape codes)
        echo -e "\033]8;;file://$path\a$path\033]8;;\a"
    done | gum choose --no-limit --header="Select files to open (Enter to confirm)" > "$selected_file"
    
    # Open selected files
    while read -r path; do
        if [[ -e "$path" ]]; then
            case "$(uname -s)" in
                Darwin*)  # macOS
                    open -R "$path"  # Reveal in Finder
                    ;;
                Linux*)   # Linux
                    xdg-open "$(dirname "$path")" &  # Open containing folder
                    ;;
                *)
                    echo "Unsupported OS"
                    ;;
            esac
        else
            gum style --foreground 196 "Path not found: $path"
        fi
    done < "$selected_file"
    
    rm "$selected_file"

        fi
    else
        gum style --foreground 196 "No search criteria specified"
        sleep 1
    fi

fi
done
