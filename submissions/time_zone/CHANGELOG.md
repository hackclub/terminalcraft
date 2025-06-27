# Changelog

All notable changes to the Meet-Zone project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v1.0.2] - 2025-01-27

### Added
- Comprehensive error handling and debug logging for executable troubleshooting
- Enhanced executable startup diagnostics with detailed error reporting
- Debug log file creation (`meet-zone-debug.log`) for troubleshooting
- Error dialog display using tkinter for better user feedback
- System information logging (Python version, platform, executable status)
- Critical import testing with detailed error messages

### Fixed
- Fixed PyInstaller build configuration to include all required Textual modules
- Added comprehensive hidden imports for textual.widgets.tab_pane and related modules
- Fixed "No module named 'textual.widgets.tab_pane'" error in executables
- Enhanced build process with --collect-all=textual flag for complete module inclusion
- Fixed Windows PowerShell compatibility issues with PyInstaller command line arguments
- Added missing tkinter and logging imports for error handling

### Changed
- Improved PyInstaller configuration with explicit Textual module imports
- Enhanced build reliability across all platforms (Windows, macOS, Linux)
- Consolidated Windows PyInstaller command to single line for PowerShell compatibility
- Enhanced main entry point with comprehensive exception handling
- Improved error reporting with both console output and GUI dialogs

## [v1.0.1] - 2025-01-27

### Added
- Enhanced terminal-based UI with improved tabbed interface
- Better error handling and validation for user inputs
- Improved time zone selection with comprehensive timezone list
- Enhanced meeting slot scoring algorithm with configurable prioritization
- Better visual feedback with color-coded status messages

### Changed
- Improved UI layout with better responsive design
- Enhanced participant management with clearer form validation
- Better meeting time calculation with more accurate availability detection
- Improved error messages and user feedback

### Fixed
- Fixed time parsing validation issues
- Improved participant removal functionality
- Better handling of edge cases in meeting slot calculation
- Fixed UI responsiveness issues

## [v1.0.0] - 2024-12-01

### Added
- Initial release of Meet-Zone
- Terminal-based UI using Textual framework
- CSV roster import functionality
- Time zone conversion and meeting time calculation
- Meeting slot scoring based on participant availability
- Support for prioritizing by participant count or meeting duration
- Weekly view for planning meetings across multiple days

### Changed

### Fixed

### Removed
