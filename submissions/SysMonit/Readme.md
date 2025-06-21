# System Analyzer

A comprehensive cross-platform system analysis tool with CLI/TUI interface for Windows, Linux, and macOS.

## 🚀 Quick Start

### Option 1: Automatic Installation
```bash
python install.py
```

### Option 2: Manual Installation
```bash
pip install psutil rich
python main.py
```

## 📋 Features

### 🗄️ Storage Analyzer
- Disk usage analysis with visual indicators
- Large file finder with customizable size filters
- Directory size analysis and comparison
- Cross-platform drive/partition detection

### 🌐 Network Analyzer
- Network interface information and status
- Port scanner with common service detection
- Ping test with detailed response times
- Active network connections monitoring

### 📊 Task Manager
- Process list with CPU/memory usage sorting
- Real-time system resource monitoring
- Process search and termination
- Live process monitoring with auto-refresh

### 🖥️ System Monitor
- Complete system information display
- CPU details with per-core usage
- Memory and swap usage monitoring
- Disk I/O statistics
- Temperature and fan sensor readings
- Real-time system performance dashboard

## 💻 System Requirements

- Python 3.6 or higher
- Works on Windows, Linux, and macOS
- Administrator/root privileges recommended for full functionality

## 🔧 Installation Files

- `main.py` - Main application entry point
- `storage_analyzer.py` - Storage analysis module
- `network_analyzer.py` - Network analysis module
- `task_manager.py` - Process and task management
- `system_monitor.py` - System monitoring and information
- `install.py` - Automated installation script
- `requirements.txt` - Python dependencies

## 🎯 Usage Examples

### Launch the application
```bash
python main.py
```

## 🛡️ Security Features

- Safe process termination with confirmation
- Non-destructive analysis operations
- Permission handling for restricted areas
- Error handling for access denied scenarios

## 🔍 Key Capabilities

- **Storage Analysis**: Find space-consuming files and directories
- **Network Diagnostics**: Test connectivity and scan for open ports
- **Performance Monitoring**: Track CPU, memory, and disk usage
- **Process Management**: View and manage running applications

## 📈 Visual Interface

- Color-coded status indicators (🟢🟡🔴)
- Rich text formatting and tables
- Real-time updating displays
- Intuitive menu navigation
- Progress bars for long operations

## 🐛 Troubleshooting

### Common Issues

**Permission Errors**: Run as administrator/root for full access to system information

**Missing Dependencies**: 
```bash
pip install --user psutil rich
```

**Python Not Found**: Ensure Python 3.6+ is installed and in PATH

### Platform-Specific Notes

- **Windows**: Some features require administrator privileges
- **Linux**: Temperature sensors may require root access
- **macOS**: Some system information requires elevated permissions

## 📚 Dependencies

- `psutil` - System and process utilities
- `rich` - Rich text and beautiful formatting

## 🎨 Interface Highlights

- Clean, modern terminal interface
- Beginner-friendly navigation
- Comprehensive system analysis
- Cross-platform compatibility
- Real-time monitoring capabilities

---

**Note**: For demo please look on this video: https://drive.google.com/file/d/1BuWdgPXkkFybzn3-TuEyxlZiC1it8Ka2/view?usp=sharing