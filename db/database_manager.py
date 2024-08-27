"""
This module manages database operations for emails.
"""

import logging
from typing import Any, Dict, List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base, Email


class DatabaseManager:
    """A class to manage database operations for emails."""

    def __init__(self, db_url: str = "sqlite:///db.sqlite3") -> None:
        """
        Initialize the DatabaseManager.

        Args:
            db_url: The database URL. Defaults to 'sqlite:///db.sqlite3'.
        """
        logging.info("Initializing DatabaseManager with URL: %s", db_url)
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def save_emails(self, emails: List[Dict[str, Any]]) -> None:
        """
        Save a list of emails to the database.

        Args:
            emails: A list of dictionaries containing email data.
        """
        logging.info("Starting to save %d emails to the database", len(emails))
        session = self.Session()
        try:
            for email in emails:
                new_email = Email(
                    id=email["id"],
                    subject=email["subject"],
                    sender=email["sender"],
                    date=email["date"],
                    body=email["body"],
                )
                session.add(new_email)
            session.commit()
            logging.info("Finished saving %d emails to the database", len(emails))
        except Exception as e:
            session.rollback()
            logging.error("Error saving emails to database: %s", e)
            logging.exception("Exception details:")
        finally:
            session.close()

    def fetch_emails(self) -> List[Dict[str, Any]]:
        """
        Fetch all emails from the database.

        Returns:
            A list of dictionaries containing email data.
        """
        logging.info("Fetching emails from the database")
        session = self.Session()
        try:
            emails = session.query(Email).all()
            return [email.to_dict() for email in emails]
        except Exception as e:
            logging.error("Error fetching emails from database: %s", e)
            logging.exception("Exception details:")
            return []
        finally:
            session.close()
