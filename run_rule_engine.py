import argparse
import logging

from rule_engine_manager import EmailRuleEngine
from utils.logging_config import configure_logging


def apply_rules():
    configure_logging()

    try:
        logging.info("Starting rule application process")

        rule_engine = EmailRuleEngine()
        rule_engine.apply_rules()

        logging.info("Rule application process completed")
    except Exception:
        logging.error("An unexpected error occurred during the rule application process")
        logging.exception("Exception details:")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Email rule application process")
    args = parser.parse_args()

    apply_rules()
