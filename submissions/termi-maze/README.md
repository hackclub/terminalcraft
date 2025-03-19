# TermiMaze


In TermiMaze, you control a player represented by the `@` symbol. The objective is to navigate through the maze and reach the exit, represented by the `E` symbol. The maze is displayed in the terminal, and you can move the player using the arrow keys. The game also features a loading screen and a winning screen.

## How to Run

To run TermiMaze, you need to have Python installed on your system. Follow these steps for running it with python:

1. Clone the repository or download the source code.
2. Open a terminal and navigate to the directory containing the `main.py` file.
3. Run the following command for installing the required packages:
    ```sh
    pip install -r requirements.txt
    ```
4. Run the game:
    ```sh
    python3 main.py
    ```

Or you can run the executable:  

1. Open the exectuable  

## How to Compile

You can compile TermiMaze into an executable using `pyinstaller`. Follow these steps:

1. Install `pyinstaller` if you haven't already:

    ```sh
    pip install pyinstaller
    ```

2. Navigate to the directory containing the `main.py` file.
3. Run the following command to create a standalone executable:

    ```sh
    pyinstaller --onefile main.py
    ```

4. The executable will be created in the `dist` directory.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.