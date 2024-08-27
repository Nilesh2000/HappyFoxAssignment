from datetime import datetime

import pytest

from rules.email_rule import EmailRule


@pytest.fixture
def sample_rule():
    return EmailRule(
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


@pytest.fixture
def sample_email():
    return {
        "id": "12345",
        "subject": "Important Test Email",
        "sender": "test@example.com",
        "date": datetime(2023, 4, 1, 12, 0, 0),
        "body": "This is a test email body.",
    }


def test_evaluate_condition(sample_rule, sample_email):
    assert (
        sample_rule.evaluate_condition(
            {"field": "From", "predicate": "contains", "value": "test@example.com"}, sample_email
        )
        is True
    )
    assert (
        sample_rule.evaluate_condition(
            {"field": "Subject", "predicate": "contains", "value": "Unimportant"}, sample_email
        )
        is False
    )


def test_evaluate(sample_rule, sample_email):
    assert sample_rule.evaluate(sample_email) is True


def test_evaluate_date_condition(sample_rule):
    condition = {"field": "Date Received", "predicate": "less than", "value": "02/04/2023"}
    assert sample_rule.evaluate_date_condition("2023-04-01 12:00:00", "less than", condition["value"]) is True
    assert sample_rule.evaluate_date_condition("2023-04-03 12:00:00", "less than", condition["value"]) is False
