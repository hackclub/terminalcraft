# Terminal-Helper
An AI tool that you can use inside the terminal to get help with commands and errors

## Demo

https://github.com/user-attachments/assets/593f412f-968e-4eda-8cdb-19e96acfc611

## Installation & Setup
1. Clone this repository 
```bash
git clone https://github.com/Outdatedcandy92/Thelper.git
```
2. cd into the repository
```bash 
cd Thelper
```
3. Install requirements
```bash
pip install -r requirements.txt
```
4. Make `thelper` executeable 
```bash
chmod +x thelper
```
## Add thelper to path
### For Linux and Mac

1. move it do a directory in your $PATH
```bash
sudo mv thelper /usr/local/bin/
```

### For Windows

1. Press Windows + S and search for Environment Variables.
2. Click Edit the system environment variables.
3. In the System Properties window, click Environment Variables.
4. Under User variables, select the Path variable and click Edit....
4. Click New and add the folder where thelper.bat is located (e.g., C:\Users\YourUsername\path_to\your_project_folder).
6. Click OK to close all windows.


## Usage

1. Run thelper to setup
```bash
> thelper
```
This will run the setup process for you  to get the API key go to [this link](https://ai.google.dev/gemini-api/docs/api-key).  
Complete the inital setup process

### Arguments


```bash
thelper -h #help command
thelper <your question> #Ask AI about your problem
thelper -i #Initlize setup again
thelper -s #Prints current settings
thelper -e #uses the copied error message and sends it to the Ai
thelper -c #copies the outputted command to your clipboard
```
