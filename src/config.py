"""App-wide constants."""

import os

_CONFIG_DIR = os.path.join(
    os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
    "mytasks",
)
os.makedirs(_CONFIG_DIR, exist_ok=True)

SCOPES: list[str] = ["https://www.googleapis.com/auth/tasks"]
CREDENTIALS_FILE: str = os.path.join(_CONFIG_DIR, "credentials.json")
TOKEN_FILE: str = os.path.join(_CONFIG_DIR, "token.json")
