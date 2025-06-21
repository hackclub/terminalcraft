# Peeky: CLI Tool

A Minimal Port & Process Inspector to inspect and manage network ports and processes.

## Features

- **scan** - List open ports with process information
- **conflicts** - Detect conflicting processes on ports
- **stats** - View network statistics and summary
- **kill** - Kill processes by port or PID
- **clean** - Clean up zombie or idle port-bound processes
- **whois** - Look up information about IP addresses and domains
- **secure** - Identify security risks in network configuration
- **export** - Export connection data in JSON or text format
- **config** - Configure settings and API keys

## Installation

### From PyPI (Recommended)

```bash
# Install from PyPI
pip install peeky

# Now you can use the 'peeky' command directly
peeky --help
```

### From Source

```bash
# Clone the repository
git clone https://github.com/amogh-agrawal/peeky.git
cd peeky

# Install in development mode
pip install -e .

# Now you can use the 'peeky' command directly
peeky --help
```

## Usage

### Scan for Open Ports

```bash
# List all open ports
peeky scan

# Filter by port
peeky scan --port 8080

# Show only TCP connections
peeky scan --tcp

# Filter by process name
peeky scan --filter node

# Show command that started process
peeky scan --command
```

### Detect Port Conflicts

```bash
# Find processes competing for the same ports
peeky conflicts
```

### View Network Statistics

```bash
# Display summary statistics and top processes/ports
peeky stats
```

### Kill Processes

```bash
# Kill by port number
peeky kill 8080

# Kill by PID
peeky kill 1234

# Force kill (SIGKILL)
peeky kill 8080 --force

# Skip confirmation prompts
peeky kill 1234 --yes
```

### Clean Up Idle Processes

```bash
# Find and clean up idle/zombie processes
peeky clean

# Just list the processes without cleaning
peeky clean --list

# Clean without confirmation
peeky clean --yes

# Force kill processes
peeky clean --force
```

### WHOIS Lookup

```bash
# Look up information about a domain
peeky whois example.com

# Look up information about an IP address
peeky whois 8.8.8.8

# Use only local resolution (no API calls)
peeky whois example.com --local
```

### Security Risk Analysis

```bash
# Identify potential security risks in network configuration
peeky secure
```

### Export Data

```bash
# Export connection data to JSON
peeky export --json

# Export to a file
peeky export --out connections.json --json

# Export filtered data
peeky export --port 8080 --tcp --json
```

### Configure API Keys

```bash
# Set up the WHOIS API key (APILayer)
peeky config --set-whois-key

# Provide an API key directly
peeky config --set-whois-key --key YOUR_API_KEY

# Show configured API keys (masked)
peeky config --show-keys
```

## API Integration

Peeky uses the APILayer WHOIS API for enhanced domain lookups. To use this feature:

1. Get an API key from [APILayer WHOIS API](https://apilayer.com/marketplace/whois-api)
2. Configure your API key:
   ```bash
   peeky config --set-whois-key
   ```