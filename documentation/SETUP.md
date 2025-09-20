# USCIS Case Status Tracker Setup Guide

This guide will help you set up and run the USCIS Case Status Tracker that connects to the official USCIS website to check your case status and send email notifications.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file:
```bash
cp env_example.txt .env
```

Edit the `.env` file with your actual USCIS case information:

```env
# USCIS Case Details
CASE_NUMBER=YSC2190123456  # Replace with your actual USCIS case number
SUBMISSION_DATE=2024-01-01  # Replace with your submission date
EMPLOYER_NAME=Your Employer Name

# Email Configuration (for notifications)
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password  # Gmail App Password
RECIPIENT_EMAIL=recipient@example.com
NOTIFICATION_METHOD=email

# Optional: Enable mock data for testing
ENABLE_MOCK_DATA=false
```

### 3. Test the Application

```bash
python test_api.py
```

This will test the connection to the USCIS website and show you the current status of your case.

### 4. Run the Main Application

```bash
python main.py
```

## 📋 What This Application Does

1. **Fetches Case Status**: Connects to USCIS website to get your current case status
2. **Sends Email Notifications**: Sends status updates via email
3. **Runs Automatically**: Can be scheduled to run daily via GitHub Actions or cron jobs
4. **Supports Multiple Forms**: Works with I-140, I-485, I-765, I-131, I-129, and other USCIS forms

## 📋 Detailed Setup Instructions

### Step 1: Environment Setup

1. **Python Version**: Ensure you have Python 3.8+ installed
2. **Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Your Case Information

1. **Find your USCIS case number** (e.g., YSC2190123456)
2. **Note your submission date** (when you filed the application)
3. **Update the `.env` file** with your information

### Step 4: Email Configuration (Optional)

If you want email notifications:

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
3. **Update the `.env` file** with your email credentials

### Step 5: Test the Setup

```bash
# Test API connection
python test_api.py

# Test full application (with mock data)
ENABLE_MOCK_DATA=true python main.py

# Test full application (with real USCIS website)
python main.py
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CASE_NUMBER` | Your USCIS case number | Required |
| `SUBMISSION_DATE` | Date you submitted the application | Required |
| `EMPLOYER_NAME` | Your employer's name | "Unknown Employer" |
| `SENDER_EMAIL` | Email for sending notifications | Optional |
| `SENDER_PASSWORD` | Gmail app password | Optional |
| `RECIPIENT_EMAIL` | Email to receive notifications | Optional |
| `ENABLE_MOCK_DATA` | Use mock data for testing | false |

### Supported Case Types

The application automatically detects and supports:
- **I-140**: Immigrant Petition for Alien Worker
- **I-485**: Application to Register Permanent Residence
- **I-765**: Application for Employment Authorization
- **I-131**: Application for Travel Document
- **I-129**: Petition for Nonimmigrant Worker
- **And more**: Any USCIS form with a case number

## 🧪 Testing

### Test API Connection Only

```bash
python test_api.py
```

### Test with Mock Data

```bash
ENABLE_MOCK_DATA=true python main.py
```

### Test Full Application

```bash
python main.py
```

## 📧 Email Notifications

The application sends email notifications with:
- Current case status
- Form type and case type
- Service center information
- Case details (if available)
- Timestamp of the check

To enable email notifications:

1. Set up Gmail App Password
2. Configure email settings in `.env`
3. Run the application

## 🔍 Troubleshooting

### Common Issues

1. **Website Connection Failed**
   - Check your internet connection
   - Verify the case number is correct
   - The USCIS website might be temporarily unavailable

2. **Email Not Sending**
   - Verify Gmail App Password is correct
   - Check 2-Factor Authentication is enabled
   - Ensure SMTP settings are correct

3. **Import Errors**
   - Run `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

4. **Case Not Found**
   - Verify your case number is correct
   - Check if the case exists in USCIS system
   - Try with a different case number for testing

### Debug Mode

Enable debug logging:

```bash
LOG_LEVEL=DEBUG python main.py
```

### Mock Data Testing

Test with mock data to verify the application works:

```bash
ENABLE_MOCK_DATA=true python main.py
```

## 🚀 Production Deployment

### GitHub Actions (Recommended)

1. Fork this repository
2. Add secrets in GitHub repository settings:
   - `CASE_NUMBER`
   - `SUBMISSION_DATE`
   - `EMPLOYER_NAME`
   - `SENDER_EMAIL`
   - `SENDER_PASSWORD`
   - `RECIPIENT_EMAIL`
3. The workflow will run automatically daily

### Local Cron Job

Add to your crontab:

```bash
# Run daily at 6 AM
0 6 * * * cd /path/to/uscis_tracker && python main.py
```

### Docker (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## 📊 Understanding the Output

The application provides:

1. **Current Status**: Your case's current status from USCIS
2. **Case Information**: Form type, case type, service center
3. **Email Notifications**: Daily updates (if configured)
4. **Logs**: Detailed logs in `uscis_tracker.log`

## 🔒 Security Notes

- Never commit your `.env` file
- Use GitHub Secrets for production
- Gmail App Passwords are more secure than regular passwords
- The application respects rate limits and is respectful to USCIS servers

## 📞 Support

If you encounter issues:

1. Check the logs in `uscis_tracker.log`
2. Run the test script: `python test_api.py`
3. Try with mock data: `ENABLE_MOCK_DATA=true python main.py`
4. Check the troubleshooting section above

## ⚠️ Disclaimer

This tool is for informational purposes only. It provides current status information from publicly available USCIS data and should not be considered as legal advice. Always consult with your immigration attorney for official guidance on your USCIS application.
