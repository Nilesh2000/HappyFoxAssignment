from unittest.mock import MagicMock, patch

import pytest

from gmail.fetch import _get_messages, _parse_email, fetch_emails


@pytest.fixture
def mock_gmail_service():
    mock_service = MagicMock()
    mock_service.users().messages().list().execute.return_value = {"messages": [{"id": "12345"}, {"id": "67890"}]}
    mock_service.users().messages().get().execute.return_value = {
        "id": "12345",
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Test Email"},
                {"name": "From", "value": "test@example.com"},
                {"name": "Date", "value": "Mon, 1 Apr 2023 12:00:00 +0000"},
            ],
            "body": {"data": "VGhpcyBpcyBhIHRlc3QgZW1haWwgYm9keS4="},  # Base64 encoded "This is a test email body."
        },
    }
    return mock_service


@patch("gmail.fetch.get_gmail_service")
def test_fetch_emails(mock_get_service, mock_gmail_service):
    mock_get_service.return_value = mock_gmail_service
    emails = fetch_emails(2)
    assert len(emails) == 2
    assert emails[0]["id"] == "12345"
    assert emails[0]["subject"] == "Test Email"
    assert emails[0]["sender"] == "test@example.com"
    assert emails[0]["body"] == "This is a test email body."


@patch("gmail.fetch.get_gmail_service")
def test_get_messages(mock_get_service, mock_gmail_service):
    mock_get_service.return_value = mock_gmail_service
    messages = _get_messages(mock_gmail_service, 2)
    assert len(messages) == 2
    assert messages[0]["id"] == "12345"


@patch("gmail.fetch.get_gmail_service")
def test_parse_email(mock_get_service, mock_gmail_service):
    mock_get_service.return_value = mock_gmail_service
    email = _parse_email(mock_gmail_service, "12345")
    assert email["id"] == "12345"
    assert email["subject"] == "Test Email"
    assert email["sender"] == "test@example.com"
    assert email["body"] == "This is a test email body."


# Add more tests for error handling and edge cases
