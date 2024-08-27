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
        logging.info(f"Loaded {len(rules)} rules from rules.json")
        return rules
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing rules.json: {e}")
    except IOError as e:
        logging.error(f"Error reading rules.json: {e}")
    except Exception as e:
        logging.error(f"Unexpected error loading rules: {e}")
        logging.exception("Exception details:")
    return []
