# CLI Instruments

A collection of virtual musical instruments with colorful interactive UI that you can play in your terminal. Now featuring realistic audio samples generated using advanced signal processing!

![CLI Instruments](https://i.imgur.com/example.png)

## Features

- **🎵 Advanced Physical Modeling**: Uses sophisticated synthesis algorithms that simulate real instrument physics
- **🎹 Piano**: Complex harmonic series with inharmonicity, multi-stage hammer and string resonance modeling
- **🎸 Guitar**: Karplus-Strong string synthesis with plucked string physics, body resonance, and natural vibrato
- **🥁 Drums**: Physical membrane modeling, snare wire simulation, cymbal modal synthesis with metallic overtones
- **🔇 Clean Audio**: One sound at a time with proper note/hit duration timing
- **🌐 Cross-Platform**: Works on Windows, macOS, and Linux with automatic fallback to basic audio

## Requirements

- Python 3.x
- Required packages (automatically installed):
  - colorama (for colored terminal output)
  - numpy (for audio sample generation)
  - simpleaudio (for audio playback)

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Available Instruments

### 1. Piano
- **Advanced Synthesis**: 20-harmonic series with realistic inharmonicity (stretch tuning)
- **Physical Modeling**: Hammer strike simulation with multi-stage string and soundboard resonance
- **Authentic Envelope**: Sharp attack followed by complex decay with multiple time constants
- **Realistic Details**: Subtle tremolo, hammer texture noise, and dynamic range preservation
- **Key Mapping**: C4, C#4, D4, D#4, E4, F4, F#4, G4, G#4, A4, A#4, B4, C5

### 2. Guitar
- **String Physics**: Karplus-Strong algorithm simulating actual plucked string behavior
- **Advanced Modeling**: Delay line feedback with string damping and nonlinear compression
- **Body Resonance**: Guitar body frequency simulation (100-630 Hz resonances)
- **Natural Expression**: Progressive vibrato, pick noise, and multi-stage sustain/decay
- **String Tuning**: Low E, A, D, G, B, High E, plus extended bass notes

### 3. Drums
- **Membrane Physics**: Real drum head modeling with pitch envelopes and overtone series
- **Snare Simulation**: Membrane tone combined with realistic snare wire rattle synthesis
- **Cymbal Modeling**: Complex modal synthesis with multiple frequency modes and metallic modulation
- **Percussion Types**: 
  - **Kick**: Deep membrane with beater attack and air displacement
  - **Snare**: Dual-layer synthesis (membrane + wire rattle)
  - **Hi-hats**: Modal cymbal synthesis with shimmer and metallic noise
  - **Toms**: Pitched membrane with characteristic pitch bends
  - **Cymbals**: Multi-mode synthesis with complex frequency modulation

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