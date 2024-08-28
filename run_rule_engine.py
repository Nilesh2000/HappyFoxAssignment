import argparse
import logging
import os

from rule_engine_manager import EmailRuleEngine
from utils.logging_config import configure_logging


def apply_rules(rules_file):
    configure_logging()

    try:
        logging.info("Starting rule application process")

        # Get the absolute path of the current script
        base_path = os.path.dirname(os.path.abspath(__file__))
        # Construct the full path to the rules file
        full_rules_path = os.path.join(base_path, rules_file)

        rule_engine = EmailRuleEngine(full_rules_path)
        rule_engine.apply_rules()

        logging.info("Rule application process completed")
    except Exception:
        logging.error("An unexpected error occurred during the rule application process")
        logging.exception("Exception details:")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Email rule application process")
    parser.add_argument("--rules", type=str, default="rules.json", help="Relative path to the rules file")
    args = parser.parse_args()

    # Get the absolute path of the current script
    base_path = os.path.dirname(os.path.abspath(__file__))
    # Construct the full path to the rules file
    full_rules_path = os.path.join(base_path, args.rules)

    if not os.path.exists(full_rules_path):
        print(f"Error: Rules file '{full_rules_path}' does not exist.")
        exit(1)

    apply_rules(args.rules)
