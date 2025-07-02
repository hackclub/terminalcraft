# Terminal Procedural Art Generator

A tool that generates beautiful procedural art animations in your terminal. Choose from multiple art modes for different visual experiences.

## Features

- 13 unique procedural art generators
- Interactive menu for easy selection
- Direct command line access to specific animations
- Dynamic resizing based on your terminal dimensions
- Smooth animations with rich colors (where terminal supports it)

## Available Art Modes

- **Matrix**: Classic digital rain effect with falling characters.
- **Particle Explosion**: Dynamic particle physics with colorful explosions.
- **Infinite Zoom**: A mesmerizing fractal zoom into the Mandelbrot set.
- **Digital Rain**: Falling Katakana characters reminiscent of the Matrix.
- **Voronoi Diagram**: Generates intricate cellular patterns with dynamic cells.
- **Kaleidoscope**: Symmetrical and repeating visual patterns that evolve over time.
- **Day/Night Cycle**: Simulates a changing sky with smooth color transitions.
- **Forest Simulation**: A growing and evolving forest with trees and falling leaves.
- **Sea Waves**: Calming ocean wave animations with depth and movement.
- **Game of Life**: Conway's classic cellular automaton with emergent patterns.
- **Spinning 3D Cube**: A rotating 3D cube rendered in ASCII characters.
- **Random Walkers**: Simple agents that move randomly, leaving colorful trails.
- **Rain**: A simple rain simulation with falling droplets.

## Installation

1. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Interactive Mode

Run the application without arguments to use the interactive menu:
```bash
python main.py
```

Use the number keys to select an art mode, or 'Q' to quit.

### Command Line Usage

Run a specific art mode directly from the command line:

```bash
python main.py <art-mode>
```

For example:
```bash
python main.py digital-rain
```

Available art mode identifiers:
- `matrix`
- `particle-explosion`
- `infinite-zoom`
- `digital-rain`
- `voronoi`
- `kaleidoscope`
- `day-night-cycle`
- `forest`
- `sea-waves`
- `game-of-life`
- `spinning-cube`
- `random-walkers`
- `rain`

To see a list of all available art modes:
```bash
python main.py --list
```

## Controls

- Press `Ctrl+C` to exit the current animation and return to the menu
- In interactive mode, press `Q` to quit the application

## Requirements

- Python 3.6+
- Terminal with color support (for best experience)
- Minimum terminal size of 80x24 characters (larger recommended)

## Dependencies

- rich: Terminal formatting and rendering
- numpy: Numerical operations for animations
- questionary: Interactive command-line interface
- scipy: Advanced mathematical functions (used by some generators)

## Contributing

Contributions are welcome! Feel free to add new art generators or improve existing ones.

1. Fork the repository
2. Create a new branch for your feature
3. Add your changes
4. Submit a pull request
