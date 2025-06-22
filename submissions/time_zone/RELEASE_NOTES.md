# Release Notes for v1.0.1

## Meet-Zone v1.0.1 - Enhanced UI and Improved Functionality

### What's New

**Enhanced User Interface**
- Improved tabbed interface with better navigation
- Enhanced participant management with clearer form validation
- Better visual feedback with color-coded status messages
- Improved UI layout with better responsive design

**Better Error Handling**
- Enhanced time parsing validation
- Improved error messages and user feedback
- Better handling of edge cases in meeting slot calculation

**Improved Functionality**
- Enhanced meeting slot scoring algorithm with configurable prioritization
- Better meeting time calculation with more accurate availability detection
- Comprehensive timezone selection list
- Fixed participant removal functionality

### Installation

Download the appropriate executable for your operating system:

- **Windows**: `meet-zone-windows-1.0.1.exe`
- **macOS**: `meet-zone-macos-1.0.1`
- **Linux**: `meet-zone-linux-1.0.1`

### Verification

Each release includes SHA256 checksums for verification:

```bash
# Windows (PowerShell)
Get-FileHash -Algorithm SHA256 meet-zone-windows-1.0.1.exe

# macOS/Linux
shasum -a 256 meet-zone-macos-1.0.1
sha256sum meet-zone-linux-1.0.1
```

### Usage

```bash
# Windows
.\meet-zone-windows-1.0.1.exe

# macOS (make executable first)
chmod +x meet-zone-macos-1.0.1
./meet-zone-macos-1.0.1

# Linux (make executable first)
chmod +x meet-zone-linux-1.0.1
./meet-zone-linux-1.0.1
```

### What's Fixed

- Fixed time parsing validation issues
- Improved participant removal functionality
- Better handling of edge cases in meeting slot calculation
- Fixed UI responsiveness issues

### Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete version history.