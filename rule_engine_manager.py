"""
This module contains the EmailRuleEngine class for applying rules to emails.
"""

import logging
from typing import Any, Dict, List

from db.database_manager import DatabaseManager
from rules.rule_loader import load_rules
from rules.rule_processor import EmailRule


class EmailRuleEngine:
    """A class to manage and apply email rules."""

    def __init__(self, rules_path: str) -> None:
        """Initialize the EmailRuleEngine with rules and emails from the database."""
        self.rules: List[EmailRule] = load_rules(rules_path)
        self.db_manager = DatabaseManager()
        self.emails: List[Dict[str, Any]] = self.db_manager.fetch_emails()
        logging.info(f"Initialized EmailRuleEngine with {len(self.rules)} rules and {len(self.emails)} emails")

    def apply_rules(self) -> None:
        """Apply all rules to all emails in the database."""
        for rule in self.rules:
            logging.info(f"Applying rule: {rule.name}")
            for email in self.emails:
                try:
                    if rule.evaluate(email):
                        rule.apply_actions(email)
                except Exception:
                    logging.error(f"Error applying rule '{rule.name}' to email ID: {email['id']}")
                    logging.exception("Exception details:")
        logging.info("Finished applying all rules")
