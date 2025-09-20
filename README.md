# USCIS Case Status Tracker

A Python application for tracking USCIS case status using the official USCIS API with OAuth2 authentication. This application can monitor various USCIS case types including I-140, I-485, I-765, I-131, I-129, and others.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env_example.txt .env

# Edit .env with your credentials
# Run the application
python main.py
```

## 📁 Project Structure

```
uscis_application_status_tracker/
├── src/uscis_tracker/          # Main package source code
│   ├── __init__.py            # Package initialization
│   ├── main.py                # Main application logic
│   ├── case_status_api.py     # USCIS API integration
│   ├── notifier.py            # Email notification system
│   └── config.py              # Configuration management
├── tests/                     # Test files
│   ├── test_api.py           # API testing
│   └── daily_test.py         # Daily API testing for production access
├── logs/                      # Application logs
├── documentation/             # Project documentation
│   ├── README.md             # Detailed setup guide
│   ├── SETUP.md              # Installation instructions
│   └── PRODUCTION_ACCESS_CHECKLIST.md  # Production access guide
├── .github/workflows/         # GitHub Actions workflows
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
└── env_example.txt           # Environment variables template
```

## 📚 Documentation

- **[📖 Detailed Setup Guide](documentation/README.md)** - Comprehensive setup and configuration instructions
- **[🔧 Installation Guide](documentation/SETUP.md)** - Step-by-step installation and configuration
- **[🚀 Production Access Guide](documentation/PRODUCTION_ACCESS_CHECKLIST.md)** - Guide for obtaining production API access

## ✨ Features

- **OAuth2 Authentication**: Secure API access using USCIS official OAuth2 credentials
- **Multiple Case Types**: Support for I-140, I-485, I-765, I-131, I-129, and other USCIS cases
- **Email Notifications**: Automated email updates for case status changes
- **Daily Testing**: Automated daily API calls for production access requirements
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **GitHub Actions**: Automated workflows for daily testing and deployment

## 🔧 Configuration

The application uses environment variables for configuration. Copy `env_example.txt` to `.env` and configure:

- **USCIS API Credentials**: Client ID, Client Secret, Access Token URL
- **Email Settings**: SMTP server, sender credentials, recipient emails
- **Case Information**: Your USCIS case number and employer details

## 🧪 Testing

```bash
# Test API functionality
python tests/test_api.py

# Run daily API test (for production access)
python tests/daily_test.py
```

## 🤖 Automation

The project includes GitHub Actions workflows for:
- **Daily API Testing**: Automated daily API calls to meet production access requirements
- **Status Monitoring**: Regular case status checks and notifications

## 📊 Current Status

- ✅ **Sandbox API Integration**: Working OAuth2 authentication with USCIS sandbox API
- ✅ **Email Notifications**: Functional email notification system
- ✅ **Error Handling**: Comprehensive error handling and logging
- ⏳ **Production Access**: Working towards production API access (requires 5 days of API traffic)

## 🛠️ Development

```bash
# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/

# Run linting
python -m flake8 src/
```

## 📄 License

This project is for personal use and educational purposes. Please ensure compliance with USCIS API terms of service.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For issues related to:
- **USCIS API**: Contact USCIS Developer Support at developersupport@uscis.dhs.gov
- **Application Issues**: Check the logs in the `logs/` directory
- **Configuration**: Refer to the [Setup Guide](documentation/SETUP.md)

---

**Note**: This application is designed for personal USCIS case tracking. Ensure you comply with all USCIS terms of service and data privacy requirements. 