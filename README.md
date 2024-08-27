# HappyFox Assignment

Python script that integrates with the Gmail API to perform rule-based operations on emails.

## Installation and Setup

1. Clone the repository:

   ```
   git clone https://github.com/Nilesh2000/gmail-rule-based-operations.git
   cd gmail-rule-based-operations
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

## Project Structure

```
.
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

## Video Demo
