"""
This module defines the SQLAlchemy models for the email database.
"""

from typing import Any, Dict

from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Email(Base):
    """SQLAlchemy model for the emails table."""

    __tablename__ = "emails"

    id = Column(String, primary_key=True)
    subject = Column(String)
    sender = Column(String)
    date = Column(DateTime)
    body = Column(String)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Email object to a dictionary.

        Returns:
            A dictionary representation of the Email object.
        """
        return {"id": self.id, "subject": self.subject, "sender": self.sender, "date": self.date, "body": self.body}
