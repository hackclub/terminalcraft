# -------------------------💻🎙️ TerminalTalks 🎙️💻 --------------------------

TerminalTalks is an **offline, voice-powered command suggestion tool** for Linux. Speak natural phrases like _"list files"_ or _"check IP,"_ and it will suggest the appropriate terminal command like `ls` or `ip a`. Perfect for when you forget commands or want hands-free Linux exploration!

## ✨ Features  
- 🛜 **Works completely offline** (no internet required after setup)  
- 🇮🇳 Supports **Indian English accent** using Vosk STT model  
- 📋 Maps speech to **150+ common Linux commands**  
- ⚡ **Simple one-command install** script  
- 🔧 Easy to modify and expand command set  
- 🐧 Beginner-friendly, works on most Linux systems  

## 🛠️ How It Works  
1. Run `terminal-talks` from any terminal  
2. It starts listening to your voice 🎤  
3. Speech is transcribed locally using Vosk  
4. Searches for matching command in its dictionary  
5. Shows the best Linux command match  
6. Copy and run it manually  

**Example:**  
🎤 You say: _"list all files"_  
💻 It shows: `Suggested command: ls -a`  

## 📥 Installation  
> **Note:** Before installing, you must manually download the offline model due to file size.  

### Step 1 — Download Speech Recognition Model  
1. Visit: [https://alphacephei.com/vosk/models](https://alphacephei.com/vosk/models)  
2. Download: `vosk-model-en-in-0.51`  
3. Extract and rename folder to `model`  
4. Place in TerminalTalks project directory  

### Step 2 — Run Install Script  
```bash  
chmod +x install.sh  
./install.sh
```
Step 3 — Use the Tool
```bash
terminal-talks  
```
Try saying: "make a folder" → Shows: Suggested command: mkdir

## 📚 Example Commands

| You Say                      | Suggested Command  |
|------------------------------|--------------------|
| "list files"                 | `ls`               |
| "show all files"             | `ls -a`            |
| "make a folder"              | `mkdir`            |
| "remove a directory"         | `rm -r`            |
| "check IP address"           | `ip a`             |
| "what's my current path"     | `pwd`              |
| "clear the screen"           | `clear`            |
| "view running processes"     | `top`              |

*Over 150 phrases supported!*

## ⚙️ Requirements

- Python 3.7+
- Linux-based system (Ubuntu, Arch, Debian, etc.)
- Working microphone
- ~1 GB free space for model

## ✔️ Tested On

- Ubuntu 22.04 ✅
- Arch Linux ✅
- Debian 12 ✅
## 🚀 Built For
This project was built for Hack Club's TerminalCraft 🛠️

## 📬 Contact
Created by Sameer Kulhari
GitHub Repository : https://github.com/Sameer-Kulhari/TerminalTalks

💡 Pro Tip: Add your own custom commands by editing the mapping dictionary!
