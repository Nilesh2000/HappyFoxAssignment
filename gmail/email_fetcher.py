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

from .authenticate import GmailAuthenticator


def fetch_emails(num_messages: int = 100) -> List[Dict[str, Any]]:
    """
    Fetch emails from the user's Gmail account.

    Args:
        num_messages: Number of messages to fetch. Defaults to 100.

    Returns:
        A list of dictionaries containing email data.
    """
    logging.info("Starting to fetch emails")
    try:
        service = GmailAuthenticator.get_gmail_service()
        messages = _get_messages(service, num_messages)
        emails = [_parse_email(service, message["id"]) for message in messages]
        logging.info(f"Fetched {len(emails)} emails")
        return emails
    except Exception as e:
        logging.error(f"Error fetching emails: {e}")
        logging.exception("Exception details:")
        return []


def _get_messages(service: Resource, num_messages: int) -> List[Dict[str, Any]]:
    """
    Get the messages from the user's Gmail account.

    Args:
        service: The Gmail API service object.
        num_messages: Number of messages to retrieve.

    Returns:
        A list of message dictionaries.
    """
    logging.info(f"Fetching {num_messages} messages from Gmail")
    try:
        results = service.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=num_messages).execute()
        messages = results.get("messages", [])
        logging.info(f"Retrieved {len(messages)} messages")
        return messages
    except Exception as e:
        logging.error(f"Error getting messages: {e}")
        logging.error(traceback.format_exc())
        return []


def _parse_email(service: Resource, message_id: str) -> Dict[str, Any]:
    """
    Parse the email data.

    Args:
        service: The Gmail API service object.
        message_id: The ID of the email message.

    Returns:
        A dictionary containing parsed email data.
    """
    logging.info(f"Parsing email with ID: {message_id}")
    try:
        email = service.users().messages().get(userId="me", id=message_id).execute()
        email_data = _extract_email_data(email, message_id)
        logging.info(
            f"Parsed email: Subject: {email_data['subject']}, From: {email_data['sender']}, Date: {email_data['date']}"
        )
        return email_data
    except Exception as e:
        logging.error(f"Error parsing email with ID {message_id}: {e}")
        logging.error(traceback.format_exc())
        return {"id": message_id, "subject": "", "sender": "", "date": None, "body": ""}


def _extract_email_data(email: Dict[str, Any], message_id: str) -> Dict[str, Any]:
    """
    Extract email data from the email object.

    Args:
        email: The email object from Gmail API.
        message_id: The ID of the email message.

    Returns:
        A dictionary containing extracted email data.
    """
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
    return email_data


def _parse_date(date_string: str) -> Optional[datetime]:
    """
    Parse the date string from email header.

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
        logging.warning(f"Unable to parse date: {date_string}")
        return None


def _get_email_body(email: Dict[str, Any]) -> str:
    """
    Get the email body.

    Args:
        email: The email message dictionary.

    Returns:
        The decoded email body as a string.
    """
    logging.info("Extracting email body")
    payload = email.get("payload", {})
    body_data = _extract_body_data(payload)

    if body_data:
        decoded_body = _decode_body(body_data)
        logging.info(f"Email body extracted, length: {len(decoded_body)} characters")
        return decoded_body

    logging.warning("No email body found")
    return ""


def _extract_body_data(payload: Dict[str, Any]) -> Optional[str]:
    """
    Extract body data from email payload.

    Args:
        payload: The email payload dictionary.

    Returns:
        The body data as a string, or None if not found.
    """
    if "parts" in payload:
        # If the email has parts, use the first part
        payload = payload["parts"][0]
    return payload.get("body", {}).get("data")


def _decode_body(body_data: str) -> str:
    """
    Decode the base64 encoded body.

    Args:
        body_data: The base64 encoded body data.

    Returns:
        The decoded body as a string.
    """
    return base64.urlsafe_b64decode(body_data).decode("utf-8")
