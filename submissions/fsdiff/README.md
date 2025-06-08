# fsdiff - High-Performance Filesystem Diff Tool

[![Go Version](https://img.shields.io/badge/Go-1.21+-blue.svg)](https://golang.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Fast parallel filesystem diff tool for cybersecurity competitions and system administration. Detect filesystem changes using Merkle trees and parallel processing.

## Features

- **Parallel Processing**: Multi-threaded scanning with configurable workers
- **Merkle Tree Integrity**: Cryptographic filesystem verification
- **Compressed Snapshots**: Efficient gzip storage
- **Smart Filtering**: Auto-exclude system directories
- **HTML Reports**: Interactive change reports
- **Security Focus**: Critical path monitoring for cybersecurity

## Installation

### Prerequisites
- Go 1.21+

### Build
```bash
git clone (the hackclub url)
cd fsdiff
go mod tidy
go build -o fsdiff main.go
```

## Usage

### Basic Commands

```bash
# Create baseline snapshot
./fsdiff snapshot / baseline.snap

# Compare snapshots
./fsdiff diff baseline.snap current.snap

# Generate HTML report
./fsdiff diff baseline.snap current.snap report.html

# Live comparison
./fsdiff live baseline.snap /
```

### Options

```bash
# Custom workers and filtering
./fsdiff -workers 16 -ignore '.cache,node_modules' snapshot /home/user user.snap

# Verbose output
./fsdiff -v snapshot / baseline.snap
```

### Flags

| Flag       | Description                     | Default           |
|------------|---------------------------------|-------------------|
| `-workers` | Number of parallel workers      | CPU cores × 2     |
| `-v`       | Verbose output                  | false             |
| `-ignore`  | Comma-separated ignore patterns | Built-in defaults |

## Performance

- **885K files** scanned in 1m17s (11,391 files/sec)
- **Memory efficient** for large filesystems
- **99%+ compression** for snapshots

[//]: # (- **Cross-platform** &#40;Linux, macOS, Windows&#41;)


### Output Example
```
🔍 Scanning filesystem: /home/user
⚙️  Using 24 workers
📏 Found 885,591 items to process in 2.3s
🚀 Starting parallel scan with 24 workers...
📊 Scanning filesystem ████████████████████████░░ 82% | 885,591 | [11,391 it/s] | 1m17s
🌳 Calculating merkle root...
✅ Scan completed successfully!
   📊 Stats: 885,590 files, 104,572 dirs, 116.7 GB processed
   ⏱️  Duration: 1m17s (11,391 files/sec)
   🌳 Merkle root: 1175354a3ee4b326
   💾 Snapshot saved: baseline.snap (15.2 MB, 0.01% compression)
```

### Diff Summary
```
============================================================
📊 FILESYSTEM DIFF SUMMARY
============================================================
Baseline: server-01 (Ubuntu 22.04.3 LTS) - 2025-01-15 10:30:15
Current:  server-01 (Ubuntu 22.04.3 LTS) - 2025-01-15 14:22:33

📈 CHANGES:
   Added:    23 files/directories
   Modified: 7 files/directories
   Deleted:  2 files/directories
   Total:    32 changes

🚨 CRITICAL CHANGES:
   ADDED /etc/passwd.bak
   MODIFIED /bin/bash
   ADDED /tmp/.hidden_backdoor
```




## Architecture

```
fsdiff/
├── main.go
├── go.mod
└── internal/
    ├── scanner/     # Parallel filesystem scanning
    ├── snapshot/    # Snapshot storage/loading
    ├── diff/        # Change detection
    ├── report/      # HTML report generation
    ├── system/      # System info collection
    └── merkle/      # Merkle tree implementation
```

## Cybersecurity Use Cases

### Incident Response
```bash
# Create baseline
./fsdiff snapshot / clean-baseline.snap

# Check for compromise
./fsdiff live clean-baseline.snap / incident-report.html
```

### Competition Defense
```bash
# Quick baseline
./fsdiff snapshot / competition-baseline.snap

# Monitor changes
./fsdiff live competition-baseline.snap / threats.html
```

## Ignore Patterns

Built-in exclusions:
- System: `/proc`, `/sys`, `/dev`, `/tmp`
- Cache: `.cache`, `node_modules`, `__pycache__`
- VCS: `.git`, `.svn`, `.hg`
- Temp: `*.tmp`, `*.log`, `*.swp`

## Troubleshooting

### Common Issues
- **Permission errors**: Run with appropriate privileges
- **High memory**: Reduce workers or add ignore patterns
- **Slow performance**: Increase workers, use SSD

### Debug
```bash
./fsdiff -v snapshot / debug.snap
```


