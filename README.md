# HappyFox Assignment

Python scripts to fetch emails from Gmail, store them in a database, and perform rule-based operations on them. ([Video Demo](https://youtu.be/Tbbc49QYREg))

## Table of Contents

- [Overview](#overview)
- [Installation and Setup](#installation-and-setup)
- [Usage](#usage)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [References](#references)
- [Contributors](#contributors)

## Overview

This project provides a set of Python scripts that allow you to:

1. Fetch emails from a Gmail account
2. Store the fetched emails in a local SQLite database
3. Apply customizable rules to process and manage the stored emails

## Installation and Setup

1. Clone the repository:

   ```
   git clone https://github.com/Nilesh2000/HappyFoxAssignment.git
   cd HappyFoxAssignment
   ```

2. Create and activate a virtual environment:

   ```
   python -m venv env
   source env/bin/activate  # On Windows, use `env\Scripts\activate`
   ```

3. Install the required packages:

   ```
   pip install -r requirements.txt
   ```

4. Set up Google Cloud Project and enable Gmail API:

   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Gmail API for your project
   - Create credentials (OAuth 2.0 Client ID) and download the `credentials.json` file
   - Place the `credentials.json` file in the project root directory

## Usage

1. Fetch and store emails:

   ```
   python fetch_and_save_emails.py --num-messages 100
   ```

   This script fetches emails from Gmail and stores them in the database. The number of messages to be fetched is configurable and defaults to 25. Use the `--num-messages` flag to specify a different number.

2. Apply rules to emails:

   ```
   python run_rule_engine.py --rules myrules.json
   ```

   This script applies rules to the emails stored in the database. You can specify a custom rules file using the `--rules` flag. The default rules file is `rules.json`.

3. View logs:

   Check the generated `app.log` file for detailed logging information.

## Tech Stack

- [Python 3](https://www.python.org/downloads/): Primary programming language
- [Google Cloud Platform](https://cloud.google.com/): For Gmail API integration
- [SQLite](https://www.sqlite.org/): Local database for storing emails
- [SQLAlchemy](https://www.sqlalchemy.org/): ORM for database operations
- [Pytest](https://docs.pytest.org/en/7.4.x/): For unit testing

## Project Structure

```
├── .gitignore # Ignore files and directories
├── .pre-commit-config.yaml # Pre-commit configuration
├── Assignment.pdf # Assignment PDF
├── README.md # This file
├── cz.json # Commitizen configuration
├── db
│   ├── database_manager.py # Database manager
│   └── models.py # Database models
├── fetch_and_save_emails.py # Script to fetch and store emails in the database
├── gmail
│   ├── authenticate.py # Gmail authentication
│   └── email_fetcher.py # Gmail email fetcher
├── requirements.txt # Project dependencies
├── rule_engine_manager.py # Rule engine manager
├── rules
│   ├── rule_loader.py # Rule loader
│   └── rule_processor.py # Rule processor
├── rules.json # Rules configuration
├── run_rule_engine.py # Script to apply rules to the emails in the database
├── rule_generator.py # Script to generate rules
└── utils
    └── logging_config.py # Logging configuration
```

## References

- [Google Gmail API Quickstart](https://developers.google.com/gmail/api/quickstart/python)
- [How to read emails from Gmail using Gmail API in Python?](https://www.geeksforgeeks.org/how-to-read-emails-from-gmail-using-gmail-api-in-python/?ref=asr1)
- [Convert Date String from Gmail to Timestamp Python](https://stackoverflow.com/questions/62092529/convert-date-string-from-gmail-to-timestamp-python)
- [Hide Git Ignored Files in Tree](https://unix.stackexchange.com/questions/291282/have-tree-hide-gitignored-files)
- [Do not log file_cache is only supported with oauth2client<4.0.0](https://stackoverflow.com/questions/40154672/importerror-file-cache-is-unavailable-when-using-python-client-for-google-ser)
- [Bump urllib3 to get rid of annoying warning](https://github.com/explosion/spaCy/discussions/12750)

## Contributors

- [Nilesh D](https://github.com/Nilesh2000) - Development and Documentation
