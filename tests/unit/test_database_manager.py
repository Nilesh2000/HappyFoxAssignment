import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.database_manager import DatabaseManager
from db.models import Base


@pytest.fixture(scope="module")
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


@pytest.fixture(scope="module")
def db_manager(test_db):
    return DatabaseManager("sqlite:///:memory:")


def test_save_emails(db_manager):
    emails = [
        {
            "id": "12345",
            "subject": "Test Email",
            "sender": "test@example.com",
            "date": "2023-04-01 12:00:00",
            "body": "This is a test email body.",
        }
    ]
    db_manager.save_emails(emails)
    fetched_emails = db_manager.fetch_emails()
    assert len(fetched_emails) == 1
    assert fetched_emails[0]["id"] == "12345"


def test_fetch_emails(db_manager):
    fetched_emails = db_manager.fetch_emails()
    assert isinstance(fetched_emails, list)
    assert all(isinstance(email, dict) for email in fetched_emails)
