# Heimdall by viv223345

A file integrity monitoring tool that tracks changes to files and directories using hashes.

[Binary](./heimdall)
[GitHub Repository](https://github.com/viv223345/heimdall)

## Overview

Heimdall monitors specified directories for file changes by computing and comparing cryptographic hashes. It can detect file additions, deletions, modifications, and moves, providing detailed reports on any changes detected.

## Features

- **File integrity monitoring** using hash algorithms
- **Change detection** for added, deleted, modified, and moved files
- **Continuous monitoring** with configurable intervals
- **Ignore** support using `.heimdallignore` files
- **Move detection** based on file hashes and metadata
- **Notifications** for detected changes
- **Report output** to files with timestamps

## Demo

https://github.com/user-attachments/assets/5c61c2a2-e888-41ce-a8f8-7b8b489f6b17

## Installation

### Prerequisites

- Python 3.8 or higher
- Optional dependencies:
  - `termcolor` for colored output
  - `notify2` for desktop notifications
  
# Dependencies
```bash
pip install termcolor notify2
```
### Method 1: Binary Installation (Recommended)

Download the pre-built binary from the releases page and make it executable:

```bash
# Download the binary
wget https://github.com/viv223345/heimdall/releases/latest/download/heimdall
chmod +x heimdall
mkdir -p ~/.local/bin
mv heimdall ~/.local/bin/heimdall

# Or, install to /usr/local/bin
# sudo mv heimdall /usr/local/bin/heimdall
```

### Method 2: From Source

#### Prerequisites
- Python 3.8 or higher
- Optional dependencies for enhanced functionality:
  - `termcolor` for colored output
  - `notify2` for desktop notifications (Linux only)

#### Installation Steps
```bash
# Clone or download the repository
git clone https://github.com/viv223345/heimdall.git
cd heimdall

# Install dependencies
pip install termcolor notify2

# Make executable
chmod +x heimdall.py
```

#### Manual Download
1. Download `heimdall.py` from the repository
2. Install dependencies: `pip install termcolor notify2`
3. Run with: `python heimdall.py`

### Method 3: Build from Source

To create your own binary:

```bash
# Install PyInstaller
pip install pyinstaller termcolor notify2

# Build binary
pyinstaller --onefile --name heimdall --optimize=2 heimdall.py

# Binary will be in dist/ directory
./dist/heimdall
```

## Usage

### Basic Usage

Create a baseline for a directory:
```bash
python heimdall.py /path/to/directory
```

Check for changes:
```bash
python heimdall.py /path/to/directory
```

### Continuous Monitoring

Monitor a directory continuously:
```bash
python heimdall.py -w /path/to/directory
```

Monitor with custom interval (default: 5 seconds):
```bash
python heimdall.py -w -i 10 /path/to/directory
```

### Additional Options

- `-v, --verbose` - Enable verbose output during scanning
- `-s, --show-size` - Display file sizes in reports
- `-o, --output FILE` - Append reports to specified file
- `-a, --algorithm ALGO` - Set hash algorithm (default: sha256)
- `--no-notifications` - Disable desktop notifications
- `-r, --reset` - Reset hash database for directory

### Examples

Monitor with verbose output and size display:
```bash
python heimdall.py -v -s /home/user/documents
```

Monitor and save reports to file:
```bash
python heimdall.py -w -o changes.log /var/www/html
```

Reset monitoring database:
```bash
python heimdall.py -r /path/to/directory
```

## Ignore Patterns

Create a `.heimdallignore` file in the monitored directory to exclude files and patterns:

```
# Ignore log files
*.log

# Ignore temporary files
*.tmp
*.temp

# Ignore specific directories
.git/
node_modules/

# Ignore specific files
config.local
```

The ignore file supports:
- Glob patterns (`*.log`, `temp*`)
- Directory patterns (`logs/`, `.git/`)
- Comments (lines starting with `#`)
- Blank lines (ignored)

## Hash Algorithms

Heimdall supports any hash algorithm available in Python's `hashlib` module:

- `sha256` (default)
- `sha1`
- `md5`
- `sha512`
- `blake2b`
- `blake2s`

Example with different algorithm:
```bash
python heimdall.py -a sha512 /path/to/directory
```

## Database Storage

Hash databases are stored in `~/.heimdall/` directory with filenames based on the monitored path hash. Each monitored directory has its own database file.

## Output Format

Reports include:
- **Added files** - New files detected
- **Deleted files** - Files no longer present
- **Modified files** - Files with changed content
- **Moved files** - Files relocated within the directory tree

Example output:
```
Added files (2):
  + /path/to/new_file.txt [1.2KB] (mtime: 2024-01-15 10:30:45)
  + /path/to/another.doc [15.3KB] (mtime: 2024-01-15 10:31:20)

Modified files (1):
  * /path/to/changed.txt [2.1KB] (mtime: 2024-01-15 10:32:10)

Moved files (1):
  /old/path/file.txt → /new/path/file.txt [5.4KB]
```
