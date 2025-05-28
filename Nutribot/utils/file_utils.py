import os
import json
from config import LOGIN_FILE

def ensure_login_file_exists():
    if not os.path.exists(LOGIN_FILE):
        with open(LOGIN_FILE, 'w') as f:
            json.dump({}, f)

def load_user_credentials():
    ensure_login_file_exists()
    try:
        with open(LOGIN_FILE, 'r') as f:
            data = f.read().strip()
            return json.loads(data) if data else {}
    except json.JSONDecodeError:
        return {}

def save_user_credentials(credentials: dict):
    with open(LOGIN_FILE, 'w') as f:
        json.dump(credentials, f, indent=4)
