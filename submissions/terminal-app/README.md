# Expense Tracker

A simple command-line expense and income tracker built with Python. It allows users to add and view expenses and income, as well as track total spending per category. This project is inspired by Bagels project.


## Credits & Inspiration
I take this project inspiration from  [Bagels](https://github.com/EnhancedJax/Bagels), a terminal-based project that demonstrated excellent command-line interface design patterns.




## Features
- Add and view expenses
- Add and view income
- Display total spending per category
- Uses CSV files to store data
- User-friendly terminal interface using `rich` and `cursesmenu`

## Bugs
- During exit option, the program does not exit properly.


## Installation

### Windows
1. Clone the repository or download the script:
   ```sh
   git clone https://github.com/arjun654321/terminal-app.git
   cd terminal-app
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```



### Linux
1. Clone the repository:
   ```sh
   git clone https://github.com/arjun654321/terminal-app.git
   cd terminall-app
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```




## Running the Application

### Windows
Run the following command in the terminal:
```sh
python app.py
```



### Linux
Run the following command in the terminal:
```sh
python3 app.py
```
or
```sh
python app.py
```



## Dependencies
The project requires the following Python packages:
```
curses-menu==0.9.0
rich==13.9.4
```
These will be installed automatically when running `pip install -r requirements.txt`.



## How to Use
1. After running the script, you will see a menu with options.
2. Use arrow keys to navigate and select an option.
3. Follow on-screen instructions to add expenses, view records, and analyze spending.
4. Press Enter to confirm actions and continue.



## Contributing
Feel free to fork this repository and make improvements. If you encounter any issues, please open an issue on GitHub.
