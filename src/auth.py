"""OAuth2 credential management."""

import os

from google.auth.transport import requests
from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from config import CREDENTIALS_FILE, SCOPES, TOKEN_FILE


def get_credentials() -> credentials.Credentials:
    creds: credentials.Credentials | None = None

    if os.path.exists(TOKEN_FILE):
        creds = credentials.Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if creds is not None and creds.valid:
        return creds

    if creds is not None and creds.expired and creds.refresh_token is not None:
        creds.refresh(requests.Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)

    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())

    return creds
