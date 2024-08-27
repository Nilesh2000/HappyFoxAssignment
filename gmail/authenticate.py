"""
This module handles OAuth 2.0 authentication flow for the Gmail API.
"""

import logging
import os
from typing import Optional

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"


def _load_credentials() -> Optional[Credentials]:
    """
    Load credentials from token file if it exists.

    Returns:
        The loaded credentials if the token file exists, None otherwise.
    """
    try:
        if os.path.exists(TOKEN_FILE):
            return Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    except Exception as e:
        logging.error("Error loading credentials: %s", e)
    return None


def _refresh_credentials(creds: Optional[Credentials]) -> Optional[Credentials]:
    """
    Refresh expired credentials.

    Args:
        creds: The credentials to refresh.

    Returns:
        The refreshed credentials if successful, None otherwise.
    """
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            return creds
        except RefreshError as e:
            logging.error("Error refreshing credentials: %s", e)
    return None


def _get_new_credentials() -> Optional[Credentials]:
    """
    Get new credentials through OAuth flow.

    Returns:
        The newly obtained credentials, or None if an error occurs.
    """
    try:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        return flow.run_local_server(port=0)
    except Exception as e:
        logging.error("Error obtaining new credentials: %s", e)
        return None


def _save_credentials(creds: Credentials) -> None:
    """
    Save credentials to token file.

    Args:
        creds: The credentials to save.
    """
    try:
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    except IOError as e:
        logging.error("Error saving credentials: %s", e)


def authenticate_gmail() -> Optional[Credentials]:
    """
    Authenticate the user's Gmail account.

    Returns:
        The valid credentials for Gmail API access, or None if authentication fails.
    """
    try:
        creds = _load_credentials()
        if not creds or not creds.valid:
            creds = _refresh_credentials(creds) or _get_new_credentials()
            if creds:
                _save_credentials(creds)
            else:
                logging.error("Failed to obtain valid credentials.")
                return None
        return creds
    except Exception as e:
        logging.error("Error during authentication: %s", e)
        logging.exception("Exception details:")
        return None


def get_gmail_service() -> Optional[Resource]:
    """
    Get the Gmail API service.

    Returns:
        The Gmail API service object, or None if service creation fails.
    """
    try:
        creds = authenticate_gmail()
        if creds:
            return build("gmail", "v1", credentials=creds)
        else:
            logging.error("Authentication failed. Unable to create Gmail service.")
            return None
    except Exception as e:
        logging.error("Error creating Gmail service: %s", e)
        logging.exception("Exception details:")
        return None
