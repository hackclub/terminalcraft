# CLI Instruments

A collection of virtual musical instruments with colorful interactive UI that you can play in your terminal.

![CLI Instruments](https://i.imgur.com/example.png)

## Requirements

- Windows operating system (uses the `winsound` module)
- Python 3.x
- Colorama package (for colored terminal output)

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Available Instruments

### 1. Piano
- Play individual notes on a virtual piano keyboard
- Uses keyboard keys to simulate piano keys (white and black keys)
- Visual feedback with keys highlighted when pressed

### 2. Guitar
- Play guitar chords with a strumming effect
- Each key plays a different chord (E minor, E major, A minor, etc.)
- Visual feedback when strumming

### 3. Drums
- Play a virtual drum kit with various percussion sounds
- Each key corresponds to a different drum or cymbal
- Visual feedback when drums are hit

## How to Play

1. Run the main program with:
   ```
   python cli_instruments.py
   ```

2. Select an instrument from the colorful menu by entering the corresponding number.

3. Use the keyboard keys shown on screen to play the selected instrument.

4. Press ESC to return to the main menu.

5. Select 'q' from the main menu to quit the program.

## Individual Instruments

You can also run each instrument directly:

- Piano: `python piano.py`
- Guitar: `python guitar.py`
- Drums: `python drums.py`

## Controls

### Piano
```
  W E   T Y U    (Black keys)
 A S D F G H J K  (White keys)
```

### Guitar
```
A = Em   S = E    D = Am   F = A
G = D    H = Dm   J = C    K = Cm   L = E7
```

### Drums
```
K = Crash cymbal    L = Ride cymbal
G = Tom 1           H = Tom 2
J = Tom 3
D = Hi-hat closed   F = Hi-hat open
S = Snare
A = Kick drum
``` 