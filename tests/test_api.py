#!/usr/bin/env python3
"""
USCIS Case Status Tracker - Test Suite
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from uscis_tracker.case_status_api import CaseStatusAPI
from uscis_tracker.main import main
import logging

def test_uscis_api():
    """Test the USCIS API functionality"""
    print("🚀 USCIS Case Status Tracker - Test Suite")
    print("=" * 50)
    
    # Test with a sample case number
    case_number = "IOE0933489493"
    print(f"Testing USCIS API with case number: {case_number}")
    
    try:
        api = CaseStatusAPI()
        status = api.get_case_status(case_number)
        
        if status:
            print("✅ API test successful!")
            print(f"Case Number: {status.get('case_number', 'Unknown')}")
            print(f"Status: {status.get('status', 'Unknown')}")
            print(f"Form Type: {status.get('form_type', 'Unknown')}")
            print(f"Case Type: {status.get('case_type', 'Unknown')}")
            print(f"Office: {status.get('office', 'Unknown')}")
            print(f"Last Updated: {status.get('last_updated', 'Unknown')}")
            print(f"Details: {status.get('details', 'Unknown')}")
            print(f"Data Source: {status.get('data_source', 'Unknown')}")
            print(f"Method: {status.get('method', 'Unknown')}")
            return True
        else:
            print("❌ API test failed - no result returned")
            return False
            
    except Exception as e:
        print(f"❌ API test failed with error: {e}")
        return False

def test_full_application():
    """Test the full application flow"""
    print("\n🧪 Testing full application...")
    
    try:
        success = main()
        if success:
            print("✅ Full application test successful!")
            return True
        else:
            print("❌ Full application test failed!")
            return False
    except Exception as e:
        print(f"❌ Full application test failed with error: {e}")
        return False

if __name__ == "__main__":
    # Test API
    api_success = test_uscis_api()
    
    # Test full application
    app_success = test_full_application()
    
    # Overall result
    if api_success and app_success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
