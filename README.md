# PERM Labor Application Status Tracker

A Python-based automation app that tracks US PERM labor application status daily using data from permupdate.com.

## 🎯 Features

- **Daily Status Monitoring**: Automatically checks PERM application status every day
- **Queue Position Tracking**: Identifies the position of your application in the current queue
- **ETA Estimation**: Calculates estimated approval dates based on processing trends
- **Email Notifications**: Sends daily summary emails with current status and updates
- **GitHub Actions Integration**: Runs automatically via GitHub Actions scheduler
- **Mock Data Support**: Includes fallback data for testing when scraping fails
- **Secure Configuration**: All sensitive data stored in environment variables

## 📦 Tech Stack

- **Language**: Python 3.11+
- **Libraries**: `requests`, `beautifulsoup4`, `smtplib`, `schedule`, `datetime`, `json`
- **Runtime**: GitHub Actions (daily scheduler)
- **Notifications**: Email (Gmail SMTP)

## 🏗️ Project Structure

```
perm_tracker/
├── main.py                 # Main application orchestrator
├── config.py              # Configuration loader
├── perm_scraper.py        # PERM data scraping module
├── estimate.py            # ETA estimation module
├── notifier.py            # Email notification module
├── config.json            # Sample configuration template
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── env_example.txt        # Environment variables template
├── .github/
│   └── workflows/
│       └── daily_check.yml # GitHub Actions workflow
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd perm_tracker
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
# PERM Application Details
PERM_CASE_NUMBER=A-12345-67890
SUBMISSION_DATE=2024-01-15
EMPLOYER_LETTER=A
EMPLOYER_NAME=Your Company Name

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
PERM_UPDATE_URL=https://permupdate.com
SCRAPER_TIMEOUT=30
SCRAPER_RETRIES=3

# ETA Estimation Configuration
DEFAULT_PROCESSING_RATE=50
CONFIDENCE_HIGH=0.8
CONFIDENCE_MEDIUM=0.6
CONFIDENCE_LOW=0.4

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=perm_tracker.log

# Security Configuration
ENABLE_MOCK_DATA=false
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
python main.py
```

### 6. Set Up GitHub Actions

1. Fork this repository to your GitHub account
2. Go to Settings → Secrets and variables → Actions
3. Add the following secrets:
   - `PERM_CASE_NUMBER`
   - `SUBMISSION_DATE`
   - `EMPLOYER_LETTER`
   - `EMPLOYER_NAME`
   - `SENDER_EMAIL`
   - `SENDER_PASSWORD`
   - `RECIPIENT_EMAIL`
   - `NOTIFICATION_METHOD`
   - `SMTP_SERVER` (optional)
   - `SMTP_PORT` (optional)
   - `PERM_UPDATE_URL` (optional)
   - `SCRAPER_TIMEOUT` (optional)
   - `SCRAPER_RETRIES` (optional)
   - `DEFAULT_PROCESSING_RATE` (optional)
   - `CONFIDENCE_HIGH` (optional)
   - `CONFIDENCE_MEDIUM` (optional)
   - `CONFIDENCE_LOW` (optional)
   - `LOG_LEVEL` (optional)
   - `ENABLE_MOCK_DATA` (optional)
   - `MOCK_POSITION` (optional)
   - `MOCK_TOTAL_APPLICATIONS` (optional)
   - `MOCK_PROCESSING_RATE` (optional)

The workflow will run automatically every day at 6:00 AM PST.

## 📧 Email Format

The daily email includes:

- **Current Status**: Position in queue, processing rate, last processed date
- **Estimated Timeline**: Processing date, approval date, days remaining
- **Confidence Level**: High/Medium/Low based on data quality
- **Progress Percentage**: Visual representation of queue progress
- **Next Steps**: Guidance for the immigration process

## 🔧 Configuration Options

### PERM Application Settings

- `PERM_CASE_NUMBER`: Your PERM case number (format: A-XXXXX-XXXXX)
- `SUBMISSION_DATE`: Date when PERM was submitted (YYYY-MM-DD)
- `EMPLOYER_LETTER`: First letter of employer name
- `EMPLOYER_NAME`: Full employer name

### Notification Settings

- `NOTIFICATION_METHOD`: "email" (Telegram support planned)
- `SENDER_EMAIL`: Gmail address for sending notifications
- `SENDER_PASSWORD`: Gmail app password
- `RECIPIENT_EMAIL`: Email address to receive updates
- `SMTP_SERVER`: SMTP server (default: smtp.gmail.com)
- `SMTP_PORT`: SMTP port (default: 587)

### Scraper Settings

- `PERM_UPDATE_URL`: URL for PERM status data (default: permupdate.com)
- `SCRAPER_TIMEOUT`: Request timeout in seconds (default: 30)
- `SCRAPER_RETRIES`: Number of retry attempts (default: 3)
- `DEFAULT_PROCESSING_RATE`: Applications processed per day (default: 50)

### ETA Estimation Settings

- `CONFIDENCE_HIGH`: High confidence threshold (default: 0.8)
- `CONFIDENCE_MEDIUM`: Medium confidence threshold (default: 0.6)
- `CONFIDENCE_LOW`: Low confidence threshold (default: 0.4)

### Security Settings

- `ENABLE_MOCK_DATA`: Force use of mock data (default: false)
- `MOCK_POSITION`: Mock position in queue (default: 1500)
- `MOCK_TOTAL_APPLICATIONS`: Mock total applications (default: 5000)
- `MOCK_PROCESSING_RATE`: Mock processing rate (default: 50)

## 🛠️ Development

### Running Tests

```bash
# Test individual modules
python -c "from perm_scraper import PERMScraper; print('Scraper OK')"
python -c "from estimate import ETAEstimator; print('Estimator OK')"
python -c "from notifier import get_notification_service; print('Notifier OK')"
```

### Adding New Features

1. **New Data Sources**: Extend `PERMScraper` class
2. **Additional Notifications**: Implement new `NotificationService` subclass
3. **Enhanced ETA**: Modify `ETAEstimator` with historical data analysis

## 🔒 Security Notes

- **Never commit your `.env` file** to version control (it's in .gitignore)
- Use GitHub Secrets for sensitive information in production
- Gmail App Passwords are more secure than regular passwords
- The scraper includes rate limiting to be respectful to permupdate.com
- All configuration is now environment-based for better security

## 📊 Mock Data

When the scraper cannot access permupdate.com, the system uses mock data for testing:

- Position in queue: Configurable via `MOCK_POSITION`
- Processing rate: Configurable via `MOCK_PROCESSING_RATE`
- Status: "Pending Review"
- ETA: Estimated based on current position and rate

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

This tool is for informational purposes only. It provides estimates based on publicly available data and should not be considered as legal advice. Always consult with your immigration attorney for official guidance on your PERM application.

## 🆘 Troubleshooting

### Common Issues

1. **Email not sending**: Check Gmail App Password and 2FA settings
2. **Scraper failing**: The system will use mock data as fallback
3. **GitHub Actions not running**: Verify secrets are set correctly
4. **Import errors**: Ensure all dependencies are installed
5. **Configuration errors**: Check that all required environment variables are set

### Logs

Check the `perm_tracker.log` file for detailed error messages and debugging information.

## 📞 Support

For issues and questions:
1. Check the logs in `perm_tracker.log`
2. Review the troubleshooting section
3. Open an issue on GitHub with detailed information 