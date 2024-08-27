"""
This module manages database operations for emails.
"""

import logging
from typing import Any, Dict, List

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base, Email


class DatabaseManager:
    """A class to manage database operations for emails."""

    def __init__(self, db_url: str = "sqlite:///db.sqlite3") -> None:
        """
        Initialize the DatabaseManager.

        Args:
            db_url: The database URL. Defaults to 'sqlite:///db.sqlite3'.
        """
        logging.info(f"Initializing DatabaseManager with URL: {db_url}")
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def _get_session(self) -> Session:
        """Create and return a new database session."""
        return self.Session()

    def _close_session(self, session: Session) -> None:
        """Close the given database session."""
        session.close()

    def _add_email_to_session(self, session: Session, email_data: Dict[str, Any]) -> None:
        """Add a single email to the session."""
        new_email = Email(
            id=email_data["id"],
            subject=email_data["subject"],
            sender=email_data["sender"],
            date=email_data["date"],
            body=email_data["body"],
        )
        session.add(new_email)

    def save_emails(self, emails: List[Dict[str, Any]]) -> None:
        """
        Save a list of emails to the database.

        Args:
            emails: A list of dictionaries containing email data.
        """
        logging.info(f"Starting to save {len(emails)} emails to the database")
        session = self._get_session()
        try:
            for email in emails:
                self._add_email_to_session(session, email)
            session.commit()
            logging.info(f"Finished saving {len(emails)} emails to the database")
        except Exception as e:
            session.rollback()
            logging.error(f"Error saving emails to database: {e}")
            logging.exception("Exception details:")
        finally:
            self._close_session(session)

    def fetch_emails(self) -> List[Dict[str, Any]]:
        """
        Fetch all emails from the database.

        Returns:
            A list of dictionaries containing email data.
        """
        logging.info("Fetching emails from the database")
        session = self._get_session()
        try:
            emails = session.query(Email).all()
            return [email.to_dict() for email in emails]
        except Exception as e:
            logging.error(f"Error fetching emails from database: {e}")
            logging.exception("Exception details:")
            return []
        finally:
            self._close_session(session)
