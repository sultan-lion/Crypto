# calendar_push.py
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def _get_user_creds(oauth_client_path: str, token_path: str = "token.json") -> Credentials:
    """
    OAuth user login flow:
    - First run opens a browser to login and grant permissions
    - Saves token.json locally
    - Next runs reuse token.json silently
    """
    creds: Optional[Credentials] = None

    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    except Exception:
        creds = None

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        return creds

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(oauth_client_path, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    return creds


def push_calendar_event(
    oauth_client_path: str,
    calendar_id: str,
    title: str,
    description: str,
    timezone: str,
) -> str:
    """
    Creates a 10-minute event starting now in the user's Google Calendar.
    """
    creds = _get_user_creds(oauth_client_path=oauth_client_path)
    service = build("calendar", "v3", credentials=creds)

    start_dt = datetime.now()
    end_dt = start_dt + timedelta(minutes=10)

    event = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": timezone},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": timezone},
    }

    created = service.events().insert(calendarId=calendar_id, body=event).execute()
    return created.get("htmlLink", "")