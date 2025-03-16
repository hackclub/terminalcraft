# Terminal-Games

This is a compendium of quick fun games to play in the terminal. It comes with a wide variety of built-in games, including multiple popular games like PacMan and Wordle. It is fully functional and extremely easy to use!

## Features

- Easy to use
- Variety of games 
- Comes with a clean CLI interface

## Technologies Used

This console application uses 2 main technologies on the front end, [Python 3.11] and the [simple-colors] module, but uses lots of different technologies in the background like the keyboard module (to take user input in a more intuitive manner). Also, the PacMan games is a copy of the game from [this] repository as no compendium of terminal games would be complete without it, so go give that repo a star ;)


## Installation

Install the repository and the following packages and you are good to go!
```sh
pip install -r .\requirements.txt
```

## Execution
To run the app, navigate to the directory of installation. From there open it in terminal and type:
```sh
py -3 main.py
```
Then follow the on-screen instructions to enjoy

## <span style="color:#FF0000;">WARNING</span> 

The keyboard module used in the CLI is very dangerous and therefore I recommend that you do not allow this script to run in the background as it will record all keystrokes while the script is running. It will also press keys like "backspace" to try and counteract the effects of keys being stored in the RAM. This can be dangerous if you are not in the terminal window as this can delete your work!

## Development

Want to contribute? Great! Pull requests and issues are welcome! [Here] is an excellent guide on how to create pull requests and forks to request changes. I suggest using the addon "Better Comments" on Visual Studio Code as it makes the comments more readable. If you can not use the addon, I have used the following tags to make the comments more readable:

- #todo: This is a todo
- #*: This explains the code
- #!: This is a warning

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job.)

   [Python 3.10]: <https://www.python.org/downloads/release/python-3109/>
   [simple-colors]: <https://pypi.org/project/simple-colors/>
   [Here]: <https://www.dataschool.io/how-to-contribute-on-github/>
   [this]: <https://github.com/atharva-malik/Terminal-Pacman>
