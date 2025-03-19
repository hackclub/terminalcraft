import os

BASE_URL = "https://quadcopter-log-api.onrender.com"

TOKEN_FILE = os.path.expanduser("~/.logcli_token")

def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        f.write(token)

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None

def clear_token():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
