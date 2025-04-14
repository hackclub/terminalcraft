# Ferrislog

[![Rust](https://img.shields.io/badge/Rust-1.72%2B-orange)](https://www.rust-lang.org/)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)

A persistent, log-structured key-value store implemented in Rust with a friendly CLI interface. Designed for reliability, simplicity, and educational purposes.

## Features

- **Core Operations**: Set, get, and remove key-value pairs with easy commands
- **Persistence**: All operations are logged as JSON to survive program restarts
- **Log Compaction**: Automatic compaction when log size exceeds threshold
- **Snapshots**: Create and load snapshots for backup and recovery
- **Command Line Interface**: Built with `clap` for intuitive command parsing

## Installation

```bash
# Clone the repository
git clone https://github.com/FabioCanavarro/Ferrislog
cd Ferrislog

# Build with Cargo
cargo build --release

# Install globally
cargo install --path .
```

## Usage

### Basic Operations

```bash
# Set a key-value pair
kvs set username ferris
# Output: Key set successfully

# Get the value for a key
kvs get username
# Output: ferris

# Remove a key
kvs rm username
# Output: Key removed successfully

# Try to get a non-existent key
kvs get username
# Output: Key not found
```

### Advanced Features
```bash
# List all keys in the store
kvs list_key
# Output: Keys: config, username, settings, 

# Count the number of keys
kvs count
# Output: 3

# Create a snapshot (backup)
kvs create_snapshot
# Output: Snapshot Created at /path/to/snapshots/log_2025-03-19_14-30-00.txt

# Load a snapshot
kvs load_snapshot /path/to/snapshots/log_2025-03-19_14-30-00.txt
# Output: Snapshot Loaded
```

## Implementation Details

### Storage Architecture
Ferrislog uses a log-structured storage model:

1. All operations (set, remove) are appended to a log file

2. An in-memory hash map tracks positions of the latest value for each key

3. On startup, the store rebuilds its state by replaying the log

4. Periodic compaction removes redundant entries to keep the log size manageable

## Performance Considerations

- Log Compaction: Automatically triggers when log exceeds 1024 bytes

- Memory Usage: Keeps only key pointers in memory, not values

- Recovery: Rebuilds state on startup by replaying the log

## Future Enhancements

- Multi-threaded operations for better performance

- Client-server architecture with network support

- Time-to-live (TTL) for keys
