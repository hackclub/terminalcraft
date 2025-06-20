# TerminalTalks

TerminalTalks is an offline, voice-powered command suggestion tool for Linux. Speak natural phrases like “list files” or “check IP,” and it will suggest the appropriate terminal command, such as `ls` or `ip a`. Designed for quick use, it's especially helpful for those who forget common commands or want to explore Linux hands-free.

------------------------------------------------------------

FEATURES

- Works completely offline (no internet required after setup)
- Supports Indian English accent using Vosk STT model
- Maps speech to 150+ common Linux commands
- Simple one-command install script
- Easy to modify and expand command set
- Beginner-friendly, works on most Linux systems

------------------------------------------------------------

HOW IT WORKS

1. You run the command `terminal-talks` from any terminal.
2. It starts listening to your voice using the default microphone.
3. Speech is transcribed locally using the Vosk model.
4. It searches for a matching command in its mapping dictionary.
5. The best-matching Linux command is shown as output.
6. You can copy and run it manually.

Example:

You say: “list all files”  
It shows: Suggested command: `ls -a`

------------------------------------------------------------

INSTALLATION

NOTE: Before installing, you must manually download the offline model due to file size.

STEP 1 — Download the Speech Recognition Model:

- Visit: https://alphacephei.com/vosk/models
- Download: vosk-model-en-in-0.51
- Extract the folder
- Rename the folder to: model
- Move this folder into the TerminalTalks project directory

Your final folder structure should look like:

TerminalTalks/
├── install.sh
├── terminal-talks
├── requirements.txt
├── README.md
└── model/
    └── vosk files...

STEP 2 — Run the Install Script:

Make sure you're inside the `TerminalTalks` folder:

```bash
chmod +x install.sh
./install.sh
```
What this does:

Installs all Python packages listed in requirements.txt
Creates a global command terminal-talks accessible from any directory

STEP 3 — Use the Tool:

After installation:

terminal-talks

Say something like “make a folder”It shows: Suggested command: mkdir

EXAMPLES OF SUPPORTED COMMANDS

You Say                      →  Suggested Command

"list files"                →  ls"show all files"            →  ls -a"make a folder"             →  mkdir"remove a directory"        →  rm -r"check IP address"          →  ip a"what’s my current path"    →  pwd"clear the screen"          →  clear"view running processes"    →  top

More than 150 phrases are supported.

REQUIREMENTS

Python 3.7+

Linux-based system (Ubuntu, Arch, Debian, etc.)

Working microphone input

~1 GB free space for the speech model

TESTED ON

Ubuntu 22.04 ✅

Arch Linux ✅

Debian 12 ✅

Tested by 3 users on various machines.

BUILT FOR

This project was built for Hack Club’s TerminalCrafthttps://terminalcraft.hackclub.dev


CONTACT

Created by Sameer KulhariGitHub: https://github.com/sameer-kulhariRepository: https://github.com/sameer-kulhari/TerminalTalks
