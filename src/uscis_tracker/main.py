#!/usr/bin/env python3
"""
USCIS Case Status Tracker
Main script that checks USCIS case status and sends daily updates
"""

import os
import sys
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Import our modules
from .case_status_api import CaseStatusAPI
from .notifier import get_notification_service
from . import config

# Load environment variables
load_dotenv()

# Configure logging
def setup_logging():
    """Setup logging configuration"""
    # Ensure logs directory exists
    log_dir = os.path.dirname(config.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )


def get_case_status() -> Optional[Dict[str, Any]]:
    """Get current USCIS case status"""
    logger = logging.getLogger(__name__)
    try:
        api = CaseStatusAPI()
        logger.info(f"Fetching USCIS status for case: {config.CASE_NUMBER}")
        status = api.get_case_status(case_number=config.CASE_NUMBER)
        if status:
            logger.info(f"Successfully retrieved USCIS status: {status}")
            return status
        else:
            logger.error("Failed to get USCIS status from uscis.gov API")
            return None
    except Exception as e:
        logger.error(f"Error getting USCIS status: {e}")
        return None


def send_status_update(status: Dict[str, Any]) -> bool:
    """Send USCIS case status update notification"""
    logger = logging.getLogger(__name__)
    
    try:
        # Create email configuration from new config structure
        email_config = {
            "smtp_server": config.EMAIL_HOST,
            "smtp_port": config.EMAIL_PORT,
            "sender_email": config.EMAIL_USER,
            "sender_password": config.EMAIL_PASSWORD,
            "recipient_email": ",".join(config.EMAIL_RECIPIENTS)
        }
        
        # Get the appropriate notification service
        if config.NOTIFICATION_METHOD == "email":
            service = get_notification_service("email", email_config)
        else:
            logger.error(f"Unknown notification method: {config.NOTIFICATION_METHOD}")
            return False
        
        # Send the update (without ETA)
        success = service.send_status_update(
            case_number=config.CASE_NUMBER,
            status=status,
            eta={},  # Empty ETA since we're not using estimation
            employer_name=config.EMPLOYER_NAME
        )
        
        if success:
            logger.info(f"Status update sent successfully via {config.NOTIFICATION_METHOD}")
        else:
            logger.error(f"Failed to send status update via {config.NOTIFICATION_METHOD}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error sending status update: {e}")
        return False


def main() -> bool:
    """Main function to check USCIS case status and send notifications"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting USCIS Case Status Tracker")
    logger.info(f"Case Number: {config.CASE_NUMBER}")
    logger.info(f"Notification method: {config.NOTIFICATION_METHOD}")
    logger.info(f"Mock data enabled: {config.ENABLE_MOCK_DATA}")
    
    # Get case status
    status = get_case_status()
    if status is None:
        logger.error("Could not retrieve USCIS case status")
        return False
    
    logger.info(f"Current USCIS status: {status}")
    
    # Send notification with status only (no ETA)
    return send_status_update(status)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 