# CliTunes

CliTunes is a terminal music player that supports playing local music files and streaming from Spotify.

## Features

- Play local audio files
- Spotify integration for search
- Lyrics fetching for songs
- Random play functionality

## Installation

### From PyPI
```bash
pip install CliTunesGithub==0.1.0
```

### From Source
```bash
git clone https://github.com/GaoYeGithub/clitunes.git
cd clitunes
pip install -e .
```

## Configuration

On first run, CliTunes will create a configuration file at `~/.config/clitunes/config.json`. You'll need to edit this file to add:
- Command for Windows: `notepad $env:USERPROFILE\.config\clitunes\config.json`


1. Music directories where your local files are stored
    - Window Directory example 
    ```bash
    "music_dirs": ["C:\\Users\\<profilename>\\OneDrive\\Music"]
    ```
2. Spotify API credentials (client ID and client secret) (Optional)

### Spotify API Credentials

To get Spotify API credentials:
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Create a new application
3. Copy the client ID and client secret to your config file

## Usage

### Basic Usage
```bash
clitunes
```

### Play a Random Track
```bash
clitunes random
```

### Search Spotify
```bash
clitunes search "Yellow Submarine"
```

## Controls

In the player interface:

- **N**: Next track
- **P**: Previous track
- **+**: Volume up
- **-**: Volume down
- **R**: Play random track
- **Q**: Quit
