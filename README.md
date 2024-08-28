# HappyFox Assignment

Python scripts to fetch emails from Gmail, store them in a database, and perform rule-based operations on them.

## Table of Contents

- [Installation and Setup](#installation-and-setup)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [References](#references)
- [Video Demo](#video-demo)

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

5. Run the script to fetch and store emails in the database. Number of messages to be fetched is configurable and defaults to 25. (This step is to be done only once):

   ```
   python fetch_and_save_emails.py --num-messages 100
   ```

6. Run the script to apply rules to the emails in the database:

   ```
   python run_rule_engine.py
   ```

7. You can view logs in the generated `app.log` file.

## Tech Stack

- [Python 3](https://www.python.org/downloads/)
- [Google Cloud Platform](https://cloud.google.com/) (For Gmail API)
- [SQLite](https://www.sqlite.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pytest](https://docs.pytest.org/en/7.4.x/)

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

## Video Demo
