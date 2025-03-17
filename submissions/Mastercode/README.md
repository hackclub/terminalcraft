# Mastercode

This is a terminal-based password manager and diary application built using the `urwid` library for the user interface and `cryptography.fernet` for encryption. The application allows you to manage passwords, store encrypted diary entries, and configure settings.

## Features

- **Password Management**: Add, view, edit, and delete passwords. Notes aswell!
- **Diary**: Add, view, and delete encrypted diary entries that noone but you can access.
- **Settings**: Configure password generation length and allow/disallow duplicate diary entries.
- **Encryption**: All passwords and diary entries and password notes are encrypted using `cryptography.fernet`.
- **Browser password support**: Supports importing and exporting passwords in csv web browser format. Mastercode thrives in this use case as it can be used for encrypting your passwords and accessing them and re-exporting them again without relying on browser password managers!
- **File navigation**: for importing and exporting files, easy to use.
- **Passy**: A digital cow that shows various funny faces and criticises/compliments your passwords.
- **Mouse compatibility**: Wanna rebell? Go for it, click the menus and buttons with your mouse.
```
 __________________________
< Hey I'm Passy! Keep safe! >
 --------------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
```
## System table
| Operating System | Supported  | Notes               |
|------------------|------------|---------------------|
| Linux            | ✔️         | Fully supported , tested on Ubuntu 24.04, should work on other distros    |
|Windows 11|✔️|Works, Even Windows Terminal works along with  classic cmd.|
| Windows 10       | ✔️         | Works on Python 3.13.2      |
| Windows 7        | ❌         | End of support  , Doesn't work on Python 3.8, urwid is at fault. (console output errors, rust 🦀, dll issues)|
| macOS            | ✔️         | If it works on Linux, should work on here, just use latest python|


## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/MangyCat/Mastercode.git
    cd Mastercode
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```
3. Install without requirements.txt:
    ```sh
    pip install cowsay cryptography urwid
    ```
## Usage

1. Run the application:
    ```sh
    python main.py
    ```