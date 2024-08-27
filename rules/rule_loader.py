"""
This module handles loading rules from the rules.json file.
"""

import json
import logging
from typing import List

from .rule_processor import EmailRule


def load_rules() -> List[EmailRule]:
    """
    Load rules from the rules.json file.

    Returns:
        A list of EmailRule instances.
    """
    try:
        with open("rules.json", "r") as f:
            rules = [EmailRule(rule_data) for rule_data in json.load(f)]
        logging.info("Loaded %d rules from rules.json", len(rules))
        return rules
    except json.JSONDecodeError as e:
        logging.error("Error parsing rules.json: %s", e)
    except IOError as e:
        logging.error("Error reading rules.json: %s", e)
    except Exception as e:
        logging.error("Unexpected error loading rules: %s", e)
        logging.exception("Exception details:")
    return []
