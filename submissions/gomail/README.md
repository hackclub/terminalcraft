# GoMail

Terminal-based email client for sending emails from the command line.

## Usage

### Quick Start

```bash
# Build the application
./build.sh

# Run the application
./run.sh --help

# Send email directly
./run.sh --to="user@example.com" --subject="Subject" --body="Message"

# With attachments
./run.sh --to="user@example.com" --subject="Files" --attachments="file.txt,doc.pdf"
```

### Alternative Build Methods

```bash
# Using Makefile
make build

# Using Go directly
go build -o gomail .

# Cross-platform release build
make release
```

### Running the Application

```bash
# Direct execution after building
./gomail --to="user@example.com" --subject="Subject" --body="Message"

# Using the run script (builds if needed)
./run.sh --to="user@example.com" --subject="Subject" --body="Message"

# Interactive mode (TUI)
./run.sh

# Setup wizard
./run.sh setup
```

## Configuration

Set environment variables:
- `GOMAIL_FROM`: Your email address
- `GOMAIL_SMTP_HOST`: SMTP server
- `GOMAIL_SMTP_USERNAME`: Username
- `GOMAIL_SMTP_PASSWORD`: Password
- `RESEND_API_KEY`: For Resend API (alternative to SMTP)

## Build Scripts

GoMail includes convenient build and run scripts:

### `build.sh`
- Builds the application for the current platform
- Automatically determines version from git tags
- Enables CGO for SQLite support
- Makes the binary executable

### `run.sh`  
- Runs the GoMail application
- Automatically builds if binary doesn't exist
- Passes all arguments to the application
- Convenient for development and testing

### Usage Examples

```bash
# Build only
./build.sh

# Run with automatic build
./run.sh --help

# Send email using run script
./run.sh --to="user@example.com" --subject="Test" --body="Hello World"

# Run setup wizard
./run.sh setup
```

