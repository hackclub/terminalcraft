# TuiType

A terminal-based typing test application similar to MonkeyType, built with Rust and the Ratatui library.

## Installation

### From Source

1. Clone the repository:

```bash
git clone https://github.com/RobbyV2/tuitype.git
cd tuitype
```

1. Run the application:

```bash
cargo run
```

## WebAssembly Support

- WIP

## Usage

- Use your keyboard
- Press `Esc` to open the TUI menu
  - From here you can look at the help menu, or change various settings

## Configuration

TuiType saves configuration in your system's config directory:

- Windows: `%APPDATA%\tuitype\config.json`
- macOS: `~/Library/Application Support/tuitype/config.json`
- Linux: `~/.config/tuitype/config.json`

## License

MIT
