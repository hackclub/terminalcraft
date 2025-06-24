# LockBox Password Manager

### A secure command-line password manager with military-grade encryption and intuitive features.

## Features

| Feature | Description |
|---------|-------------|
| **Secure Storage** | AES-256 encrypted vault |
| **Password Generation** | Create 16-character strong passwords |
| **Instant Search** | Fuzzy-find passwords in milliseconds |
| **Cross-Platform** | Windows/macOS/Linux support |
| **Zero Trust** | No internet connection needed for core operations |
| **Breach Check** | Verify passwords against HIBP database |

## New Security Feature: Password Breach Check

LockBox now integrates with Have I Been Pwned's (HIBP) API to check if your passwords have been exposed in known data breaches. This feature:

- Checks passwords against 613+ million breached credentials
- Uses secure k-Anonymity model (only sends first 5 chars of SHA-1 hash)
- Provides instant feedback before password storage
- Helps prevent using compromised credentials

## Installation

### Linux
# 1. Install system dependencies
```
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-tk python3-dev git
```
```
# 2. Clone the repository
git clone https://github.com/belalmostafaaa/lockbox.git
cd lockbox
```
```
# 3. Install Python packages directly
sudo pip3 install cryptography pyperclip requests
```
```
# 4. Make the script executable
chmod +x lockbox.py
```
```
# 5. Run (with sudo for proper permissions)
sudo ./lockbox.py
```
### Windows
```
# 1. Install Python 3 (run as Administrator)
winget install Python.Python.3.10 --accept-package-agreements --accept-source-agreements
```
```
# 2. Clone repository (requires git installed)
git clone https://github.com/belalmostafaaa/lockbox.git
cd lockbox
```
```
# 3. Install dependencies
python -m pip install cryptography pyperclip requests
```
```
# 4. Run as Admin
Start-Process python -ArgumentList "lockbox.py" -Verb RunAs
```
### macOS
```
# 1. Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
```
# 2. Install dependencies
brew install python-tk
```
```
# 3. Clone the repository
git clone https://github.com/belalmostafaaa/lockbox.git
cd lockbox
```
```
# 4. Install Python packages
pip3 install cryptography pyperclip requests
```
```
# 5. Run with sudo
sudo python3 lockbox.py
```
## Running

### Linux/macOS
```
sudo ./lockbox.py or sudo python3 lockbox.py
```
### Windows
```
python lockbox.py
```

## Notes:
- The terminal or Powershell must be run as Administrator

- Internet connection required for breach checking feature

- No passwords are transmitted - only hash prefixes are checked
