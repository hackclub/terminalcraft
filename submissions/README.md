# DOSEPER

A tool for sending multiple HTTP requests for website testing.

## Features
- Send multiple HTTP requests concurrently.
- Basic error handling and reporting.
- Customizable via command line options.

## Installation
```bash
pip install doseper
```

## Usage
```bash
doseper help
```

Run doseper with:

```bash
doseper <url> <times> <mode> [rate]
```

- `url`: Target URL (must start with http:// or https://)
- `times`: Number of requests to send
- `mode`: Execution mode (F = Fast, H = Human, R = Rate-limited)
- `rate`: Requests per second limit (only for mode R, max 50)

**Examples:**

```bash
doseper "https://example.com" 100 H
doseper "https://example.com" 100 R 10
```

## License

This project is licensed under the MIT License.

**This project includes AI-assisted editing.**
