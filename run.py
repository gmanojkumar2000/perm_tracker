#!/usr/bin/env python3
"""
USCIS Case Status Tracker - Main Entry Point
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from uscis_tracker.main import main

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 