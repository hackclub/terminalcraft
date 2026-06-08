# Git Log
terminalcraft submission

## Description
This is an app that allows you to create logs in terminal. This is helps if you are working on a project and want a consistent log or journal. It can be used as a devlog showing important events and when they occurred.

## Installation

### Windows
1. clone the repo by running this in terminal

```
git clone https://github.com/BoaN235/GitLog.git
```

2. install dependencies by running this in terminal
```
pip install -r requirements.txt
```
### Linux
1. clone the repo by running this in terminal

```
git clone https://github.com/BoaN235/GitLog.git
```

2. create a virtual env 
```
python -m venv GitLog
```

3. install dependencies to the virtual env
```
GitLog/bin/pip install -r requirements.txt
```

5. activate the virtual env
```
source GitLog/bin/activate
```

6. when finished using the application run this to close the virtual env
```
deactivate 
```

### MacOS

Not Currently tested

### Running the Script

1. run the script
```
python gitlog.py
```

2. get your github access token and input it when ask for it
    - go to the github page at [github.com](https://github.com/)
    - click on your profile
          ![image](https://github.com/user-attachments/assets/caf7b4aa-830f-4c1a-9820-8f9fcff9888b)
    - click settings
          ![image](https://github.com/user-attachments/assets/a43da35e-7cae-4462-a91a-af7095556f40)
    - scroll to find developer settings
          ![image](https://github.com/user-attachments/assets/8f4f6b57-ee5d-445e-b9aa-395ab70768dc)
    - click Personal access tokens
          ![image](https://github.com/user-attachments/assets/a1a1b54d-bfea-4efa-b645-5e71c5549cd1)
    - click Tokens (classic)
          ![image](https://github.com/user-attachments/assets/73bc8f72-7516-41eb-8c03-84ee7a737d99)
    - generate new token (classic)
          ![image](https://github.com/user-attachments/assets/ab16e282-2685-4bd7-8985-1e84f0a6f4b8)
    - write "for GitLog" in the notes
          ![image](https://github.com/user-attachments/assets/67b374df-1bd0-4a24-995e-d808fb0561f0)
    - select repo in scopes
          ![image](https://github.com/user-attachments/assets/967e9478-2b67-4858-af9e-ee0de7bcffaf)
    - scroll to the bottom and click generate token
          ![image](https://github.com/user-attachments/assets/5bce4c5e-3b0a-475b-b0ea-ebfcd2b732ea)
    - copy the token
          ![image](https://github.com/user-attachments/assets/70401201-1c58-48ca-aa8f-fa6ccb2b480d)
    - input it into the terminal
    ```
    please input your github access token:

    your-token-here

    ```

## creating a log
      You will be asked which menu option 

      ```
            welcome to GitLog: your-current-repo


            1) Create Log 
            2) Set Current Repo 
            3) Update Repo Data 
            4) Setup 
            5) close
      ```
      1. Update Repo Data
      doing this will get your github repos

      2. set current repo
      input the number for whichever repo you want

      ```
      Which repo would you like to add a log file to
      0) user/repo-name
      1) user/repo-name
      2) user/repo-name
      3) user/repo-name
      4) user/repo-name
      Which repo would you like to add a log file to
      ```
      3. create a log
      enter 1 in the menu to generate a log

      4. input title

      ```
      input title:
      your-title-here
      ```
      
      5. input log

      ```
      input log:
      input-your-log-here
      ```

      You have successfully created a log.

## Next Steps
- allowing you to send images with a log
