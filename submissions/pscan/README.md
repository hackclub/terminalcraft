# pscan

A cross-platform process scanner that retrieves important information about target processes, including ASLR slide detection and platform-specific security features.

## Overview

This application simplifies the process of obtaining ASLR slide information and provides additional platform-specific security details (such as Hardened Runtime and Rosetta translation status on macOS) in a clean, formatted output.

## Features

### macOS
- Task name
- Process architecture detection
- Hardened Runtime status
- Rosetta translation detection
- Dynamic/Runtime base address

### Linux
- Task name
- ASLR enabled status
- Dynamic/Runtime base address

## Platform Support

### macOS
- **Supported versions**: macOS 11 and above
- **Tested on**: macOS 15.5 on Apple Silicon
- **Architectures**: Both x86_64 and aarch64 versions tested through Rosetta 2 runtime.

### Linux
- **Tested on**: aarch64 Ubuntu 24.04.2
- **Cross-platform testing**: x86_64 Linux version tested on aarch64 Ubuntu 24.04.2 through Rosetta 2 on Linux runtime functionality and Apple Virtualisation
- **Architectures**: aarch64 and x86_64

## **MSRV** (Minimum Supported Rust Version):
1.85.1

## Installation

### From Source

```bash
cargo build --release
```

### Cross-compilation with zigbuild

For cross-compilation to Linux targets, you can use `cargo-zigbuild`:

```bash
# Install zigbuild using binstall for a faster installation
cargo binstall cargo-zigbuild
# or
cargo install cargo-zigbuild

# Build for aarch64 Linux
cargo zigbuild --target aarch64-unknown-linux-gnu --release

# Build for x86_64 Linux
cargo zigbuild --target x86_64-unknown-linux-gnu --release
```

## Usage

### Basic Usage

```bash
# Scan a process by PID
pscan --pid <process_id>

# Show version information
pscan --version
```

### Examples

```bash
# Scan process with PID 1234
pscan -p 1234

# Show version
pscan -v
```

### Sample Output

On macOS:
```
┌─────────────────────┬──────────────────────────────────────┐
│ Property            │ Value                                │
├─────────────────────┼──────────────────────────────────────┤
│ Task Name           │ example_process                      │
│ Architecture        │ arm64                                │
│ Hardened Runtime    │ true                                 │
│ Rosetta Translated  │ false                                │
│ Base Address        │ 0x0000000000000000                   │
└─────────────────────┴──────────────────────────────────────┘
```

On Linux:
```
┌─────────────────────┬──────────────────────────────────────┐
│ Property            │ Value                                │
├─────────────────────┼──────────────────────────────────────┤
│ Task Name           │ example_process                      │
│ Architecture        │ aarch64                              │
│ ASLR Enabled        │ true                                 │
│ Base Address        │ 0x0000000000000000                   │
└─────────────────────┴──────────────────────────────────────┘
```

## Command Line Options

- `-p, --pid <PID>` - Process ID to scan
- `-v, --version` - Show version information
- `-h, --help` - Show help information