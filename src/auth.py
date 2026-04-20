"""OAuth2 credential management."""

import json
import os

from google.auth.transport import requests
from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from config import CREDENTIALS_FILE, SCOPES, TOKEN_FILE

_cached_creds: credentials.Credentials | None = None


def _save_credentials(creds: credentials.Credentials) -> None:
    data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes) if creds.scopes else SCOPES,
        "expiry": creds.expiry.strftime("%Y-%m-%dT%H:%M:%SZ") if creds.expiry else None,
    }
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f)


def get_credentials() -> credentials.Credentials:
    global _cached_creds

    if _cached_creds is not None and _cached_creds.valid:
        return _cached_creds

    creds: credentials.Credentials | None = None
    if os.path.exists(TOKEN_FILE):
        creds = credentials.Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if creds is not None and creds.valid:
        _cached_creds = creds
        return creds

    if creds is not None and creds.expired and creds.refresh_token is not None:
        creds.refresh(requests.Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)

    _save_credentials(creds)
    _cached_creds = creds
    return creds
