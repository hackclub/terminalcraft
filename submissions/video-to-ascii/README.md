# Video to ASCII Art Converter & Animation Demos

This Python program converts videos into ASCII art and plays them directly in your terminal. Watch your favorite videos transformed into text characters with advanced features like color support, multiple character sets, and playback controls! It also includes stunning ASCII animation demos that don't require any video input.

## Features

### Video Conversion Features
- Converts any video format supported by OpenCV to ASCII art
- **Color support** - view videos in full color using ANSI terminal colors
- **Multiple character sets** - choose from standard, detailed, or inverted ASCII characters
- **Smart terminal sizing** - automatically detects and uses your terminal dimensions
- **Preloading mode** - smoother playback by processing all frames before playing
- **Playback controls** - loop videos or play them in reverse
- Maintains aspect ratio during conversion with terminal character correction
- Adjustable width and height for ASCII output
- FPS control to manage playback speed
- Progress tracking during playback

### ASCII Animation Demos
- **5 stunning animations** that don't require any video input
- **Sine Wave** - Enhanced with multiple waves, twinkling stars, moving moon, and floating particles
- **Matrix Digital Rain** - Realistic digital rain with variable speeds, colors, and special effects
- **Fireworks** - Dynamic fireworks with different explosion types, smoke trails, and realistic physics
- **Starfield** - 3D star field with depth perception, twinkling stars, and nebula effects
- **Plasma Effect** - Colorful plasma with interactive blobs, dynamic wave patterns, and color shifts
- All animations support the same character sets and color options as video conversion
- Customizable parameters for width, height, FPS, and duration

## Requirements

- Python 3.6+
- OpenCV (cv2)

## Installation

1. Make sure you have Python installed on your system
2. Install the required dependencies:

```
pip install opencv-python
```

## Usage

### Video Conversion

Basic usage:

```
python video_to_ascii.py path/to/your/video.mp4
```

With optional parameters:

```
python video_to_ascii.py path/to/your/video.mp4 --width 120 --height 60 --fps 20 --charset detailed --color --preload --loop
```

### ASCII Animation Demos

Run the animation demos:

```
python ascii_demos.py
```

Run a specific animation directly:

```
python ascii_demos.py --demo 1  # Sine Wave
python ascii_demos.py --demo 2  # Matrix Digital Rain
python ascii_demos.py --demo 3  # Fireworks
python ascii_demos.py --demo 4  # Starfield
python ascii_demos.py --demo 5  # Plasma Effect
```

With optional parameters:

```
python ascii_demos.py --demo 3 --width 120 --height 60 --fps 30 --duration 20 
```

### Video Conversion Parameters

- `video_path`: Path to the video file (required)
- `--width`: Width of ASCII art in characters (default: auto-detect terminal width)
- `--height`: Height of ASCII art in characters (default: auto-detect terminal height)
- `--fps`: Maximum frames per second cap (default: 30)
- `--charset`: ASCII character set to use (choices: standard, detailed, inverted)
- `--color`: Enable color output using ANSI terminal colors
- `--preload`: Preload all frames before playing (smoother but uses more memory)
- `--loop`: Loop the video playback continuously
- `--reverse`: Play the video in reverse

### Animation Demo Parameters

- `--demo`: Select a specific demo to run (1-5)
- `--width`: Width of ASCII art in characters (default: auto-detect terminal width)
- `--height`: Height of ASCII art in characters (default: auto-detect terminal height)
- `--fps`: Frames per second for the animation (default: 30)
- `--duration`: Duration of the animation in seconds (default: 10)
- `--charset`: ASCII character set to use (choices: standard, detailed, inverted)

## Controls

- Press `Ctrl+C` to stop playback at any time

## Examples

Play a video with default settings (auto-detects terminal size):
```
python video_to_ascii.py my_video.mp4
```

Play a video with custom dimensions:
```
python video_to_ascii.py my_video.mp4 --width 150 --height 60
```

Play a video with color and detailed character set:
```
python video_to_ascii.py my_video.mp4 --color --charset detailed
```

