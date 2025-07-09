# TermiCast 🛰️

*Because checking weather apps when you're offline is... impossible.*

A neat Python terminal app that uses satellite data to predict weather without needing internet. Works great for camping, remote work, or when you just don't trust online forecasts!

## What does it do?

- **Works offline**: All the magic happens on your computer using satellite orbital data
- **Tracks weather satellites**: Follows NOAA, METOP, and other weather birds as they fly over
- **Predicts weather**: Turns satellite pass patterns into actual forecasts  
- **Natural disaster warnings**: Early heads-up based on satellite analysis
- **Pressure sensor support**: Hook up a USB/GPIO barometric sensor for better accuracy
- **Pretty terminal UI**: Rich colors and ASCII maps because terminals can be beautiful too
- **Single executable**: Build it once, run it anywhere (no Python installation needed!)

## Quick Start

### Option 1: Build it yourself (Recommended)

**On Linux/macOS:**
```bash
./build.sh
```

**On Windows:**
```batch
build.bat
```

That's it! The scripts handle everything and create a single executable in the `dist/` folder.

### Option 2: Traditional Python install

1. **Get the code:**
```bash
git clone <this-repo>
cd TermiCast
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install TermiCast:**
```bash
pip install -e .
```

## Using TermiCast

### Basic commands (after building):

```bash
# Weather forecast for your area
./dist/termicast forecast --location "Your City, Country"

# See what satellites are overhead today
./dist/termicast satellites --today

# Cool ASCII weather map
./dist/termicast map

# Barometric pressure trends (if you have a sensor)
./dist/termicast pressure-trend

# Set your default location so you don't have to type it every time
./dist/termicast config --location "Your City, Country"
```

### Setting up satellite data

The app needs TLE (Two-Line Element) files for satellite tracking:

1. Create a `tle/` folder in your project directory
2. Download TLE files for weather satellites from sources like:
   - [Celestrak](https://www.celestrak.com/NORAD/elements/)
   - [Space-Track.org](https://www.space-track.org/) (requires free account)
3. Save them as `.tle` files in the `tle/` folder

### Optional: Add a pressure sensor

If you have a USB barometric pressure sensor:

```bash
./dist/termicast sensor --port /dev/ttyUSB0 --enable
```

The app will use real pressure readings to improve forecast accuracy.

## Supported Satellites

TermiCast works best with these weather satellites:
- **NOAA satellites** (NOAA-18, NOAA-19, NOAA-20) - Great for cloud imaging
- **METOP satellites** (METOP-A, METOP-B, METOP-C) - Excellent for precipitation data  
- **GOES satellites** - Geostationary coverage for specific regions

## Configuration

Settings are stored in `~/.termicast/config.json`. You can edit this file directly or use the `config` command to change preferences.

## Building from Source

The build process creates a single executable that includes Python and all dependencies. No need for users to install anything!

**Requirements:**
- Python 3.8+
- PyInstaller (added to requirements.txt)

**Build process:**
1. Run the appropriate build script for your OS
2. Find your executable in `dist/`
3. Distribute the single file - it runs anywhere!

**Manual build:**
```bash
python build_executable.py
```

## Troubleshooting

**"No satellites visible"** - Check your TLE files and make sure they're recent (updated weekly).

**"Location not found"** - Try a different format like "City, State" or "City, Country".

**Build fails** - Make sure you have Python 3.8+ and all dependencies installed.

**Executable won't run** - On Linux/macOS, make sure it's executable: `chmod +x dist/termicast`

## Why I built this

I got tired of weather apps that need internet and wanted something that works anywhere. Plus, satellite data is fascinating and surprisingly accurate when you know how to interpret it!

## Contributing

Found a bug? Have an idea? Open an issue or send a PR. I'm always looking for ways to make this better.

## License

MIT License - use it however you want! 