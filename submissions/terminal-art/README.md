# Terminal Video Simulations

This project contains several Python programs that create video-like simulations and interactive games in the terminal using ASCII characters and the curses library.

## Menu

A menu program is included to easily launch any of the simulations:

```
python menu.py
```

Use the arrow keys to navigate, Enter to select a simulation, and Q to quit.

## Requirements

- Python 3.6 or higher
- curses library (included in standard library for Unix/Linux/macOS; for Windows, install windows-curses)

If you're on Windows, you'll need to install the windows-curses package:

```
pip install windows-curses
```

## Programs

### Basic Simulations

#### 1. Basic Video Simulation

A simple wave-like animation using ASCII characters.

```
python video_terminal.py
```

#### 2. Matrix Effect

A simulation of the famous "digital rain" effect from The Matrix movie.

```
python matrix_terminal.py
```

#### 3. Fire Effect

A simulation of fire using ASCII characters and colors.

```
python fire_terminal.py
```

#### 4. Dancing Man

A simulation of a dancing stick figure with disco lights.

```
python dancing_man.py
```

#### 5. Bouncing Ball

A physics-based simulation of bouncing balls with trails.

```
python bouncing_ball.py
```

#### 6. Dance and Bounce

A combined simulation featuring both the dancing man and bouncing balls.

```
python dance_and_bounce.py
```

#### 7. Starfield

A simulation of flying through space with stars moving toward you.

```
python starfield.py
```

#### 8. Rain

A simulation of rain falling with splashes when raindrops hit the ground.

```
python rain.py
```

#### 9. Conway's Game of Life

An implementation of Conway's Game of Life cellular automaton with interactive controls.

```
python game_of_life.py
```

#### 10. Fireworks Display

A colorful fireworks simulation with rising rockets and particle explosions.

```
python fireworks.py
```

#### 11. Digital Clock

A customizable digital clock with ASCII art digits and various display options.

```
python digital_clock.py
```

### Interactive Games

#### 12. Snake Game

A classic snake game where you control a snake to eat food and grow longer.

```
python snake_game.py
```

#### 13. Typing Test

A typing speed and accuracy test with WPM (words per minute) calculation.

```
python typing_test.py
```

## Controls

### Common Controls
- Press `q` to quit any simulation
- Press `Ctrl+C` to force quit

### Specific Controls

#### Bouncing Ball & Dance and Bounce
- Press `Space` to add a new ball
- Press `+`/`-` to adjust dancing speed (Dance and Bounce only)

#### Dancing Man
- Press `+`/`-` to adjust dancing speed

#### Starfield
- Press `+`/`-` to adjust flying speed

#### Rain
- Press `+`/`-` to adjust rain intensity

#### Conway's Game of Life
- Press `r` to randomize the grid
- Press `c` to clear the grid
- Press `Space` to pause/resume the simulation
- Press `+`/`-` to adjust simulation speed
- Click on cells to toggle their state (if mouse support is available)

#### Fireworks Display
- Press `Space` to manually launch a firework
- Press `+`/`-` to adjust the automatic launch rate

#### Digital Clock
- Press `c` to change the color scheme
- Press `s` to toggle seconds display
- Press `d` to toggle date display
- Press `a` to toggle AM/PM display
- Press `h` to toggle between 12h and 24h format
- Press `r` to toggle rainbow mode
- Press `m` to cycle through animation modes
- Press `*` to toggle background stars

#### Snake Game
- Use arrow keys to control the snake
- Press `r` to restart after game over

#### Typing Test
- Type the displayed text
- Press `ESC` to restart the test

## How It Works

These simulations use the curses library to control the terminal display. Each program:

1. Initializes the terminal screen for drawing
2. Creates a simulation loop that generates frames
3. Renders each frame to the terminal
4. Cleans up the terminal state when exiting

The simulations use different algorithms to create their effects:

- **video_terminal.py**: Uses wave patterns and noise to create a dynamic display
- **matrix_terminal.py**: Creates falling columns of characters that mimic the Matrix digital rain
- **fire_terminal.py**: Uses a cellular automaton approach to simulate fire rising from the bottom of the screen
- **dancing_man.py**: Uses pre-defined ASCII art frames to animate a dancing stick figure
- **bouncing_ball.py**: Uses physics calculations to simulate realistic ball bouncing with gravity
- **dance_and_bounce.py**: Combines the dancing man and bouncing ball simulations
- **starfield.py**: Creates a 3D effect of stars moving toward the viewer
- **rain.py**: Simulates raindrops falling with realistic splash effects
- **game_of_life.py**: Implements Conway's Game of Life cellular automaton with rules for cell birth, survival, and death
- **fireworks.py**: Simulates fireworks with physics for rocket launch, explosion, and particle movement with gravity
- **digital_clock.py**: Displays the current time using ASCII art digits with various display options and animations
- **snake_game.py**: Implements the classic snake game with collision detection
- **typing_test.py**: Measures typing speed and accuracy with real-time feedback

## Customization

You can modify these programs to create your own terminal animations by changing:

- The characters used for display
- The colors (if supported by your terminal)
- The algorithms that generate the patterns
- The speed of the animation

Enjoy the terminal video simulations and games!