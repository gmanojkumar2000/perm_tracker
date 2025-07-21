#!/usr/bin/env python3
"""
PERM Labor Application Status Tracker
Main script that checks PERM application status and sends daily updates
"""

import os
import sys
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Import our modules
from perm_scraper import PERMScraper
from estimate import ETAEstimator
from notifier import get_notification_service
import config

# Load environment variables
load_dotenv()

# Configure logging
def setup_logging():
    """Setup logging configuration to always log to perm_tracker.log"""
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('perm_tracker.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def load_credentials_from_env():
    """Load credentials from environment variables"""
    # Update email config with environment variables
    sender_email = os.getenv('SENDER_EMAIL')
    if sender_email:
        config.EMAIL_CONFIG['sender_email'] = sender_email
    sender_password = os.getenv('SENDER_PASSWORD')
    if sender_password:
        config.EMAIL_CONFIG['sender_password'] = sender_password
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    if recipient_email:
        config.EMAIL_CONFIG['recipient_email'] = recipient_email


def get_perm_status() -> Optional[Dict[str, Any]]:
    """Get current PERM application status"""
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize scraper
        scraper = PERMScraper()
        logger.info(f"Fetching PERM status for case: {config.PERM_CASE_NUMBER}")
        
        # Get the status
        status = scraper.get_perm_status(
            case_number=config.PERM_CASE_NUMBER,
            submission_date=config.SUBMISSION_DATE,
            employer_letter=config.EMPLOYER_LETTER
        )
        
        if status:
            logger.info(f"Successfully retrieved PERM status: {status}")
            return status
        else:
            logger.error("Failed to get PERM status from permupdate.com")
            return None
            
    except Exception as e:
        logger.error(f"Error getting PERM status: {e}")
        return None


def estimate_approval_eta(status: Dict[str, Any]) -> Dict[str, Any]:
    """Estimate approval ETA based on current status"""
    logger = logging.getLogger(__name__)
    
    try:
        estimator = ETAEstimator()
        eta = estimator.calculate_eta(
            position=status.get('position_in_queue', 0),
            processing_rate=status.get('processing_rate', config.DEFAULT_PROCESSING_RATE),
            submission_date=config.SUBMISSION_DATE
        )
        
        logger.info(f"Estimated approval ETA: {eta}")
        return eta
        
    except Exception as e:
        logger.error(f"Error estimating ETA: {e}")
        return {
            'estimated_approval_date': '2024-06-15',
            'days_remaining': 120,
            'confidence_level': 'Low',
            'progress_percentage': 50.0,
            'estimated_processing_date': '2024-03-15',
            'processing_rate': config.DEFAULT_PROCESSING_RATE,
            'position_in_queue': config.MOCK_POSITION,
            'submission_date': config.SUBMISSION_DATE,
            'is_fallback': True
        }


def send_status_update(status: Dict[str, Any], eta: Dict[str, Any]) -> bool:
    """Send PERM status update notification"""
    logger = logging.getLogger(__name__)
    
    try:
        # Get the appropriate notification service
        if config.NOTIFICATION_METHOD == "email":
            service = get_notification_service("email", config.EMAIL_CONFIG)
        else:
            logger.error(f"Unknown notification method: {config.NOTIFICATION_METHOD}")
            return False
        
        # Send the update
        success = service.send_status_update(
            case_number=config.PERM_CASE_NUMBER,
            status=status,
            eta=eta,
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


def main():
    """Main function to run the PERM tracker system"""
    logger = logging.getLogger(__name__)
    
    logger.info("Starting PERM Labor Application Status Tracker")
    logger.info(f"Case Number: {config.PERM_CASE_NUMBER}")
    logger.info(f"Submission Date: {config.SUBMISSION_DATE}")
    logger.info(f"Employer Name: {config.EMPLOYER_NAME}")
    logger.info(f"Notification method: {config.NOTIFICATION_METHOD}")
    logger.info(f"Mock data enabled: {config.ENABLE_MOCK_DATA}")
    
    # Load credentials from environment
    load_credentials_from_env()
    
    # Get current PERM status
    status = get_perm_status()
    
    if status is None:
        logger.error("Could not retrieve PERM status")
        return False
    
    logger.info(f"Current PERM status: {status}")
    
    # Estimate approval ETA
    eta = estimate_approval_eta(status)
    logger.info(f"Estimated approval ETA: {eta}")
    
    # Send status update
    return send_status_update(status, eta)


if __name__ == "__main__":
    setup_logging()
    success = main()
    sys.exit(0 if success else 1) 