"""
This script fetches emails from Gmail and saves them to the database.
"""

import argparse
import logging
from typing import Any, Dict, List

from db.database_manager import DatabaseManager
from gmail.fetch import fetch_emails

# Configure logging
from utils.logging_config import configure_logging


def main(num_messages: int) -> None:
    """Main function to fetch emails and save them to the database."""
    configure_logging()

    try:
        logging.info("Starting email fetch and save process")

        # Fetch emails from Gmail
        emails: List[Dict[str, Any]] = fetch_emails(num_messages)

        # Save emails to database
        db_manager = DatabaseManager()
        db_manager.save_emails(emails)

        logging.info("Email fetch and save process completed")
    except Exception:
        logging.error("An unexpected error occurred during the email fetch and save process")
        logging.exception("Exception details:")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Email fetch and save process")
    parser.add_argument("--num_messages", type=int, default=25, help="Number of messages to fetch from Gmail")
    args = parser.parse_args()

    main(args.num_messages)
