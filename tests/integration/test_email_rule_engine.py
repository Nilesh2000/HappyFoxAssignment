from unittest.mock import MagicMock, patch

import pytest

from email_rule_engine import EmailRuleEngine
from rules.email_rule import EmailRule


@pytest.fixture
def mock_db_manager():
    mock_manager = MagicMock()
    mock_manager.fetch_emails.return_value = [
        {
            "id": "12345",
            "subject": "Important Test Email",
            "sender": "test@example.com",
            "date": "2023-04-01 12:00:00",
            "body": "This is a test email body.",
        },
        {
            "id": "67890",
            "subject": "Unimportant Email",
            "sender": "noreply@example.com",
            "date": "2023-04-02 12:00:00",
            "body": "This is another test email body.",
        },
    ]
    return mock_manager


@pytest.fixture
def mock_rule_loader():
    return [
        EmailRule(
            {
                "name": "Test Rule",
                "description": "A test rule",
                "type": "all",
                "condition": [
                    {"field": "From", "predicate": "contains", "value": "test@example.com"},
                    {"field": "Subject", "predicate": "contains", "value": "important"},
                ],
                "action": [{"type": "move", "value": "TestLabel"}],
            }
        )
    ]


@patch("email_rule_engine.load_rules")
@patch("email_rule_engine.DatabaseManager")
def test_email_rule_engine(mock_db_manager_class, mock_load_rules, mock_db_manager, mock_rule_loader):
    mock_db_manager_class.return_value = mock_db_manager
    mock_load_rules.return_value = mock_rule_loader

    engine = EmailRuleEngine()

    # Mock the apply_actions method to avoid actual API calls
    with patch.object(EmailRule, "apply_actions") as mock_apply_actions:
        engine.apply_rules()

        # Check that apply_actions was called once for the matching email
        assert mock_apply_actions.call_count == 1
        mock_apply_actions.assert_called_with(mock_db_manager.fetch_emails.return_value[0])


# Add more tests for different scenarios and edge cases
