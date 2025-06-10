# GoMail

Terminal-based email client for sending emails from the command line.

## Usage

```bash
# Build
make build

# Send email
./gomail --to="user@example.com" --subject="Subject" --body="Message"

# With attachments
./gomail --to="user@example.com" --subject="Files" --attachments="file.txt,doc.pdf"
```

## Configuration

Set environment variables:
- `GOMAIL_FROM`: Your email address
- `GOMAIL_SMTP_HOST`: SMTP server
- `GOMAIL_SMTP_USERNAME`: Username
- `GOMAIL_SMTP_PASSWORD`: Password
- `RESEND_API_KEY`: For Resend API (alternative to SMTP)

