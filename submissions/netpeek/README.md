# NetPeek — All in One Terminal Network Toolkit

This is a simple terminal app made for network diagnostics, this has wide range of  tools like port and IP scanning, goelocation lookups, and exportable logs.

---

## Features

* View real time bandwidth usage per interface
* Scan your local subnet and identify live hosts (with geolocation)
* List open ports on your machine
* Scan custom or common ports on any IP
* Live TUI bandwidth monitor
* Show your public IP address and ISP information
* Export output to JSON

---

## Insteuctions

1. Clone this repo

2. Install dependencies:

```
pip install psutil requests
```
If you are on windows, you'll also need to run
```
pip install windows-curses
```
---

## Usage

```
python netpeek.py <mode> [options]
```

### Modes

| Mode           | Description                               |
| -------------- | ----------------------------------------- |
| `stats`        | Show bandwidth usage per interface        |
| `ports`        | List open ports using `netstat`           |
| `scan`         | Scan local subnet for active devices      |
| `tui`          | Launch terminal live bandwidth monitor    |
| `aboutme`      | Display your public IP, ISP, and location |
| `ports_custom` | Scan a custom port range on a host        |
| `ports_common` | Scan common ports on a host               |

---

## Examples commands

```
# Show network interface stats
python netpeek.py stats

# Scan subnet and export results
python netpeek.py scan --export

# List local open ports
python netpeek.py ports

# Start terminal bandwidth monitor
python netpeek.py tui

# Display your public IP info
python netpeek.py aboutme

# Scan ports 20 to 100 on 192.168.1.181
python netpeek.py ports_custom --host 192.168.1.181 --start-port 20 --end-port 100

# Scan common ports on a host
python netpeek.py ports_common --host 192.168.1.181
```

---

## Output Logs

Use `--export` to save output in JSON format to `netpeek_log.json`. It'll also add the timestamp to the log
