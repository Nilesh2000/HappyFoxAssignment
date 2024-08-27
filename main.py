"""
This script applies operations to emails in the database using Gmail API.
"""

import logging
from typing import Any, Dict, List

from db.database_manager import DatabaseManager
from email_rule_engine import EmailRuleEngine
from gmail.fetch import fetch_emails

# Configure logging
from utils.logging_config import configure_logging


def main() -> None:
    """Main function to run the email rule application process."""
    configure_logging()

    try:
        logging.info("Starting email rule application process")

        # Fetch emails from Gmail
        emails: List[Dict[str, Any]] = fetch_emails()

        # Save emails to database
        db_manager = DatabaseManager()
        db_manager.save_emails(emails)

        # Apply rules to emails
        engine = EmailRuleEngine()
        engine.apply_rules()

        logging.info("Email rule application process completed")
    except Exception:
        logging.error("An unexpected error occurred during the email rule application process")
        logging.exception("Exception details:")


if __name__ == "__main__":
    main()
