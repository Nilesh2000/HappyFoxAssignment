"""
This script fetches emails from the user's Gmail account using the Gmail API.

It provides functions to retrieve, parse, and extract information from emails,
including subject, sender, date, and body content.
"""

import base64
import logging
from datetime import datetime
from email.utils import mktime_tz, parsedate_tz
from typing import Any, Dict, List, Optional

from googleapiclient.discovery import Resource

from authenticate import get_gmail_service

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def fetch_emails(num_messages: int = 25) -> List[Dict[str, Any]]:
    """
    Fetch emails from the user's Gmail account.

    Args:
        num_messages (int): Number of messages to fetch. Defaults to 25.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing email data.
    """
    logger.info("Starting to fetch emails")
    service = get_gmail_service()
    messages = _get_messages(service, num_messages)
    emails = [_parse_email(service, message["id"]) for message in messages]
    logger.info(f"Fetched {len(emails)} emails")
    return emails


def _get_messages(service: Resource, num_messages: int) -> List[Dict[str, Any]]:
    """
    Get the messages from the user's Gmail account.

    Args:
        service (Resource): The Gmail API service object.
        num_messages (int): Number of messages to retrieve.

    Returns:
        List[Dict[str, Any]]: A list of message dictionaries.
    """
    logger.info(f"Fetching {num_messages} messages from Gmail")
    results = service.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=num_messages).execute()
    messages = results.get("messages", [])
    logger.info(f"Retrieved {len(messages)} messages")
    return messages


def _parse_email(service: Resource, message_id: str) -> Dict[str, Any]:
    """
    Parse the email data.

    Args:
        service (Resource): The Gmail API service object.
        message_id (str): The ID of the email message.

    Returns:
        Dict[str, Any]: A dictionary containing parsed email data.
    """
    logger.info(f"Parsing email with ID: {message_id}")
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

    logger.info(
        f"Parsed email: Subject: {email_data['subject']}, From: {email_data['sender']}, Date: {email_data['date']}"
    )
    return email_data


def _parse_date(date_string: str) -> Optional[datetime]:
    """
    Parse the date string from email header.

    Args:
        date_string (str): The raw date string from email header.

    Returns:
        Optional[datetime]: Parsed datetime object or None if parsing fails.
    """
    parsed_date = parsedate_tz(date_string)
    if parsed_date:
        timestamp = mktime_tz(parsed_date)
        return datetime.fromtimestamp(timestamp)
    else:
        logger.warning(f"Unable to parse date: {date_string}")
        return None


def _get_email_body(email: Dict[str, Any]) -> str:
    """
    Get the email body.

    Args:
        email (Dict[str, Any]): The email message dictionary.

    Returns:
        str: The decoded email body as a string.
    """
    logger.info("Extracting email body")
    payload = email.get("payload", {})
    if "parts" in payload:
        # If the email has parts, use the first part
        payload = payload["parts"][0]

    body_data = payload.get("body", {}).get("data")
    if body_data:
        # Decode the base64 encoded body
        decoded_body = base64.urlsafe_b64decode(body_data).decode("utf-8")
        logger.info(f"Email body extracted, length: {len(decoded_body)} characters")
        return decoded_body
    logger.warning("No email body found")
    return ""


if __name__ == "__main__":
    logger.info("Starting email fetching process")
    emails = fetch_emails()
    logger.info(f"Email fetching process completed. Total emails fetched: {len(emails)}")
