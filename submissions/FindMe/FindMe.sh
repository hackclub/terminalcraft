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
#Debian reqiuerments
deb-req() {
        if ! command -v figlet &> /dev/null; then
        sudo apt-get install -y figlet  || exit 1
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
    if ! command -v gum &> /dev/null; then
        sudo apt install gum
    fi
}
#Arch requerments
arch-req() {

    if ! command -v figlet &> /dev/null; then
        sudo pacman -S --noconfirm figlet || exit 1
    fi
    if ! command -v dialog &> /dev/null; then
        sudo pacman -S --noconfirm dialog || exit 1
    fi
    if ! command -v boxes &> /dev/null; then
        if command -v yay &> /dev/null; then
     	yay -S --noconfirm boxes || exit 1
     	elif command -v paru &> /dev/null; then
        paru -S --noconfirm boxes || exit 1
	else
 	echo "Error: No AUR helper (yay/paru) found. Please install one first."
        exit 1
	fi
    fi
    if ! command -v lolcat &> /dev/null; then
        if command -v yay &> /dev/null; then
     	yay -S --noconfirm lolcat || exit 1
     	elif command -v paru &> /dev/null; then
        paru -S --noconfirm lolcat || exit 1
	else
 	echo "Error: No AUR helper (yay/paru) found. Please install one first."
        exit 1
	fi
    fi
    if ! command -v gum &> /dev/null; then
        if command -v yay &> /dev/null; then
     	yay -S --noconfirm gum || exit 1
     	elif command -v paru &> /dev/null; then
        paru -S --noconfirm gum || exit 1
	else
 	echo "Error: No AUR helper (yay/paru) found. Please install one first."
        exit 1
	fi
    fi
}
#Opensus requeirments
suse-req() {
    if ! command -v figlet &> /dev/null; then
        sudo zypper install -y figlet || exit 1
    fi
    if ! command -v dialog &> /dev/null; then
        sudo zypper install -y dialog || exit 1
    fi
    if ! command -v boxes &> /dev/null; then
        sudo zypper install -y boxes || exit 1
    fi
    if ! command -v lolcat &> /dev/null; then
        sudo zypper install -y lolcat || exit 1
    fi
    if ! command -v gum &> /dev/null; then
        echo "Gum not in repos, installing manually..."
        curl -LO https://github.com/charmbracelet/gum/releases/latest/download/gum_0.13.0_linux_amd64.rpm
        sudo rpm -i gum_*.rpm || exit 1
        rm gum_*.rpm
    fi
}
#Fedora and RedHat and CentOS requeirments
rpm-req() {
    if command -v dnf &> /dev/null; then
        PKG_MGR="dnf"
    else
        PKG_MGR="yum"
    fi
    
    sudo $PKG_MGR install -y epel-release
    
    if ! command -v figlet &> /dev/null; then
        sudo $PKG_MGR install -y figlet || exit 1
    fi
    if ! command -v dialog &> /dev/null; then
        sudo $PKG_MGR install -y dialog || exit 1
    fi
    if ! command -v boxes &> /dev/null; then
        sudo $PKG_MGR install -y boxes || exit 1
    fi
    if ! command -v lolcat &> /dev/null; then
        sudo $PKG_MGR install -y lolcat || exit 1
    fi
    if ! command -v gum &> /dev/null; then
        sudo $PKG_MGR install -y gum || {
            echo "Gum not in repos, installing manually..."
            curl -LO https://github.com/charmbracelet/gum/releases/latest/download/gum_0.13.0_linux_amd64.rpm
            sudo rpm -i gum_*.rpm || exit 1
            rm gum_*.rpm
        }
    fi
}

    # Detect distribution
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
    elif [ -f /etc/redhat-release ]; then
        DISTRO="rhel"
    elif [ -f /etc/arch-release ]; then
        DISTRO="arch"
    elif [ -f /etc/SuSE-release ]; then
        DISTRO="suse"
    else
        echo "Unsupported Linux distribution"
        exit 1
    fi

    # Install packages based on distro
    case $DISTRO in
        ubuntu|debian|pop|linuxmint|kali)
            echo "Detected Distro: $DISTRO"
            deb-req ;;
        fedora|rhel|centos|almalinux|rocky)
            echo "Detected Distro: $DISTRO"
            rpm-req ;;
        arch|manjaro|endeavouros)
            echo "Detected Distro: $DISTRO"
            arch-req ;;
        opensuse*|sles|sled)
            echo "Detected Distro: $DISTRO"
            suse-req ;;
        *)
            echo "Unsupported distribution: $DISTRO"
            exit 1 ;;
    esac

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
    loca=$(dialog --menu 'choose where to find' 0 0 3 '/' 'Find in the root dir' '/home' 'Find in the home dir for all users' "/home/$(whoami)" 'Find in the current user home dir' 'Custom Location' "Let's you enter a specific location" 'Exit' "Exit the program" 3>&1 1>&2 2>&3)
    if [[ $loca == "Exit" ]]; then
clear        
break
    fi
    if [[ $loca = "Custom Location" ]]; then
    loca=$(dialog --inputbox "Enter the location full PATH" 0 0  2>&1 >/dev/tty)
    che=$(test -e "$loca" && echo "Exists" || echo "invaild PATH")
    fi
    clear
    if [[ -z "$loca" ]]; then
        echo "No location selected. Returning to the beginning..."
        continue
    fi
    if [[ $che = "Exists" || $loca = "/" || $loca = "/home" || $loca = "/home/$(whoami)" ]]; then
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
    done | gum choose --no-limit --header="Select files to open (Space to select, Enter to confirm)" > "$selected_file" 


    
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
    elif [[ $che = "invaild PATH" ]]; then
    echo $che
    sleep 2
    continue
    fi

#============================================================================================================================================




    #MacOS section
    else 
    loca=$(gum choose --header="$(gum style --foreground 212 "WHERE TO SEARCH?")" \
        --cursor="→ " --selected.foreground=212 --limit=1 \
        "/ : Root directory" \
        "/Users : All users' home" \
        "/Library : The library directory" \
        "Custom-Location : Let's you enter a specific location"\
        "Exit : Quit program")

    # Handle selection
    if [[ $loca = "/ : Root directory" ]]; then
        loca="/"
    elif [[ $loca = "/Users : All users' home" ]]; then
        loca="/Users"
    elif [[ $loca = "/Library : The library directory" ]]; then
        loca="/Library"
    elif [[ $loca = "Custom-Location : Let's you enter a specific location" ]]; then 
        loca=$(gum input --placeholder "Enter the location full PATH" --prompt.foreground=212)
        che=$(test -e "$loca" && echo "Exists" || echo "invaild PATH")
    else
        clear
        break
    fi
    
    if [[ $che = "Exists" || $loca = "/" || $loca = "/Users" || $loca = "/Library" ]]; then
    # Method selection
    gum style --foreground 212 "SELECT SEARCH METHODS (SPACE to select, ENTER to confirm)"
    methods=$(gum choose  --no-limit \
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
    done | gum choose --no-limit --header="Select files to open (Space to select, Enter to confirm)"> "$selected_file"
    
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
    elif [[ $che = "invaild PATH" ]]; then
    echo $che 
    sleep 2
    continue
    fi

fi
done
