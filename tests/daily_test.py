#!/usr/bin/env python3
"""
Daily USCIS API Test Script
Runs daily API calls to generate traffic for production access requirements
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import our modules
from uscis_tracker.case_status_api import CaseStatusAPI
from uscis_tracker import config

# Load environment variables
load_dotenv()

def setup_logging():
    """Setup logging for daily tests"""
    # Ensure logs directory exists
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'daily_api_tests.log')),
            logging.StreamHandler(sys.stdout)
        ]
    )

def run_daily_api_test():
    """Run daily API test to generate traffic"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=" * 60)
        logger.info(f"Daily USCIS API Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # Test with your real case number
        api = CaseStatusAPI()
        case_number = config.CASE_NUMBER
        
        logger.info(f"Testing case number: {case_number}")
        
        # Get case status
        status = api.get_case_status(case_number)
        
        if status:
            logger.info(f"API Test Successful")
            logger.info(f"   Status: {status.get('status', 'Unknown')}")
            logger.info(f"   Method: {status.get('method', 'Unknown')}")
            logger.info(f"   Data Source: {status.get('data_source', 'Unknown')}")
        else:
            logger.error("API Test Failed - No response")
            
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"Daily API test failed: {e}")
        return False

def main():
    """Main function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Daily USCIS API Test")
    
    success = run_daily_api_test()
    
    if success:
        logger.info("Daily test completed successfully")
        sys.exit(0)
    else:
        logger.error("Daily test failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
