"""
This script applies operations to emails in the database using Gmail API.

The rules for the operations are specified in the rules.json file.

Each rule is a JSON object with the following structure:
{
    "name": "Rule Name",
    "description": "Rule Description",
    "type": "any/all",
    "condition": [
        {
            "field": "From / Subject / Body / Date Received",
            "predicate": "contains / not contains / equals / not equals / less than / greater than",
            "value": "Hello"
        }
    ],
    "action": [
        {
            "type": "move / mark",
            "value": "label name / read / unread"
        }
    ]
}
"""

import datetime
import json
import logging
import sqlite3
from typing import Any, Dict, List

from fetch import fetch_emails, get_gmail_service
from save_emails_to_db import save_emails_to_db

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class EmailRule:
    """A class representing an email rule.

    Attributes:
        name (str): The name of the rule.
        description (str): A description of the rule.
        type (str): The type of the rule ('any' or 'all').
        conditions (List[Dict[str, str]]): A list of conditions for the rule.
        actions (List[Dict[str, str]]): A list of actions for the rule.
    """

    def __init__(self, rule_data: Dict[str, Any]):
        """Initialize an EmailRule instance.

        Args:
            rule_data: A dictionary containing the rule data.
        """
        self.name: str = rule_data["name"]
        self.description: str = rule_data["description"]
        self.type: str = rule_data["type"]
        self.conditions: List[Dict[str, str]] = rule_data["condition"]
        self.actions: List[Dict[str, str]] = rule_data["action"]
        logging.info(f"Initialized rule: {self.name}")

    def evaluate(self, email: Dict[str, Any]) -> bool:
        """Evaluate if the rule applies to the given email.

        Args:
            email: A dictionary containing email data.

        Returns:
            A boolean indicating whether the rule applies to the email.
        """
        evaluation_function = all if self.type == "all" else any
        result = evaluation_function(self.evaluate_condition(cond, email) for cond in self.conditions)
        logging.info(f"Rule '{self.name}' evaluation result: {result}")
        return result

    def evaluate_condition(self, condition: Dict[str, str], email: Dict[str, Any]) -> bool:
        """Evaluate a single condition for the given email.

        Args:
            condition: A dictionary containing the condition details.
            email: A dictionary containing email data.

        Returns:
            A boolean indicating whether the condition is met.
        """
        field: str = condition["field"].lower()
        predicate: str = condition["predicate"].lower()
        value: str = condition["value"].lower()

        field_value: str = self.get_field_value(email, field)

        if field in ["from", "subject", "body"]:
            result = self.evaluate_text_condition(field_value, predicate, value)
        elif field == "date received":
            result = self.evaluate_date_condition(field_value, predicate, value)
        else:
            result = False

        logging.info(
            f"Condition evaluation: field='{field}', predicate='{predicate}', value='{value}', result={result}"
        )
        return result

    def get_field_value(self, email: Dict[str, Any], field: str) -> str:
        """Get the value of the specified field from the email.

        Args:
            email: A dictionary containing email data.
            field: The field to retrieve from the email.

        Returns:
            The value of the specified field as a lowercase string.
        """
        field_mapping: Dict[str, str] = {
            "from": "sender",
            "subject": "subject",
            "body": "body",
            "date received": "date",
        }
        value = email.get(field_mapping.get(field, ""), "").lower()
        logging.debug(f"Field '{field}' value: {value}")
        return value

    def evaluate_text_condition(self, field_value: str, predicate: str, value: str) -> bool:
        """Evaluate text-based conditions.

        Args:
            field_value: The value of the field to evaluate.
            predicate: The predicate to use for evaluation.
            value: The value to compare against.

        Returns:
            A boolean indicating whether the condition is met.
        """
        if predicate == "contains":
            return value in field_value
        elif predicate == "does not contain":
            return value not in field_value
        elif predicate == "equals":
            return value == field_value
        elif predicate == "not equals":
            return value != field_value
        logging.warning(f"Unknown predicate '{predicate}' for text condition")
        return False

    def evaluate_date_condition(self, field_value: str, predicate: str, value: str) -> bool:
        """Evaluate date-based conditions.

        Args:
            field_value: The value of the date field to evaluate.
            predicate: The predicate to use for evaluation.
            value: The date value to compare against.

        Returns:
            A boolean indicating whether the condition is met.
        """
        try:
            email_date: datetime.datetime = datetime.datetime.strptime(field_value, "%Y-%m-%d %H:%M:%S")
            rule_date: datetime.datetime = datetime.datetime.strptime(value, "%d/%m/%Y")

            if predicate == "less than":
                return email_date < rule_date
            elif predicate == "greater than":
                return email_date > rule_date
            logging.warning(f"Unknown predicate '{predicate}' for date condition")
        except ValueError as e:
            logging.error(f"Error parsing date: {e}")
        return False

    def apply_actions(self, email: Dict[str, Any]) -> None:
        """Apply the specified actions to the given email.

        Args:
            email: A dictionary containing email data.
        """
        for action in self.actions:
            action_type: str = action["type"]
            action_value: str = action["value"]

            if action_type == "move":
                self.move_email(email, action_value)
            elif action_type == "mark":
                if action_value == "read":
                    self.mark_email_as_read(email)
                elif action_value == "unread":
                    self.mark_email_as_unread(email)
            logging.info(f"Applied action: type='{action_type}', value='{action_value}' to email ID: {email['id']}")

    def move_email(self, email: Dict[str, Any], label: str) -> None:
        """Move the given email to the specified label.

        Args:
            email: A dictionary containing email data.
            label: The label to move the email to.
        """
        service = get_gmail_service()
        try:
            service.users().messages().modify(
                userId="me", id=email["id"], body={"addLabelIds": [label], "removeLabelIds": ["INBOX"]}
            ).execute()
            logging.info(f"Moved email ID: {email['id']} to label: {label}")
        except Exception as e:
            logging.error(f"Error moving email: {e}")

    def mark_email_as_read(self, email: Dict[str, Any]) -> None:
        """Mark the given email as read.

        Args:
            email: A dictionary containing email data.
        """
        service = get_gmail_service()
        try:
            service.users().messages().modify(
                userId="me", id=email["id"], body={"removeLabelIds": ["UNREAD"]}
            ).execute()
            logging.info(f"Marked email ID: {email['id']} as read")
        except Exception as e:
            logging.error(f"Error marking email as read: {e}")

    def mark_email_as_unread(self, email: Dict[str, Any]) -> None:
        """Mark the given email as unread.

        Args:
            email: A dictionary containing email data.
        """
        service = get_gmail_service()
        try:
            service.users().messages().modify(userId="me", id=email["id"], body={"addLabelIds": ["UNREAD"]}).execute()
            logging.info(f"Marked email ID: {email['id']} as unread")
        except Exception as e:
            logging.error(f"Error marking email as unread: {e}")