Play a video with slower frame rate:
```
python video_to_ascii.py my_video.mp4 --fps 15
```

Preload video for smoother playback and loop continuously:
```
python video_to_ascii.py my_video.mp4 --preload --loop
```

Play a video in reverse with inverted character set:
```
python video_to_ascii.py my_video.mp4 --reverse --charset inverted
```

## How It Works

### Video Conversion

The program:
1. Loads the video using OpenCV
2. Detects terminal size for optimal display (if width/height not specified)
3. Processes frames based on selected mode:
   - **Streaming mode**: Processes frames on-the-fly (default)
   - **Preload mode**: Processes all frames before playback for smoother performance
4. For each frame:
   - Resizes it to the specified dimensions while maintaining aspect ratio
   - Applies terminal character aspect ratio correction
   - Converts it to grayscale (or keeps color information if color mode enabled)
   - Maps each pixel to an ASCII character based on brightness using selected character set
   - Applies ANSI color codes if color mode is enabled
   - Displays the resulting ASCII art in the terminal
   - Waits to maintain the original video speed
5. Handles playback controls:
   - Loops video if loop option is enabled
   - Plays in reverse if reverse option is enabled

### ASCII Animation Demos

#### Sine Wave Animation
A mesmerizing wave animation that features:
- Multiple sine waves with different colors, frequencies, and amplitudes
- A dark blue night sky background with twinkling stars
- A moving moon with an uneven surface
- Floating particles that follow the main wave
- Dynamic color transitions and wave interactions

#### Matrix Digital Rain Animation
A recreation of the iconic "digital rain" effect featuring:
- Vertical streams of characters that fall at variable speeds
- Bright white "head" characters with a subtle glow effect
- Fading green trails of varying lengths
- Random character changes at different rates
- Occasional "focus drops" that are longer and faster
- Subtle background grid and random glitch effects
- Horizontal scan lines that appear periodically

#### Fireworks Animation
A dynamic fireworks display featuring:
- Rising fireworks with smoke trails and realistic physics
- Multiple explosion types (circular, spiral, random, large)
- Particles that respond to simulated wind and gravity
- Secondary colors for multi-color explosion effects
- A gradient night sky background with twinkling stars
- A moon with an uneven surface

#### Starfield Animation
A 3D star field simulation featuring:
- Stars with varying depths, creating a realistic 3D effect
- Dynamic movement that creates a flying through space sensation
- Twinkling stars with subtle color variations
- A distant, moving spiral galaxy
- Occasional shooting stars
- A subtle nebula background
- Stars with a glow effect

#### Plasma Effect Animation
A psychedelic plasma animation featuring:
- Dynamic, colorful patterns generated from multiple sine waves
- Interactive blobs that move around and influence the plasma pattern
- Circular waves that emanate from the blobs
- A color palette that shifts over time
- Occasional electric sparks (white pixels)
- Organic, flowing patterns that continuously evolve

## Tips

### Video Conversion Tips
- For better results, use a terminal with a small font size
- For color mode, use a terminal that supports ANSI color codes
- The detailed character set provides more gradations but may look better in larger terminal fonts
- Videos with good contrast work best with standard and inverted character sets
- Use preload mode for smoother playback on shorter videos
- For very large videos, avoid preload mode to prevent memory issues
- Try different terminal color schemes for different effects
- If the output looks stretched, try specifying both width and height manually
- For Windows users: Windows Terminal supports ANSI colors better than the default Command Prompt

### Animation Demo Tips
- For the best experience, run the animations in a terminal with a dark background
- The Matrix Digital Rain and Plasma Effect animations look best with color enabled
- For a more immersive experience, run the animations in full-screen terminal mode
- Try different character sets to see how they affect each animation
- Increase the width and height for more detailed animations
- For smoother animations, ensure your terminal can handle the specified FPS
- The Fireworks and Starfield animations are particularly impressive at larger sizes
- Try the custom settings option in the menu to fine-tune your experience
- For a mesmerizing display, try running the animations with the loop option enabled