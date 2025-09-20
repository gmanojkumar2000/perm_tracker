"""
USCIS Case Status Tracker Package
A Python package for tracking USCIS case status using the official API
"""

__version__ = "1.0.0"
__author__ = "USCIS Tracker Team"
__description__ = "USCIS Case Status Tracker with OAuth2 API integration"

from .case_status_api import CaseStatusAPI
from .notifier import NotificationService, EmailNotificationService, get_notification_service
from .config import *

__all__ = [
    'CaseStatusAPI',
    'NotificationService', 
    'EmailNotificationService',
    'get_notification_service'
]
