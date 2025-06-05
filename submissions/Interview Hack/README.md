Hack Interview is a program in which you can answer questions asked in programming interviews.

![Captura de pantalla 2025-06-03 174403](https://github.com/user-attachments/assets/1fb55b4d-dfac-4d3c-91da-d80653b99fa7)



The program can help you improve your interview skills in the workplace.

✅ Step-by-Step Guide to Run the Interview Simulator on Windows
1. Install Python (if not already installed)
Go to: https://www.python.org/downloads/windows/

Download and install Python (make sure to check the box that says “Add Python to PATH” during installation).

2. Open Command Prompt (CMD) or Windows Terminal
Press Win + R, type cmd or wt, and press Enter.

3. Create a New Folder for Your Project (Optional)
mkdir interview_simulator
cd interview_simulator

4. Create the Python File
Open Notepad or VS Code.
Paste your Python code.
Save the file as: simulator.py

5. Install Required Python Packages
Run the following command to install all necessary libraries:
pip install pyfiglet termcolor rich

6. Run the Program
Now execute your program with:
python simulator.py



✅ Step-by-Step Guide to Run the Interview Simulator on Linux
1. Open a Terminal
You can press:
Ctrl + Alt + T, or
Search for "Terminal" in your applications menu.

2. Make Sure Python is Installed
Most Linux distributions come with Python pre-installed. To check:
python3 --version
If not installed:
sudo apt install python3  # For Debian/Ubuntu
sudo dnf install python3  # For Fedora
sudo pacman -S python     # For Arch

3. Install pip (if not installed)
sudo apt install python3-pip  # Debian/Ubuntu

4. Create a Project Directory
mkdir interview_simulator
cd interview_simulator

5. Create the Python File
Use any editor you like:
nano simulator.py
Paste your code.
Press Ctrl + O to save, then Enter.
Press Ctrl + X to exit.

6. Install Required Python Packages
pip3 install pyfiglet termcolor rich

7. Run the Script
python3 simulator.py
📝 Optional: Make the Script Executable
Add this at the very top of your file:
#!/usr/bin/env python3
Then in terminal:
chmod +x simulator.py
./simulator.py



✅ Step-by-Step Guide to Run the Interview Simulator on macOS
1. Open Terminal
Press Command + Space to open Spotlight.
Type Terminal and hit Enter.

2. Check if Python is Installed
macOS comes with Python 2.x preinstalled, but you should use Python 3.
Check version:
python3 --version
If not installed or outdated, install it via Homebrew:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python

3. Create a Project Folder
mkdir interview_simulator
cd interview_simulator

4. Create the Python File
Use any text editor like nano, vim, or Visual Studio Code:
nano simulator.py
Paste your code inside.
Save with Ctrl + O, press Enter.
Exit with Ctrl + X.

5. Install Required Python Packages
pip3 install pyfiglet termcolor rich

6. Run the Program
python3 simulator.py
🛠 Optional: Make it Executable
Add this as the first line in your script:
#!/usr/bin/env python3
Make it executable:
chmod +x simulator.py
Then run it like this:
./simulator.py
✅ Tip: Keep the Terminal Open After It Ends
If running the script by double-clicking or via .command file, add this at the bottom of your script:
input('\nPress Enter to exit...')
