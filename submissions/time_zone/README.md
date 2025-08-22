# Meet-Zone

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A professional terminal application for identifying optimal meeting times across multiple time zones. Meet-Zone streamlines the scheduling process for distributed teams with an intuitive interface built on the Textual framework.

## Overview

Meet-Zone solves the challenge of coordinating meetings across global teams by:

- Analyzing participant availability across different time zones
- Identifying optimal meeting slots that maximize attendance
- Providing a clear, ranked list of potential meeting times
- Supporting both command-line and interactive interfaces

## Installation

### From Releases

The easiest way to install Meet-Zone is to download the pre-built executable for your platform from the [Releases page](https://github.com/yourusername/meet-zone/releases).

1. Download the appropriate file for your operating system:
   - Windows: `meet-zone-windows.exe`
   - macOS: `meet-zone-macos`
   - Linux: `meet-zone-linux`

2. Verify the file integrity using the provided SHA256 checksum:
   ```bash
   # Windows (PowerShell)
   Get-FileHash -Algorithm SHA256 meet-zone-windows.exe | Format-List
   
   # macOS/Linux
   shasum -a 256 meet-zone-macos  # or meet-zone-linux
   ```

3. Make the file executable (macOS/Linux only):
   ```bash
   chmod +x meet-zone-macos  # or meet-zone-linux
   ```

4. Run the application:
   ```bash
   # Windows
   .\meet-zone-windows.exe
   
   # macOS/Linux
   ./meet-zone-macos  # or ./meet-zone-linux
   ```

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/meet-zone.git
cd meet-zone

# Install the package in development mode
python -m pip install -e .
```

## Requirements

- Python 3.10+
- Dependencies:
  - textual >= 0.38.1
  - pytz >= 2023.3
  - zoneinfo (for Python < 3.9)

## Usage

### Command Line Interface

```bash
# Launch with empty UI (add participants manually)
python -m meet_zone

# Load participants from CSV file
python -m meet_zone roster.csv

# Specify minimum meeting duration
python -m meet_zone roster.csv --duration 45

# Display top N meeting slots
python -m meet_zone roster.csv --top 5

# Show options for the entire week
python -m meet_zone roster.csv --week

# Prioritize by duration instead of participant count
python -m meet_zone roster.csv --prioritize duration

# Specify start date for search
python -m meet_zone roster.csv --date 2023-12-01
```

### CSV Format

Participant data should be provided in CSV format with the following structure:

```csv
name,timezone,start_time,end_time
```

Example:

```csv
Alice,America/New_York,09:00,17:00
Bob,Europe/London,09:00,17:00
Charlie,Asia/Tokyo,09:00,17:00
```

## Application Interface

The application provides a tabbed interface with two primary sections:

### Participants Management

- Add participants with name, timezone, and working hours
- View all participants in a tabular format
- Remove selected participants or clear all entries

### Meeting Time Finder

- Configure meeting parameters:
  - Minimum duration
  - Number of results to display
  - Date range (today or full week)
  - Prioritization strategy (participants vs. duration)
- View results with detailed information:
  - Start and end times (UTC)
  - Meeting duration
  - Participant count and percentage
  - List of available participants

## Architecture

Meet-Zone is built with a modular architecture:

- `parser.py`: Handles CSV parsing and participant data structures
- `scheduler.py`: Implements the core scheduling algorithm
- `ui.py`: Provides the Textual-based user interface
- `__main__.py`: Entry point with command-line argument handling

## Building from Source

To build the executable from source:

1. Install PyInstaller and other build dependencies:
   ```bash
   python -m pip install pyinstaller cairosvg pillow
   ```

2. Build the executable:
   ```bash
   # Windows
   pyinstaller --name="meet-zone-windows" --onefile --windowed --icon=icon.ico --add-data="roster.csv;." --hidden-import=zoneinfo.tzpath src/meet_zone/__main__.py
   
   # macOS
   pyinstaller --name="meet-zone-macos" --onefile --windowed --icon=icon.png --add-data="roster.csv:." --hidden-import=zoneinfo.tzpath src/meet_zone/__main__.py
   
   # Linux
   pyinstaller --name="meet-zone-linux" --onefile --windowed --icon=icon.png --add-data="roster.csv:." --hidden-import=zoneinfo.tzpath src/meet_zone/__main__.py
   ```

## Versioning

This project follows [Semantic Versioning](https://semver.org/). For the versions available, see the [tags on this repository](https://github.com/yourusername/meet-zone/tags).

## Changelog

See the [CHANGELOG.md](CHANGELOG.md) file for details on version history and changes.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Project Link: [https://github.com/yourusername/meet-zone](https://github.com/yourusername/meet-zone)