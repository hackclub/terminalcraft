# simulator3000
![image](https://github.com/user-attachments/assets/31257258-f373-4359-bd6c-0596795be8ea)
(sorry for the name, projekcik is just the shortened form of project in polish, at the beginning I did not realle know in which way it would evolve)

## Overview

The Terminal Particle Simulator is an advanced physics simulation that runs entirely within your terminal. It models complex particle interactions using realistic physics principles including gravity, electrostatics, magnetism, drag forces, and spring connections. The simulator features:

- Real-time particle physics with collision detection
- Multiple force types that can be toggled during simulation
- Three boundary condition modes (reflective, periodic, infinite)
- Particle trails for visualizing movement history
- Interactive controls for manipulating simulation parameters
- Color-coded particles with physical properties (mass, charge)

This project was developed to demonstrate that complex physics simulations can run effectively in a terminal environment without graphical windows. The implementation required significant research into physics modeling and terminal rendering techniques.

## Features

- **Advanced Physics Engine**:
  - Gravitational forces with adjustable constant
  - Electrostatic forces (Coulomb's law)
  - Magnetic forces (Lorentz force in 2D)
  - Drag forces with configurable coefficient
  - Spring forces between particles
  - Elastic collisions with restitution
  - Multiple boundary conditions

- **Visualization**:
  - Colored particles (8 terminal colors)
  - Particle trails showing movement history
  - Real-time statistics display
  - Interactive control reference

- **Controls**:
  - Toggle forces during simulation
  - Adjust simulation speed
  - Add new particles dynamically
  - Pause/resume simulation
  - Toggle particle trails

## Requirements

- **Platform**: Linux (tested on Ubuntu 20.04+, Fedora, Arch)
- **Python**: 3.6 or higher
- **Terminal**: Supports UTF-8 characters and 256 colors (GNOME Terminal, Konsole, Terminator, Alacritty recommended)

No external Python packages are required - everything uses the standard library.

## Installation & Running

1. Clone or download the project files
2. Navigate to the project directory
3. Run the simulator:

```bash
python3 main.py
```

### Command-line Options

```bash
python3 main.py [options]

Options:
  --gravity FLOAT   Set gravitational constant (default: 0.1)
  --k FLOAT         Set electrostatic constant (default: 5.0)
  --drag FLOAT      Set drag coefficient (default: 0.01)
```

## Controls

| Key | Function |
|-----|----------|
| `Space` | Pause/resume simulation |
| `g` | Toggle gravity |
| `e` | Toggle electrostatic forces |
| `m` | Toggle magnetic forces |
| `d` | Toggle drag forces |
| `b` | Cycle boundary conditions |
| `t` | Toggle particle trails |
| `s` | Toggle statistics display |
| `+` | Increase simulation speed |
| `-` | Decrease simulation speed |
| `a` | Add new particle |
| `q` | Quit simulator |

## Why I Created This

I developed this particle simulator to:
1. Demonstrate that complex physics simulations can run effectively in terminal environments
2. Create an educational tool for visualizing fundamental physics principles
3. Challenge myself to implement realistic physics in a constrained environment
4. Provide a visually appealing alternative to graphical simulations
5. Explore the capabilities of Python's curses library for terminal applications

The project required significant research into:
- Physics modeling (Newtonian mechanics, electromagnetism)
- Numerical integration methods
- Collision detection and resolution algorithms
- Terminal rendering techniques and optimizations

Special thanks to the following resources that helped overcome implementation challenges:
- Physics for Game Developers (O'Reilly)
- Real-Time Collision Detection (Morgan Kaufmann)
- Python curses documentation
- Numerous physics and mathematics StackExchange discussions

## Known Limitations

- Performance may degrade with >100 particles on slower systems
- Terminal rendering artifacts may occur with very fast particles
- Magnetic forces are simplified to 2D approximation
- Spring connections may become unstable at high speeds

## Contribution

This project is open to contributions! If you'd like to:
- Report bugs
- Suggest improvements
- Add new features
- Optimize performance

Please feel free to create issues or submit pull requests.
