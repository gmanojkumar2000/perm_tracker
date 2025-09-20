# USCIS Case Status Tracker

A Python-based automation app that tracks USCIS case status daily using the official USCIS website.

## 🎯 Features

- **Daily Status Monitoring**: Automatically checks USCIS case status every day
- **Status Details**: Fetches the latest status, last update, and office from the USCIS website
- **Email Notifications**: Sends daily summary emails with current status and updates
- **GitHub Actions Integration**: Runs automatically via GitHub Actions scheduler
- **Mock Data Support**: Includes fallback data for testing when website is unavailable
- **Secure Configuration**: All sensitive data stored in environment variables
- **Multi-Form Support**: Works with I-140, I-485, I-765, I-131, I-129, and other USCIS forms

## 📦 Tech Stack

- **Language**: Python 3.11+
- **Libraries**: `requests`, `beautifulsoup4`, `smtplib`, `schedule`, `datetime`, `json`
- **Runtime**: GitHub Actions (daily scheduler)
- **Notifications**: Email (Gmail SMTP)

## 🏗️ Project Structure

```
uscis_tracker/
├── main.py                 # Main application orchestrator
├── config.py              # Configuration loader
├── case_status_api.py     # USCIS case status API module
├── notifier.py            # Email notification module
├── test_api.py            # Test script
├── env_example.txt        # Environment variables template
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── .github/
│   └── workflows/
│       └── daily_check.yml # GitHub Actions workflow
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd uscis_tracker
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Your Settings

Copy the example environment file and configure it:

```bash
cp env_example.txt .env
```

Edit the `.env` file with your actual configuration:

```env
# USCIS Case Details
CASE_NUMBER=YSC2190123456

# Email Configuration
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=recipient@example.com
NOTIFICATION_METHOD=email

# SMTP Configuration (optional - defaults to Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Telegram Configuration (for future use)
# TELEGRAM_BOT_TOKEN=your-bot-token
# TELEGRAM_CHAT_ID=your-chat-id

# Scraper Configuration
SCRAPER_TIMEOUT=30
SCRAPER_RETRIES=3

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=uscis_tracker.log

# Security Configuration
ENABLE_MOCK_DATA=false
MOCK_USCIS_STATUS=Case Was Received
MOCK_POSITION=1500
MOCK_TOTAL_APPLICATIONS=5000
MOCK_PROCESSING_RATE=50
```

### 4. Set Up Gmail App Password

For Gmail, you'll need to create an App Password:

1. Go to your Google Account settings
2. Navigate to Security → 2-Step Verification
3. Create an App Password for "Mail"
4. Use this password in your `.env` file

### 5. Test Locally

```bash
python test_api.py
```

### 6. Set Up GitHub Actions

1. Fork this repository to your GitHub account
2. Go to Settings → Secrets and variables → Actions
3. Add the following secrets:
   - `CASE_NUMBER`
   - `SENDER_EMAIL`
   - `SENDER_PASSWORD`
   - `RECIPIENT_EMAIL`
   - `NOTIFICATION_METHOD`
   - `SMTP_SERVER` (optional)
   - `SMTP_PORT` (optional)
   - `SCRAPER_TIMEOUT` (optional)
   - `SCRAPER_RETRIES` (optional)
   - `LOG_LEVEL` (optional)
   - `ENABLE_MOCK_DATA` (optional)
   - `MOCK_POSITION` (optional)
   - `MOCK_TOTAL_APPLICATIONS` (optional)
   - `MOCK_PROCESSING_RATE` (optional)

The workflow will run automatically every day at 6:00 AM PST.

## 📧 Email Format

The daily email includes:

- **Current Status**: Current case status from USCIS
- **Case Information**: Form type, case type, service center
- **Case Details**: Additional information from USCIS
- **Timestamp**: When the check was performed

## 🔧 Configuration Options

### USCIS Case Settings

- `CASE_NUMBER`: Your USCIS case number (e.g., YSC2190123456)

### Notification Settings

- `NOTIFICATION_METHOD`: "email" (Telegram support planned)
- `SENDER_EMAIL`: Gmail address for sending notifications
- `SENDER_PASSWORD`: Gmail app password
- `RECIPIENT_EMAIL`: Email address to receive updates
- `SMTP_SERVER`: SMTP server (default: smtp.gmail.com)
- `SMTP_PORT`: SMTP port (default: 587)

### Scraper Settings

- `SCRAPER_TIMEOUT`: Request timeout in seconds (default: 30)
- `SCRAPER_RETRIES`: Number of retry attempts (default: 3)

### Security Settings

- `ENABLE_MOCK_DATA`: Force use of mock data (default: false)
- `MOCK_POSITION`: Mock position in queue (default: 1500)
- `MOCK_TOTAL_APPLICATIONS`: Mock total applications (default: 5000)
- `MOCK_PROCESSING_RATE`: Mock processing rate (default: 50)

## 🛠️ Development

### Running Tests

```bash
# Test individual modules
python -c "from case_status_api import CaseStatusAPI; print('API OK')"
python -c "from notifier import get_notification_service; print('Notifier OK')"
```

### Adding New Features

1. **New Data Sources**: Extend `CaseStatusAPI` class
2. **Additional Notifications**: Implement new `NotificationService` subclass
3. **Enhanced Status Parsing**: Modify `_parse_html_response` method

## 🔒 Security Notes

- **Never commit your `.env` file** to version control (it's in .gitignore)
- Use GitHub Secrets for sensitive information in production
- Gmail App Passwords are more secure than regular passwords
- The scraper includes rate limiting to be respectful to USCIS servers
- All configuration is now environment-based for better security

## 📊 Mock Data

When the USCIS website cannot be reached, the system uses mock data for testing:

- Status: Configurable via `MOCK_USCIS_STATUS`
- Form Type: Automatically detected from case number

You can force mock data by setting `ENABLE_MOCK_DATA=true` in your `.env` file.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## ⚠️ Disclaimer

This tool is for informational purposes only. It provides current status information from publicly available USCIS data and should not be considered as legal advice. Always consult with your immigration attorney for official guidance on your USCIS application.

## 🆘 Troubleshooting

### Common Issues

1. **Email not sending**: Check Gmail App Password and 2FA settings
2. **Scraper failing**: The system will use mock data as fallback
3. **GitHub Actions not running**: Verify secrets are set correctly
4. **Import errors**: Ensure all dependencies are installed
5. **Configuration errors**: Check that all required environment variables are set

### Logs

Check the `uscis_tracker.log` file for detailed error messages and debugging information.

## 📞 Support

For issues and questions:
1. Check the logs in `uscis_tracker.log`
2. Review the troubleshooting section
3. Open an issue on GitHub with detailed information 