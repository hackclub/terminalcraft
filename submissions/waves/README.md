# Wave on String Simulation - Terminal Version

A physics simulation of wave propagation on a string with real-time interactive controls, rendered entirely in the terminal using ASCII art and dot-based visualization.

## About This Project

This simulation implements the mathematical wave equation in real-time, showing how waves travel, reflect, and interact on a vibrating string. Perfect for physics students, educators, and anyone curious about wave mechanics! The entire simulation runs in your terminal with smooth ASCII art rendering and responsive keyboard controls.

**Key Educational Concepts:**
- Wave propagation and reflection
- Boundary condition effects
- Wave interference and superposition
- Energy conservation and damping
- Frequency and amplitude relationships

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

2. **First-time usage:**
   - The simulation starts automatically in **Pulse mode**
   - You'll see a wave pulse traveling along the string
   - The wave reflects when it hits the boundary

3. **Basic controls to try:**
   - Press **SPACE** to pause and resume
   - Press **A** or **S** to increase/decrease wave amplitude
   - Press **M** to cycle through different wave modes
   - Press **Q** to quit

4. **Explore different modes:**
   - **Pulse**: Watch single wave pulses travel and reflect
   - **Oscillate**: See continuous waves and standing wave patterns
   - **Manual**: Control the wave source directly with I/K keys

### Your First Experiments

**Experiment 1 - Wave Reflection:**
1. Start the program (default Pulse mode)
2. Watch the pulse travel and reflect off the fixed end
3. Press **B** to try different boundary conditions
4. Notice how the reflection changes!

**Experiment 2 - Standing Waves:**
1. Press **M** to switch to Oscillate mode
2. Adjust frequency with **F** and **G** keys
3. Find frequencies that create standing wave patterns
4. Try different boundary conditions with **B**

**Experiment 3 - Interactive Control:**
1. Press **M** twice to reach Manual mode
2. Use **I** and **K** keys to create your own waves
3. Try creating multiple pulses or custom patterns
4. Add random disturbances with **X**

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

## Troubleshooting

### Common Issues

**"Import 'numpy' could not be resolved"**
- Solution: Install numpy with `pip install numpy`
- Check your Python interpreter in VS Code (Ctrl+Shift+P → "Python: Select Interpreter")

**Wave is moving too fast**
- Press **L** to enable slow motion mode
- Use **G** to increase pulse width (slower frequency)
- Try **F** to decrease pulse width for faster waves

**Can't see the wave clearly**
- Press **A** to increase amplitude
- Press **U** to toggle rulers if they're cluttering the view
- Try different boundary conditions with **B**
- Maximize your terminal window for better display

**Terminal display issues**
- Ensure your terminal supports ANSI escape sequences
- On Windows: Use PowerShell, Command Prompt, or Windows Terminal
- Try running in a different terminal application
- Some older terminals may not display correctly

**Controls not responding**
- Make sure the terminal window has focus (click on it)
- Try pressing keys more gently (avoid holding them down)
- Restart the program if input becomes unresponsive

### Performance Tips

- **Maximize terminal window** for the best visual experience
- **Use dark terminal background** for better contrast
- **Close other resource-intensive applications** for smoother animation
- **Try slow motion mode** if the animation is too fast to follow

## Educational Resources

### Physics Concepts Demonstrated

1. **Wave Equation**: `∂²y/∂t² = c²(∂²y/∂x²) - γ(∂y/∂t)`
   - See how mathematical equations translate to real wave behavior

2. **Boundary Conditions**: 
   - Fixed End: Like a guitar string attached to a bridge
   - Loose End: Like a rope with a free end
   - No End: Like an infinite string (no reflections)

3. **Standing Waves**:
   - Switch to Oscillate mode and experiment with frequencies
   - Find resonant frequencies where nodes and antinodes form

4. **Wave Interference**:
   - Use Manual mode to create multiple wave sources
   - Observe constructive and destructive interference


