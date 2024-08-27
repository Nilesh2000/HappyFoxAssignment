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

5. Run the script:
   ```
   python main.py
   ```

## Project Structure

```
.
├── .gitignore # Ignore files and directories
├── .pre-commit-config.yaml # Pre-commit configuration
├── Assignment.pdf # Assignment PDF
├── cz.json # Commitizen configuration
├── db # Database
│   ├── database_manager.py # Database manager
│   └── models.py # Database models
├── email_rule_engine.py # Email rule engine
├── gmail
│   ├── authenticate.py # Gmail authentication
│   └── fetch.py # Gmail fetch
├── main.py # Main script
├── README.md # README
├── requirements.txt # Requirements
├── rules # Rules
│   ├── email_rule.py # Email rule
│   └── rule_loader.py # Rule loader
├── rules.json # Rules
├── save_emails_to_db.py # Save emails to database
└── utils # Utils
    └── logging_config.py # Logging configuration
```

## Video Demo
