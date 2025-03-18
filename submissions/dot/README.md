# Dot

```
██████╗░░█████╗░████████╗
██╔══██╗██╔══██╗╚══██╔══╝
██║░░██║██║░░██║░░░██║░░░
██║░░██║██║░░██║░░░██║░░░
██████╔╝╚█████╔╝░░░██║░░░
╚═════╝░░╚════╝░░░░╚═╝░░░
```

A tool that comes in handy when managing your dotfiles.

## Features

- Create and manage symlinks for scripts and configuration files
- Interactive TUI with intuitive navigation
- Easy installation and configuration
- Makes managing and editing dotfiles easier

## Installation

### Quick Install

```bash
git clone https://github.com/yourusername/dot.git
cd dot
chmod +x dot
./dot install
```

### Manual Setup

1. Clone this repository
2. Make the script executable: `chmod +x dot`
3. Create symlinks manually: `./dot make`

## Usage

```
Usage: dot {make|kill|list|install|edit|config|interactive|help}

make        - Create symlinks for scripts and config files
kill        - Remove symlinks
list        - List active symlinks
install     - Install dot script to /usr/local/bin
edit        - Edit scripts and configuration files
config      - Edit dot configuration
interactive - Open interactive menu mode
help        - Show this help message
```

### Interactive Mode

Launch the interactive TUI with:

```bash
dot interactive
```

Navigate using arrow keys or number keys, press Enter to select.

## Configuration

The configuration file is created automatically at `~/.dotconfig` by default, and can be edited with:

```bash
dot config
```

Default configuration:

```bash
# Dot configuration file
# Source directories
SCRIPT_DIR="/path/to/dot/scripts"
CONF_DIR="/path/to/dot/conf"

# Destination directories
BIN_DIR="/usr/local/bin"
CONFIG_DIR="~/.config"

# Editor (default: nano)
EDITOR=""
```

## Directory Structure

```
dot/
├── dot (main script)
├── scripts/ (your executable scripts)
│   ├── script1
│   └── script2
└── conf/ (your configuration directories)
    ├── app1/
    └── app2/
```
