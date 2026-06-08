![DreamShell](https://github.com/rinogodson/DreamShell/blob/main/banner.png?raw=true)
# DreamShell
It is an amazing CLI apps to write your dream journals in a retro cybercore-y way... ;)

## Installation
For Linux/MacOS:
```
sudo curl -sL https://github.com/rinogodson/DreamShell/releases/latest/download/install.sh | bash
```
On Linux, run this after installation:
```
echo "export PATH=\"$HOME/.local/bin:$PATH\"" >> ~/.bashrc; source ~/.bashrc
```
No Windows Support (FileSystem Sucks)

Commands:
1. `new` to create a new dream
2. `list` to get list

## `new` command
To create a new dream, type `new` and follow the instructions, add a title, tags and write your dream. The date will be automatically added and the dream log will be saved in `~/.dreamshell/dreams/`

## `list` command
To get list of dreams, type `list`. Select the log from the list view and get a preview of it.

HELP:
Ctrl + i for help            
Ctrl + w to log the dream    
Ctrl + n for next pane       
Ctrl + b for previous pane   
Ctrl + x to exit             
                             
Tags Syntax:                 
  #tag1 #tag2 ... #tagn      
                             
  add #lucid if it was lucid 

