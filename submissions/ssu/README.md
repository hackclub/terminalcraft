# System Security Utility

The `ssu` CLI simplifies security with an intuitive interface. Easily customize your layout in `~/Documents/ssu/directories.yaml` and configure scripts in `~/Documents/ssu/scripts/`

This tool only supports Linux. The program natively executes bash scripts.

## 📦 Installation

Prerequisites: https://go.dev/doc/install

```bash
go install github.com/awesomebrownies/ssu/cmd/ssu@latest
```

V: View File, Enter: Execute/Open, Escape: Exit, Up/Down Arrow: Navigate

## Modules

### Firewall

- Configure UFW (uncomplicated firewall)
- Configure System CTL IPv4

### Remote Access Points

- Modify SSH Configuration

### Least Privilege

- Disable Root (sudo su)
- Disable Guest User & Greeter Remote Login
- System File Permissions
