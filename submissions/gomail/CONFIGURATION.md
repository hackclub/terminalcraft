# GoMail Configuration Management

GoMail includes comprehensive configuration management with database tracking for audit and history purposes.

## Features

### Configuration Tracking
- All configuration changes are logged to a SQLite database
- Track when changes were made, by whom, and from which source (CLI, UI, file)
- View configuration history and statistics
- Application events (start, reconfigure, errors) are logged

### Database Tables
- `configuration_history`: Tracks all configuration changes
- `app_events`: Logs application events and actions
- `sent_emails`: Email history (existing)
- `cache`: Drafts and templates (existing)

## CLI Commands

### Configuration Management
```bash
# View all configuration settings
gomail config list

# Get a specific configuration value
gomail config get app.default_from
gomail config get email.smtp.host

# Set a configuration value
gomail config set app.default_from "me@example.com"
gomail config set email.smtp.host "smtp.gmail.com" --description "Changed SMTP server"

# View configuration change history
gomail config history
gomail config history --key app.default_from --limit 10

# Show configuration statistics
gomail config stats

# Reset all configuration to defaults
gomail config reset --description "Starting fresh"
gomail config reset --force  # Skip confirmation
```

### Reconfiguration
```bash
# Launch interactive setup wizard
gomail reconfigure
```

## TUI Interface

- Press `Ctrl+G` in the inbox to view current configuration
- Press `i` to return to inbox from configuration view

## Configuration Keys

All configuration keys use dot notation:

### Application Settings
- `app.default_from` - Default sender email
- `app.signature` - Email signature
- `app.unsafe_html` - Enable unsafe HTML rendering

### Email Settings
- `email.delivery_method` - "smtp" or "resend"
- `email.smtp.host` - SMTP server hostname
- `email.smtp.port` - SMTP server port
- `email.smtp.username` - SMTP username
- `email.smtp.password` - SMTP password
- `email.smtp.encryption` - "starttls", "ssl", or "none"
- `email.smtp.insecure_skip_verify` - Skip TLS verification
- `email.resend.api_key` - Resend API key

### Storage Settings
- `storage.retention_days` - Days to keep sent emails
- `storage.cache_retention_days` - Days to keep drafts
- `storage.auto_save_drafts` - Enable auto-save
- `storage.auto_save_interval_seconds` - Auto-save interval

### UI Settings
- `ui.theme` - "auto", "light", or "dark"
- `ui.show_cc_bcc` - Always show CC/BCC fields
- `ui.compact_mode` - Enable compact mode

## Database Location

Configuration tracking data is stored in: `~/.gomail/gomail.db`

## Configuration File Location

Configuration file is stored in: `~/.gomail/config.toml`

## Example Usage

```bash
# Set up email configuration
gomail config set email.delivery_method smtp
gomail config set email.smtp.host smtp.gmail.com
gomail config set email.smtp.username myemail@gmail.com
gomail config set app.default_from myemail@gmail.com

# View what changed
gomail config history --limit 5

# Check configuration statistics
gomail config stats

# Launch reconfiguration if needed
gomail reconfigure
```

## Event Tracking

The system automatically tracks:
- Application starts
- Configuration changes
- Reconfiguration events
- Migration events
- Errors and failures

Use `gomail config history` and `gomail config stats` to view this information.