class EmailRuleEngine:
    """A class representing an email rule engine.

    Attributes:
        rules (List[EmailRule]): A list of EmailRule instances.
        emails (List[Dict[str, Any]]): A list of email data dictionaries.
    """

    def __init__(self):
        """Initialize an EmailRuleEngine instance."""
        self.rules: List[EmailRule] = self.load_rules()
        self.emails: List[Dict[str, Any]] = self.fetch_emails_from_db()
        logging.info(f"Initialized EmailRuleEngine with {len(self.rules)} rules and {len(self.emails)} emails")

    def load_rules(self) -> List[EmailRule]:
        """Load rules from the rules.json file.

        Returns:
            A list of EmailRule instances.
        """
        try:
            with open("rules.json", "r") as f:
                rules = [EmailRule(rule_data) for rule_data in json.load(f)]
            logging.info(f"Loaded {len(rules)} rules from rules.json")
            return rules
        except Exception as e:
            logging.error(f"Error loading rules: {e}")
            return []

    def fetch_emails_from_db(self) -> List[Dict[str, Any]]:
        """Fetch emails from the SQLite database.

        Returns:
            A list of dictionaries containing email data.
        """
        try:
            conn = sqlite3.connect("db.sqlite3")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM emails")
            columns: List[str] = [column[0] for column in cursor.description]
            emails: List[Dict[str, Any]] = [dict(zip(columns, row)) for row in cursor.fetchall()]
            conn.close()
            logging.info(f"Fetched {len(emails)} emails from the database")
            return emails
        except Exception as e:
            logging.error(f"Error fetching emails from database: {e}")
            return []

    def apply_rules(self) -> None:
        """Apply rules to emails in the database."""
        for rule in self.rules:
            logging.info(f"Applying rule: {rule.name}")
            for email in self.emails:
                if rule.evaluate(email):
                    rule.apply_actions(email)
        logging.info("Finished applying all rules")


if __name__ == "__main__":
    logging.info("Starting email rule application process")
    emails = fetch_emails()
    save_emails_to_db(emails)
    engine = EmailRuleEngine()
    engine.apply_rules()
    logging.info("Email rule application process completed")
