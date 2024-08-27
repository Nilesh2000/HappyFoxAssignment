"""
This module contains the EmailRuleEngine class for applying rules to emails.
"""

import logging
from typing import Any, Dict, List

from db.database_manager import DatabaseManager
from rules.email_rule import EmailRule
from rules.rule_loader import load_rules


class EmailRuleEngine:
    """A class to manage and apply email rules."""

    def __init__(self) -> None:
        """Initialize the EmailRuleEngine with rules and emails from the database."""
        self.rules: List[EmailRule] = load_rules()
        self.db_manager = DatabaseManager()
        self.emails: List[Dict[str, Any]] = self.db_manager.fetch_emails()
        logging.info("Initialized EmailRuleEngine with %d rules and %d emails", len(self.rules), len(self.emails))

    def apply_rules(self) -> None:
        """Apply all rules to all emails in the database."""
        for rule in self.rules:
            logging.info("Applying rule: %s", rule.name)
            for email in self.emails:
                try:
                    if rule.evaluate(email):
                        rule.apply_actions(email)
                except Exception:
                    logging.error("Error applying rule '%s' to email ID: %s", rule.name, email["id"])
                    logging.exception("Exception details:")
        logging.info("Finished applying all rules")
