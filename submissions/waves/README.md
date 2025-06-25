# Wave on String Simulation - Terminal Version

A physics simulation of wave propagation on a string with real-time interactive controls, rendered entirely in the terminal using ASCII art and dot-based visualization.

## Features

- **Wave Generation Modes**:
  - **Pulse**: Single wave pulse that travels along the string
  - **Oscillate**: Continuous sinusoidal wave generation
  - **Manual**: Real-time manual control with keyboard input

- **Interactive Parameters** (adjustable in real-time):
  - Wave amplitude
  - Pulse width/frequency
  - Damping (None/Lots)
  - String tension (Low/High)
  - Boundary conditions (Fixed End/Loose End/No End)

- **Visual Elements**:
  - Smooth ASCII art wave visualization using dots (., o, *, #)
  - Real-time simulation timer
  - Amplitude rulers and scales
  - Zero reference line
  - Live parameter display
  - Wave energy and frequency monitoring
  - FPS counter

- **Advanced Features**:
  - Anti-flicker optimized rendering
  - Slow motion mode
  - Wave disturbance injection
  - Preset save/load functionality
  - Real-time wave statistics

## Installation

Install the required dependency:

```bash
pip install -r requirements.txt
```

## Usage

Run the simulation:
```bash
python wave_simulation.py
```

## Interactive Controls

During simulation, use these keyboard controls:

| Key | Action |
|-----|--------|
| **SPACE** | Pause/Resume simulation |
| **Q** | Quit simulation |
| **R** | Restart simulation |
| **M** | Cycle through modes (Pulse → Oscillate → Manual) |
| **A/S** | Increase/Decrease amplitude |
| **W/E** | Increase/Decrease pulse width |
| **F/G** | Adjust frequency (faster/slower) |
| **D** | Toggle damping (None ↔ Lots) |
| **T** | Toggle tension (Low ↔ High) |
| **B** | Cycle boundary conditions (Fixed → Loose → No End) |
| **L** | Toggle slow motion mode |
| **U** | Toggle rulers on/off |
| **V** | Toggle reference line on/off |
| **I/K** | Manual control up/down (Manual mode only) |
| **Z** | Zero out the wave |
| **X** | Add random disturbance |
| **C** | Clear wave history |
| **P/O** | Save/Load preset |

## Wave Visualization

The simulation uses ASCII characters to create smooth wave curves:
- `#` - Wave peaks (highest intensity)
- `*` - High amplitude regions
- `o` - Medium amplitude regions
- `.` - Low amplitude regions
- `,` - Very small oscillations
- `-` - Zero reference line
- ` ` - Empty space

## Wave Physics

The simulation accurately models the 1D wave equation:
```
∂²y/∂t² = c²(∂²y/∂x²) - γ(∂y/∂t)
```

Where:
- `y` is displacement
- `c` is wave speed (depends on tension)
- `γ` is damping coefficient

### Boundary Conditions

1. **Fixed End**: Wave reflects with phase inversion (like a string tied to a wall)
2. **Loose End**: Wave reflects without phase change (like a free end)
3. **No End**: Absorbing boundary with no reflection (infinite string)

### Real-time Monitoring

The simulation displays:
- Current wave amplitude
- Total wave energy
- Dominant frequency
- Simulation time
- Frame rate (FPS)

## Usage Examples

### Getting Started
1. Run: `python wave_simulation.py`
2. Watch the initial pulse propagate
3. Press **SPACE** to pause and examine the wave
4. Press **M** to try different modes

### Pulse Mode
- Creates a single wave pulse that travels along the string
- Great for observing basic wave propagation and reflection
- Adjust amplitude (**A/S**) and pulse width (**W/E**)

### Oscillate Mode  
- Continuous sinusoidal wave generation
- Perfect for studying wave interference and standing waves
- Experiment with frequency (**F/G**) and observe patterns

### Manual Mode
- Real-time interactive wave control
- Use **I/K** keys to create custom wave shapes
- Great for understanding wave sources and superposition

## Educational Applications

This simulation is perfect for:
- **Physics Education**: Demonstrating wave mechanics principles
- **Interactive Learning**: Hands-on exploration of wave behavior
- **Boundary Condition Studies**: Comparing different end conditions
- **Wave Interference**: Observing how waves interact
- **Energy and Damping**: Understanding wave energy dissipation

## Technical Features

- **Anti-flicker rendering**: Optimized for smooth terminal display
- **Real-time physics**: Accurate finite difference wave equation solver
- **Responsive controls**: Immediate parameter adjustment
- **Cross-platform**: Works on Windows, macOS, and Linux terminals
- **Performance optimized**: Efficient ASCII rendering and calculation caching
