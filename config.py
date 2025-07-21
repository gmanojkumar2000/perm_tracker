"""
Configuration loader for the PERM Labor Application Status Tracker
Loads all config from environment variables using python-dotenv
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Helper to get env with type casting and default
getenv = lambda key, default=None, cast=str: cast(os.getenv(key, default))

# PERM Application Configuration
PERM_CASE_NUMBER = getenv("PERM_CASE_NUMBER", "")
SUBMISSION_DATE = getenv("SUBMISSION_DATE", "")  # YYYY-MM-DD format
EMPLOYER_LETTER = getenv("EMPLOYER_LETTER", "")  # First letter of employer name
EMPLOYER_NAME = getenv("EMPLOYER_NAME", "")

# Notification Configuration
NOTIFICATION_METHOD = getenv("NOTIFICATION_METHOD", "email").lower()  # "email" or "telegram"

# Email Configuration
EMAIL_CONFIG = {
    "smtp_server": getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(getenv("SMTP_PORT", 587)),
    "sender_email": getenv("SENDER_EMAIL", ""),
    "sender_password": getenv("SENDER_PASSWORD", ""),
    "recipient_email": getenv("RECIPIENT_EMAIL", ""),
}

# Telegram Configuration (for future use)
TELEGRAM_CONFIG = {
    "bot_token": getenv("TELEGRAM_BOT_TOKEN", ""),
    "chat_id": getenv("TELEGRAM_CHAT_ID", ""),
}

# PERM Scraper Configuration
PERM_UPDATE_URL = getenv("PERM_UPDATE_URL", "https://permupdate.com")
SCRAPER_TIMEOUT = int(getenv("SCRAPER_TIMEOUT", 30))
SCRAPER_RETRIES = int(getenv("SCRAPER_RETRIES", 3))

# ETA Estimation Configuration
DEFAULT_PROCESSING_RATE = int(getenv("DEFAULT_PROCESSING_RATE", 50))  # applications per day
CONFIDENCE_LEVELS = {
    "high": float(getenv("CONFIDENCE_HIGH", 0.8)),
    "medium": float(getenv("CONFIDENCE_MEDIUM", 0.6)),
    "low": float(getenv("CONFIDENCE_LOW", 0.4))
}

# Logging Configuration
LOG_LEVEL = getenv("LOG_LEVEL", "INFO")
LOG_FILE = getenv("LOG_FILE", "perm_tracker.log")

# Security Configuration
ENABLE_MOCK_DATA = getenv("ENABLE_MOCK_DATA", "false").lower() == "true"
MOCK_POSITION = int(getenv("MOCK_POSITION", 1500))
MOCK_TOTAL_APPLICATIONS = int(getenv("MOCK_TOTAL_APPLICATIONS", 5000))
MOCK_PROCESSING_RATE = int(getenv("MOCK_PROCESSING_RATE", 50)) 