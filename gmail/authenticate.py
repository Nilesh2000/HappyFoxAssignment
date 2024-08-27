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


class GmailAuthenticator:
    """
    A class to handle Gmail authentication and service creation.
    """

    SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
    TOKEN_FILE = "token.json"
    CREDENTIALS_FILE = "credentials.json"

    @classmethod
    def _load_credentials(cls) -> Optional[Credentials]:
        """
        Load credentials from token file if it exists.

        Returns:
            The loaded credentials if the token file exists, None otherwise.
        """
        try:
            if os.path.exists(cls.TOKEN_FILE):
                return Credentials.from_authorized_user_file(cls.TOKEN_FILE, cls.SCOPES)
        except Exception as e:
            logging.error(f"Error loading credentials: {e}")
        return None

    @staticmethod
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
                logging.error(f"Error refreshing credentials: {e}")
        return None

    @classmethod
    def _get_new_credentials(cls) -> Optional[Credentials]:
        """
        Get new credentials through OAuth flow.

        Returns:
            The newly obtained credentials, or None if an error occurs.
        """
        try:
            flow = InstalledAppFlow.from_client_secrets_file(cls.CREDENTIALS_FILE, cls.SCOPES)
            return flow.run_local_server(port=0)
        except Exception as e:
            logging.error(f"Error obtaining new credentials: {e}")
            return None

    @classmethod
    def _save_credentials(cls, creds: Credentials) -> None:
        """
        Save credentials to token file.

        Args:
            creds: The credentials to save.
        """
        try:
            with open(cls.TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
        except IOError as e:
            logging.error(f"Error saving credentials: {e}")

    @classmethod
    def authenticate_gmail(cls) -> Optional[Credentials]:
        """
        Authenticate the user's Gmail account.

        Returns:
            The valid credentials for Gmail API access, or None if authentication fails.
        """
        try:
            creds = cls._load_credentials()
            if not creds or not creds.valid:
                creds = cls._refresh_credentials(creds) or cls._get_new_credentials()
                if creds:
                    cls._save_credentials(creds)
                else:
                    logging.error("Failed to obtain valid credentials.")
                    return None
            return creds
        except Exception as e:
            logging.error(f"Error during authentication: {e}")
            logging.exception("Exception details:")
            return None

    @classmethod
    def get_gmail_service(cls) -> Optional[Resource]:
        """
        Get the Gmail API service.

        Returns:
            The Gmail API service object, or None if service creation fails.
        """
        try:
            creds = cls.authenticate_gmail()
            if creds:
                return build("gmail", "v1", credentials=creds)
            else:
                logging.error("Authentication failed. Unable to create Gmail service.")
                return None
        except Exception as e:
            logging.error(f"Error creating Gmail service: {e}")
            logging.exception("Exception details:")
            return None
