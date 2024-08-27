"""
This module defines the EmailRule class for evaluating and applying rules to emails.
"""

import datetime
import logging
import traceback
from typing import Any, Dict, List

from gmail.authenticate import get_gmail_service


class EmailRule:
    """A class representing an email rule.

    Attributes:
        name: The name of the rule.
        description: A description of the rule.
        type: The type of the rule ('any' or 'all').
        conditions: A list of conditions for the rule.
        actions: A list of actions for the rule.
    """

    def __init__(self, rule_data: Dict[str, Any]) -> None:
        """Initialize an EmailRule instance.

        Args:
            rule_data: A dictionary containing the rule data.
        """
        self.name: str = rule_data["name"]
        self.description: str = rule_data["description"]
        self.type: str = rule_data["type"]
        self.conditions: List[Dict[str, str]] = rule_data["condition"]
        self.actions: List[Dict[str, str]] = rule_data["action"]
        logging.info("Initialized rule: %s", self.name)

    def evaluate(self, email: Dict[str, Any]) -> bool:
        """Evaluate if the rule applies to the given email.

        Args:
            email: A dictionary containing email data.

        Returns:
            A boolean indicating whether the rule applies to the email.
        """
        evaluation_function = all if self.type == "all" else any
        result = evaluation_function(self.evaluate_condition(cond, email) for cond in self.conditions)
        logging.info("Rule '%s' evaluation result: %s", self.name, result)
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
            "Condition evaluation: field='%s', predicate='%s', value='%s', result=%s", field, predicate, value, result
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
        value = str(email.get(field_mapping.get(field, ""), "")).lower()
        logging.debug("Field '%s' value: %s", field, value)
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
        logging.warning("Unknown predicate '%s' for text condition", predicate)
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
            logging.warning("Unknown predicate '%s' for date condition", predicate)
        except ValueError as e:
            logging.error("Error parsing date: %s", e)
        return False

    def apply_actions(self, email: Dict[str, Any]) -> None:
        """Apply the specified actions to the given email.

        Args:
            email: A dictionary containing email data.
        """
        for action in self.actions:
            action_type: str = action["type"]
            action_value: str = action["value"]

            try:
                if action_type == "move":
                    self.move_email(email, action_value)
                elif action_type == "mark":
                    if action_value == "read":
                        self.mark_email_as_read(email)
                    elif action_value == "unread":
                        self.mark_email_as_unread(email)
                logging.info(
                    "Applied action: type='%s', value='%s' to email ID: %s", action_type, action_value, email["id"]
                )
            except Exception:
                logging.error("Error applying action: %s %s to email ID: %s", action_type, action_value, email["id"])
                logging.error(traceback.format_exc())

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
            logging.info("Moved email ID: %s to label: %s", email["id"], label)
        except Exception:
            logging.error("Error moving email ID: %s to label: %s", email["id"], label)
            logging.error(traceback.format_exc())

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
            logging.info("Marked email ID: %s as read", email["id"])
        except Exception as e:
            logging.error("Error marking email as read: %s", e)
            logging.error(traceback.format_exc())

    def mark_email_as_unread(self, email: Dict[str, Any]) -> None:
        """Mark the given email as unread.

        Args:
            email: A dictionary containing email data.
        """
        service = get_gmail_service()
        try:
            service.users().messages().modify(userId="me", id=email["id"], body={"addLabelIds": ["UNREAD"]}).execute()
            logging.info("Marked email ID: %s as unread", email["id"])
        except Exception as e:
            logging.error("Error marking email as unread: %s", e)
            logging.error(traceback.format_exc())
