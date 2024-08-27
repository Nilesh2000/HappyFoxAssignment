"""
This script saves the emails fetched from the Gmail API to a SQLite database using SQLAlchemy.
"""

import logging
import traceback
from typing import Dict, List

from sqlalchemy import Column, DateTime, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

Base = declarative_base()


class Email(Base):
    """SQLAlchemy model for the emails table."""

    __tablename__ = "emails"

    id = Column(String, primary_key=True)
    subject = Column(String)
    sender = Column(String)
    date = Column(DateTime)
    body = Column(String)


class DatabaseManager:
    """Class to manage database operations."""

    def __init__(self, db_url: str = "sqlite:///db.sqlite3"):
        """
        Initialize the DatabaseManager.

        Args:
            db_url (str): The database URL. Defaults to 'sqlite:///db.sqlite3'.
        """
        logging.info(f"Initializing DatabaseManager with URL: {db_url}")
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def create_table(self) -> None:
        """Create the emails table if it doesn't exist."""
        logging.info("Creating emails table if it doesn't exist")
        Base.metadata.create_all(self.engine)

    def insert_email(self, email: Dict[str, str]) -> None:
        """
        Insert a single email into the table.

        Args:
            email (Dict[str, str]): A dictionary containing email data.
        """
        logging.info(f"Inserting email with ID: {email['id']}")
        session = self.Session()
        try:
            new_email = Email(
                id=email["id"], subject=email["subject"], sender=email["sender"], date=email["date"], body=email["body"]
            )
            session.add(new_email)
            session.commit()
            logging.info(f"Successfully inserted email with ID: {email['id']}")
        except Exception as e:
            session.rollback()
            logging.error(f"Error inserting email with ID {email['id']}: {str(e)}")
            logging.error(traceback.format_exc())
        finally:
            session.close()


def save_emails_to_db(emails: List[Dict[str, str]]) -> None:
    """
    Save the emails to a SQLite database.

    Args:
        emails (List[Dict[str, str]]): A list of dictionaries containing email data.
    """
    logging.info(f"Starting to save {len(emails)} emails to the database")
    try:
        manager = DatabaseManager()
        manager.create_table()

        for email in emails:
            manager.insert_email(email)

        logging.info(f"Finished saving {len(emails)} emails to the database")
    except Exception as e:
        logging.error(f"Error saving emails to database: {e}")
        logging.error(traceback.format_exc())
