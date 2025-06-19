# Example configuration with security issues
import os

# Database configuration
DB_PASSWORD = "super_secret_password_123"
API_KEY = "1234567890abcdef1234567890abcdef"

# Third-party services
ANALYTICS_URL = "https://analytics.tracker.com/script.js"
TELEMETRY_ENDPOINT = "https://telemetry.service.com/collect"

def save_user_credentials(username, password):
    """Save user credentials to a plaintext file."""
    with open('credentials.txt', 'a') as f:
        f.write(f"{username}:{password}\n")

def load_browser_data():
    """Load browser data from SQLite file."""
    import sqlite3
    conn = sqlite3.connect(os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Login Data'))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logins")
    return cursor.fetchall()
