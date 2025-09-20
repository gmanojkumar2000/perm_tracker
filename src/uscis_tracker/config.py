"""
Configuration loader for the USCIS Case Status Tracker
Loads all config from environment variables using python-dotenv
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def getenv(key: str, default: str = "") -> str:
    """Get environment variable with fallback to default"""
    return os.getenv(key, default)

# Email Configuration
EMAIL_HOST = getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(getenv("EMAIL_PORT", 587))
EMAIL_USER = getenv("SENDER_EMAIL", "")  # Use SENDER_EMAIL for backward compatibility
EMAIL_PASSWORD = getenv("SENDER_PASSWORD", "")  # Use SENDER_PASSWORD for backward compatibility
EMAIL_RECIPIENTS = getenv("RECIPIENT_EMAIL", "").split(",") if getenv("RECIPIENT_EMAIL") else []  # Use RECIPIENT_EMAIL for backward compatibility

# Case Configuration
CASE_NUMBER = getenv("CASE_NUMBER", "")

# USCIS Case Configuration (for backward compatibility)
USCIS_CASE_NUMBER = getenv("USCIS_CASE_NUMBER", CASE_NUMBER)  # Use CASE_NUMBER as fallback
EMPLOYER_NAME = getenv("EMPLOYER_NAME", "Unknown Employer")
SUBMISSION_DATE = getenv("SUBMISSION_DATE", "2024-01-01")  # Default submission date

# Notification Configuration
NOTIFICATION_METHOD = getenv("NOTIFICATION_METHOD", "email").lower()
ENABLE_MOCK_DATA = getenv("ENABLE_MOCK_DATA", "false").lower() == "true"

# Mock Data Configuration
MOCK_USCIS_STATUS = getenv("MOCK_USCIS_STATUS", "Case Was Received")
MOCK_POSITION = int(getenv("MOCK_POSITION", 1500))
MOCK_TOTAL_APPLICATIONS = int(getenv("MOCK_TOTAL_APPLICATIONS", 5000))
MOCK_PROCESSING_RATE = int(getenv("MOCK_PROCESSING_RATE", 50))

# USCIS Scraper Configuration
USCIS_UPDATE_URL = getenv("USCIS_UPDATE_URL", "https://egov.uscis.gov/casestatus/mycasestatus.do")
SCRAPER_TIMEOUT = int(getenv("SCRAPER_TIMEOUT", 30))
SCRAPER_RETRIES = int(getenv("SCRAPER_RETRIES", 3))

# USCIS API OAuth2 Configuration
USCIS_CLIENT_ID = getenv("USCIS_CLIENT_ID", "OExAiBN0EMlP3hQ8QAo8DBSEaFXKNGT6")
USCIS_CLIENT_SECRET = getenv("USCIS_CLIENT_SECRET", "mmUsEvjseRU49U0Z")
USCIS_ACCESS_TOKEN_URL = getenv("USCIS_ACCESS_TOKEN_URL", "https://api-int.uscis.gov/oauth/accesstoken")
USCIS_API_BASE_URL = getenv("USCIS_API_BASE_URL", "https://api-int.uscis.gov/case-status")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/uscis_tracker.log")

# Security Configuration
ENCRYPTION_KEY = getenv("ENCRYPTION_KEY", "your-secret-key-here")

# Validation
if not EMAIL_USER or not EMAIL_PASSWORD:
    print("Warning: Email credentials not configured. Email notifications will not work.")
if not CASE_NUMBER:
    print("Warning: No case number configured. Please set CASE_NUMBER environment variable.") 