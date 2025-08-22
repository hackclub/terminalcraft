# TShare

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Rust](https://img.shields.io/badge/rust-1.88-blue.svg)](https://www.rust-lang.org)
[![GitHub](https://img.shields.io/github/stars/RobbyV2/tshare?style=social)](https://github.com/RobbyV2/tshare)

[![Version](https://img.shields.io/badge/Version-1.0.0-blue.svg)](https://www.rust-lang.org)

Terminal sharing through web links.

## Requirements

- Rust (any recent version)

Development dependencies:
- just (`cargo install just`)
- djlint (`pip install djlint`) for HTML formatting

## Installation

Download pre-built packages from the [releases page](https://github.com/RobbyV2/tshare/releases) or build from source:

```bash
cargo build --release
# Binaries will be in target/release/
```

## Usage

Start servers:
```bash
tunnel-server &
web-server &
```

Share terminal:
```bash
tshare connect
```

## Development

See `justfile` for available commands:
```bash
just --list
```

Common commands:
```bash
just run            # Start both servers
just client connect # Create session
just build          # Build release
just build-deb      # Build .deb package
```

## Architecture

- `tshare`: CLI client, captures terminal sessions
- `tunnel-server`: WebSocket relay and API, port 8385
- `web-server`: Web interface, port 8386

## Configuration

All binaries accept `--help` for options. Default configuration works for local development.

Production example:
```bash
tunnel-server --host 0.0.0.0
web-server --host 0.0.0.0 --tunnel-url http://tunnel.example.com:8385
tshare connect --tunnel-host tunnel.example.com --web-host web.example.com
```

## License

MIT