import json
from unittest.mock import mock_open, patch

import pytest

from rules.rule_loader import load_rules


@pytest.fixture
def sample_rules():
    return [
        {
            "name": "Test Rule 1",
            "description": "A test rule",
            "type": "all",
            "condition": [{"field": "From", "predicate": "contains", "value": "test@example.com"}],
            "action": [{"type": "move", "value": "TestLabel"}],
        },
        {
            "name": "Test Rule 2",
            "description": "Another test rule",
            "type": "any",
            "condition": [{"field": "Subject", "predicate": "contains", "value": "important"}],
            "action": [{"type": "mark", "value": "read"}],
        },
    ]


def test_load_rules(sample_rules):
    mock_json = json.dumps(sample_rules)
    with patch("builtins.open", mock_open(read_data=mock_json)):
        rules = load_rules()
        assert len(rules) == 2
        assert rules[0].name == "Test Rule 1"
        assert rules[1].name == "Test Rule 2"


def test_load_rules_file_not_found():
    with patch("builtins.open", side_effect=IOError):
        rules = load_rules()
        assert len(rules) == 0


def test_load_rules_invalid_json():
    with patch("builtins.open", mock_open(read_data="invalid json")):
        rules = load_rules()
        assert len(rules) == 0


# Add more tests for edge cases and error handling
