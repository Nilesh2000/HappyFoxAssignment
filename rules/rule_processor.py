"""
This module defines the EmailRule class for evaluating and applying rules to emails.
"""

import datetime
import logging
import traceback
from typing import Any, Dict, List, Optional

from googleapiclient.discovery import Resource

from gmail.authenticate import GmailAuthenticator


class EmailRule:
    """
    A class representing an email rule.

    Attributes:
        name: The name of the rule.
        description: A description of the rule.
        type: The type of the rule ('any' or 'all').
        conditions: A list of conditions for the rule.
        actions: A list of actions for the rule.
    """

    def __init__(self, rule_data: Dict[str, Any]) -> None:
        """
        Initialize an EmailRule instance.

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
        """
        Evaluate if the rule applies to the given email.

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
        """
        Evaluate a single condition for the given email.

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
        """
        Get the value of the specified field from the email.

        Args:
            email: A dictionary containing email data.
            field: The field to retrieve from the email.

        Returns:
            The value of the specified field as a lowercase string.
        """
        field_mapping: Dict[str, str] = {
            "from": "sender",
            "subject": "subject",
            "message": "body",
            "date received": "date",
        }
        value = str(email.get(field_mapping.get(field, ""), "")).lower()
        logging.debug(f"Field '{field}' value: {value}")
        return value

    def evaluate_text_condition(self, field_value: str, predicate: str, value: str) -> bool:
        """
        Evaluate text-based conditions.

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
        """
        Evaluate date-based conditions.

        Args:
            field_value: The value of the date field to evaluate.
            predicate: The predicate to use for evaluation.
            value: The date value to compare against.

        Returns:
            A boolean indicating whether the condition is met.
        """
        try:
            email_date: datetime.datetime = datetime.datetime.strptime(field_value, "%Y-%m-%d %H:%M:%S")

            num_days, unit = value.split()
            num_days = int(num_days)

            if unit == "d":
                days_to_subtract = num_days
            elif unit == "m":
                days_to_subtract = num_days * 30
            else:
                logging.warning(f"Unknown time unit '{unit}' for date condition")
                return False

            rule_date = datetime.datetime.now() - datetime.timedelta(days=days_to_subtract)

            if predicate == "less than":
                return email_date >= rule_date
            elif predicate == "greater than":
                return email_date <= rule_date

            logging.warning(f"Unknown predicate '{predicate}' for date condition")
            return False

        except ValueError as e:
            logging.error(f"Error parsing date: {e}")
        return False

    def apply_actions(self, email: Dict[str, Any]) -> None:
        """
        Apply the specified actions to the given email.

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
                logging.info(f"Applied action: type='{action_type}', value='{action_value}' to email ID: {email['id']}")
            except Exception:
                logging.error(f"Error applying action: {action_type} {action_value} to email ID: {email['id']}")
                logging.error(traceback.format_exc())

    def move_email(self, email: Dict[str, Any], target_label: str) -> None:
        """
        Move the given email to the specified label.

        Args:
            email: A dictionary containing email data.
            target_label: The label to move the email to.
        """
        service = GmailAuthenticator.get_gmail_service()
        label_id = self._get_label_id(service, target_label)

        if label_id:
            self._modify_email_labels(service, email["id"], label_id)
        else:
            logging.error(f"Label '{target_label}' not found for email ID: {email['id']}")

    def _get_label_id(self, service: Resource, target_label: str) -> Optional[str]:
        """
        Get the ID of the specified label from the user's Gmail account.

        Args:
            service: The Gmail API service object.
            target_label: The name of the label to find.

        Returns:
            The ID of the label if found, None otherwise.
        """
        try:
            results = service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])
            for label in labels:
                if label["name"] == target_label:
                    return label["id"]
            return None
        except Exception as e:
            logging.error(f"Error fetching labels: {e}")
            return None

    def _modify_email_labels(self, service: Resource, email_id: str, label_id: str) -> None:
        """
        Modify the labels of the specified email.

        Args:
            service: The Gmail API service object.
            email_id: The ID of the email to modify.
            label_id: The ID of the label to add.
        """
        try:
            service.users().messages().modify(
                userId="me", id=email_id, body={"addLabelIds": [label_id], "removeLabelIds": ["INBOX"]}
            ).execute()
            logging.info(f"Moved email ID: {email_id} to label ID: {label_id}")
        except Exception:
            logging.error(f"Error moving email ID: {email_id} to label ID: {label_id}")
            logging.error(traceback.format_exc())

    def mark_email_as_read(self, email: Dict[str, Any]) -> None:
        """
        Mark the given email as read.

        Args:
            email: A dictionary containing email data.
        """
        service = GmailAuthenticator.get_gmail_service()
        try:
            service.users().messages().modify(
                userId="me", id=email["id"], body={"removeLabelIds": ["UNREAD"]}
            ).execute()
            logging.info(f"Marked email ID: {email['id']} as read")
        except Exception as e:
            logging.error(f"Error marking email as read: {e}")
            logging.error(traceback.format_exc())

    def mark_email_as_unread(self, email: Dict[str, Any]) -> None:
        """
        Mark the given email as unread.

        Args:
            email: A dictionary containing email data.
        """
        service = GmailAuthenticator.get_gmail_service()
        try:
            service.users().messages().modify(userId="me", id=email["id"], body={"addLabelIds": ["UNREAD"]}).execute()
            logging.info(f"Marked email ID: {email['id']} as unread")
        except Exception as e:
            logging.error(f"Error marking email as unread: {e}")
            logging.error(traceback.format_exc())
