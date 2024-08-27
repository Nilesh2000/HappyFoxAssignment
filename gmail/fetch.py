"""
This module fetches emails from the user's Gmail account using the Gmail API.
"""

import base64
import logging
import traceback
from datetime import datetime
from email.utils import mktime_tz, parsedate_tz
from typing import Any, Dict, List, Optional

from googleapiclient.discovery import Resource

from .authenticate import get_gmail_service


def fetch_emails(num_messages: int = 25) -> List[Dict[str, Any]]:
    """Fetch emails from the user's Gmail account.

    Args:
        num_messages: Number of messages to fetch. Defaults to 25.

    Returns:
        A list of dictionaries containing email data.
    """
    logging.info("Starting to fetch emails")
    try:
        service = get_gmail_service()
        messages = _get_messages(service, num_messages)
        emails = [_parse_email(service, message["id"]) for message in messages]
        logging.info("Fetched %d emails", len(emails))
        return emails
    except Exception as e:
        logging.error("Error fetching emails: %s", e)
        logging.exception("Exception details:")
        return []


def _get_messages(service: Resource, num_messages: int) -> List[Dict[str, Any]]:
    """Get the messages from the user's Gmail account.

    Args:
        service: The Gmail API service object.
        num_messages: Number of messages to retrieve.

    Returns:
        A list of message dictionaries.
    """
    logging.info("Fetching %d messages from Gmail", num_messages)
    try:
        results = service.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=num_messages).execute()
        messages = results.get("messages", [])
        logging.info("Retrieved %d messages", len(messages))
        return messages
    except Exception as e:
        logging.error("Error getting messages: %s", e)
        logging.error(traceback.format_exc())
        return []


def _parse_email(service: Resource, message_id: str) -> Dict[str, Any]:
    """Parse the email data.

    Args:
        service: The Gmail API service object.
        message_id: The ID of the email message.

    Returns:
        A dictionary containing parsed email data.
    """
    logging.info("Parsing email with ID: %s", message_id)
    try:
        email = service.users().messages().get(userId="me", id=message_id).execute()
        headers = email.get("payload", {}).get("headers", [])

        email_data = {"id": message_id, "subject": "", "sender": "", "date": None, "body": ""}

        for header in headers:
            if header["name"] == "Subject":
                email_data["subject"] = header["value"]
            elif header["name"] == "From":
                email_data["sender"] = header["value"]
            elif header["name"] == "Date":
                email_data["date"] = _parse_date(header["value"])

        email_data["body"] = _get_email_body(email)

        logging.info(
            "Parsed email: Subject: %s, From: %s, Date: %s",
            email_data["subject"],
            email_data["sender"],
            email_data["date"],
        )
        return email_data
    except Exception as e:
        logging.error("Error parsing email with ID %s: %s", message_id, e)
        logging.error(traceback.format_exc())
        return {"id": message_id, "subject": "", "sender": "", "date": None, "body": ""}


def _parse_date(date_string: str) -> Optional[datetime]:
    """Parse the date string from email header.

    Args:
        date_string: The raw date string from email header.

    Returns:
        Parsed datetime object or None if parsing fails.
    """
    parsed_date = parsedate_tz(date_string)
    if parsed_date:
        timestamp = mktime_tz(parsed_date)
        return datetime.fromtimestamp(timestamp)
    else:
        logging.warning("Unable to parse date: %s", date_string)
        return None


def _get_email_body(email: Dict[str, Any]) -> str:
    """Get the email body.

    Args:
        email: The email message dictionary.

    Returns:
        The decoded email body as a string.
    """
    logging.info("Extracting email body")
    payload = email.get("payload", {})
    if "parts" in payload:
        # If the email has parts, use the first part
        payload = payload["parts"][0]

    body_data = payload.get("body", {}).get("data")
    if body_data:
        # Decode the base64 encoded body
        decoded_body = base64.urlsafe_b64decode(body_data).decode("utf-8")
        logging.info("Email body extracted, length: %d characters", len(decoded_body))
        return decoded_body
    logging.warning("No email body found")
    return ""
