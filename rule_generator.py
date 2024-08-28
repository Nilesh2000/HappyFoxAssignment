import json
import logging
import os
from typing import Any, Dict, List, Optional

import inquirer

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_input(prompt: str, choices: Optional[List[str]] = None) -> str:
    """
    Get user input with optional choices.

    Args:
        prompt: The prompt to display to the user.
        choices: Optional list of choices for the user to select from.

    Returns:
        The user's input as a string.
    """
    if choices:
        questions = [inquirer.List("value", message=prompt, choices=choices, carousel=True)]
        return inquirer.prompt(questions)["value"]
    return input(prompt).strip()


def get_conditions() -> List[Dict[str, str]]:
    """
    Get conditions for a rule from user input.

    Returns:
        A list of dictionaries representing conditions.
    """
    conditions = []
    field_choices = ["from", "to", "subject", "message", "date received"]
    predicate_choices = {
        "date received": ["less than", "greater than"],
        "default": ["contains", "does not contain", "equals", "not equals"],
    }

    while True:
        field = get_input("Select field name:", field_choices)
        predicate = get_input("Select predicate:", predicate_choices.get(field, predicate_choices["default"]))

        if field == "date received":
            value = get_date_value()
        else:
            value = get_input("Enter value: ")

        conditions.append({"field": field, "predicate": predicate, "value": value})
        logging.info(f"Added condition: field={field}, predicate={predicate}, value={value}")

        if get_input("Add another condition? (y/n): ").lower() != "y":
            break
    return conditions


def get_date_value() -> str:
    """
    Get a valid date value from user input.

    Returns:
        A string representing the date value.
    """
    while True:
        value = get_input("Enter value (number followed by D for days or M for months, e.g., '30 D'): ")
        parts = value.split()
        if len(parts) == 2 and parts[0].isdigit() and parts[1] in ["D", "M"]:
            return value
        logging.warning("Invalid format entered for date received.")


def get_actions() -> List[Dict[str, str]]:
    """
    Get actions for a rule from user input.

    Returns:
        A list of dictionaries representing actions.
    """
    actions = []
    action_type_choices = ["mark", "move"]

    while True:
        action_type = get_input("Select action type:", action_type_choices)
        value = (
            get_input("Select value:", ["read", "unread"])
            if action_type == "mark"
            else get_input("Enter label to move to: ")
        )

        actions.append({"type": action_type, "value": value})
        logging.info(f"Added action: type={action_type}, value={value}")

        if get_input("Add another action? (y/n): ").lower() != "y":
            break
    return actions


def generate_rule() -> Dict[str, Any]:
    """
    Generate a rule based on user input.

    Returns:
        A dictionary representing the generated rule.
    """
    rule = {
        "name": get_input("\nEnter rule name: "),
        "description": get_input("Enter rule description: "),
        "type": get_input("Select rule type:", ["any", "all"]),
        "condition": get_conditions(),
        "action": get_actions(),
    }
    logging.info(f"Generated rule: {rule['name']}")
    return preview_rule(rule)


def preview_rule(rule: Dict[str, Any]) -> Dict[str, Any]:
    """
    Preview a rule and ask for confirmation.

    Args:
        rule: The rule to preview.

    Returns:
        The confirmed rule or a new rule if not confirmed.
    """
    logging.info("Preview of generated rule:")
    logging.info(json.dumps(rule, indent=2))
    if get_input("\nIs this correct? (y/n): ").lower() != "y":
        logging.info("Rule not confirmed. Generating new rule.")
        return generate_rule()
    logging.info("Rule confirmed.")
    return rule


def preview_rules(rules: List[Dict[str, Any]]) -> bool:
    """
    Preview all rules and ask for confirmation.

    Args:
        rules: List of rules to preview.

    Returns:
        True if all rules are confirmed, False otherwise.
    """
    logging.info("Preview of all generated rules:\n")
    logging.info(json.dumps(rules, indent=2))
    confirmed = get_input("\nAre all rules correct? (y/n): ").lower() == "y"
    logging.info(f"All rules confirmed: {confirmed}")
    return confirmed


def save_rules(rules: List[Dict[str, Any]]) -> None:
    """
    Save rules to a JSON file.

    Args:
        rules: List of rules to save.
    """
    rules_folder = get_input("Enter folder name to save rules (default: rules): ") or "rules"
    os.makedirs(rules_folder, exist_ok=True)
    logging.info(f"Using directory: {rules_folder}")

    filename = get_input("Enter filename without extension to save rules (default: rules): ") or "rules"
    full_path = os.path.join(rules_folder, f"{filename}.json")

    try:
        with open(full_path, "w") as f:
            json.dump(rules, f, indent=2)
        logging.info(f"Rules saved to {full_path}")
    except IOError as e:
        logging.error(f"Error saving rules: {e}")


def main() -> None:
    """
    Main function to run the rule generator.
    """
    logging.info("Starting rule generator")
    rules = []
    while True:
        rules.append(generate_rule())
        if get_input("Add another rule? (y/n): ").lower() != "y":
            break

    if preview_rules(rules):
        save_rules(rules)
    else:
        logging.warning("Rules not saved due to user rejection")
    logging.info("Rule generator finished")


if __name__ == "__main__":
    main()
