"""
This script authenticates the user's Gmail account using the Gmail API.

This module provides functions for handling OAuth 2.0 authentication flow
for the Gmail API, including loading, refreshing, and saving credentials.
"""

import logging
import os
import traceback
from typing import Optional

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Set the scope to gmail.modify so that we can read emails, move emails, add or remove labels, and mark as read, unread.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"


def load_credentials() -> Optional[Credentials]:
    """Load credentials from token file if it exists.

    Returns:
        Optional[Credentials]: The loaded credentials if the token file exists,
                               None otherwise.
    """
    try:
        if os.path.exists(TOKEN_FILE):
            return Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    except Exception as e:
        logging.error(f"Error loading credentials: {e}")
    return None


def refresh_credentials(creds: Optional[Credentials]) -> Optional[Credentials]:
    """Refresh expired credentials.

    Args:
        creds: The credentials to refresh.

    Returns:
        Optional[Credentials]: The refreshed credentials if successful,
                               None otherwise.
    """
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            return creds
        except RefreshError as e:
            logging.error(f"Error refreshing credentials: {e}")
    return None


def get_new_credentials() -> Optional[Credentials]:
    """Get new credentials through OAuth flow.

    Returns:
        Optional[Credentials]: The newly obtained credentials, or None if an error occurs.
    """
    try:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        return flow.run_local_server(port=0)
    except Exception as e:
        logging.error(f"Error obtaining new credentials: {e}")
        return None


def save_credentials(creds: Credentials) -> None:
    """Save credentials to token file.

    Args:
        creds: The credentials to save.
    """
    try:
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    except IOError as e:
        logging.error(f"Error saving credentials: {e}")


def authenticate_gmail() -> Optional[Credentials]:
    """Authenticate the user's Gmail account.

    This function attempts to load existing credentials, refresh them if
    expired, or obtain new credentials through the OAuth flow if necessary.

    Returns:
        Optional[Credentials]: The valid credentials for Gmail API access, or None if authentication fails.
    """
    try:
        creds = load_credentials()

        if not creds or not creds.valid:
            creds = refresh_credentials(creds) or get_new_credentials()
            if creds:
                save_credentials(creds)
            else:
                logging.error("Failed to obtain valid credentials.")
                return None

        return creds
    except Exception as e:
        logging.error(f"Error during authentication: {e}")
        logging.error(traceback.format_exc())
        return None


def get_gmail_service():
    """Get the Gmail API service.

    Returns:
        Resource: The Gmail API service object, or None if service creation fails.
    """
    try:
        creds = authenticate_gmail()
        if creds:
            return build("gmail", "v1", credentials=creds)
        else:
            logging.error("Authentication failed. Unable to create Gmail service.")
            return None
    except HttpError as e:
        logging.error(f"Error creating Gmail service: {e}")
        logging.error(traceback.format_exc())
        return None
    except Exception as e:
        logging.error(f"Unexpected error creating Gmail service: {e}")
        logging.error(traceback.format_exc())
        return None
