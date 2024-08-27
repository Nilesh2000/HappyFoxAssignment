"""
This module configures logging for the application.
"""

import logging


def configure_logging() -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("app.log")],
    )

    # Suppress logging from googleapiclient.discovery_cache
    logging.getLogger("googleapicliet.discovery_cache").setLevel(logging.ERROR)
