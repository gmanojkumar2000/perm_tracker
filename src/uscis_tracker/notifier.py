"""
Notifications Module
Handles email notifications for USCIS case status updates
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo
from . import config

logger = logging.getLogger(__name__)


class NotificationService:
    """Base class for notification services"""
    
    def send_status_update(self, case_number: str, status: Dict[str, Any], eta: Dict[str, Any], employer_name: str) -> bool:
        """Send USCIS case status update notification"""
        raise NotImplementedError


class EmailNotificationService(NotificationService):
    """Email notification service using SMTP"""
    
    def __init__(self, config: Dict[str, Any]):
        self.smtp_server = config.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = config.get("smtp_port", 587)
        self.sender_email = config.get("sender_email", "")
        self.sender_password = config.get("sender_password", "")
        self.recipient_emails = config.get("recipient_email", "").split(',')
        
        # Clean up email addresses (remove whitespace)
        self.recipient_emails = [email.strip() for email in self.recipient_emails if email.strip()]
        
        if not all([self.sender_email, self.sender_password]) or not self.recipient_emails:
            raise ValueError("Email configuration incomplete. Please check sender_email, sender_password, and recipient_email.")
    
    def send_status_update(self, case_number: str, status: Dict[str, Any], eta: Dict[str, Any], employer_name: str) -> bool:
        """Send email status update to all recipients"""
        logger = logging.getLogger(__name__)
        
        try:
            # Create message
            current_status = status.get('status', 'Unknown')
            subject = f"Case Status Update – {current_status}"
            body = self._create_email_body(case_number, status, eta, employer_name)
            
            # Create MIME message
            msg = MIMEMultipart()
            # Set display name for sender
            msg['From'] = f"Case Status Tracker Bot <{self.sender_email}>"
            msg['To'] = ', '.join(self.recipient_emails)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Case status update sent successfully to {len(self.recipient_emails)} recipients: {', '.join(self.recipient_emails)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send case status update email: {e}")
            return False
    
    def _create_email_body(self, case_number: str, status: Dict[str, Any], eta: Dict[str, Any], employer_name: str) -> str:
        """Create HTML email body for USCIS case status update"""
        current_status = status.get('status', 'Unknown')
        form_type = status.get('form_type', 'Unknown')
        case_type = status.get('case_type', 'Unknown')
        
        # Set status color based on current status
        status_color = '#007bff'  # Default blue
        if 'approved' in current_status.lower():
            status_color = '#28a745'  # Green
        elif 'denied' in current_status.lower():
            status_color = '#dc3545'  # Red
        elif 'rfe' in current_status.lower() or 'request for evidence' in current_status.lower():
            status_color = '#fd7e14'  # Orange
        elif 'pending' in current_status.lower():
            status_color = '#ffc107'  # Yellow
        elif 'received' in current_status.lower():
            status_color = '#6f42c1'  # Purple
        
        # Build status details
        status_details = f"""
        <p><strong>Form Type:</strong> {form_type}</p>
        <p><strong>Case Type:</strong> {case_type}</p>
        <p><strong>Employer:</strong> {employer_name}</p>
        <p><strong>Last Updated:</strong> {status.get('last_updated', 'Unknown')}</p>
        """
        
        # Add service center information if available
        if form_type == 'I-140':
            service_center = self._extract_service_center_from_case_number(case_number)
            status_details += f"""
            <p><strong>Service Center:</strong> {service_center}</p>
            """
        
        # Add details if available
        details = status.get('details', '')
        details_section = ""
        if details and details.strip():
            details_section = f"""
            <div style='background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 15px 0;'>
                <h4 style='margin-top: 0;'>Case Details:</h4>
                <p style='margin-bottom: 0;'>{details}</p>
            </div>
            """
        
        html_body = f"""
        <html>
        <body style='font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px;'>
            <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid {status_color};'>
                <h2 style='color: {status_color}; margin-top: 0;'>USCIS Case Status Update</h2>
                <h3 style='color: #333;'>Case Number: {case_number}</h3>
                
                <div style='background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0;'>
                    <h4 style='margin-top: 0; color: {status_color};'>Current Status</h4>
                    <p style='color: #333; font-size: 1.2em; font-weight: bold;'>{current_status}</p>
                </div>
                
                <div style='background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0;'>
                    <h4 style='margin-top: 0;'>Case Information</h4>
                    {status_details}
                </div>
                
                {details_section}
                
                <p style='color: #666; font-size: 12px; margin-top: 20px;'>
                    Report generated on {(datetime.now(tz=ZoneInfo('America/Los_Angeles')).strftime('%B %d, %Y at %I:%M %p %Z'))}
                </p>
                
                <div style='background-color: #e9ecef; padding: 10px; border-radius: 5px; margin-top: 15px; font-size: 12px; color: #666;'>
                    <strong>Note:</strong> This is an automated status check. For official information, please visit 
                    <a href='https://egov.uscis.gov/casestatus/mycasestatus.do' target='_blank'>USCIS Case Status</a>.
                </div>
            </div>
        </body>
        </html>
        """
        return html_body
    
    def _extract_service_center_from_case_number(self, case_number: str) -> str:
        """Extract service center from case number"""
        if len(case_number) >= 3:
            prefix = case_number[:3]
            service_center_mapping = {
                'YSC': 'Vermont Service Center',
                'WAC': 'California Service Center',
                'LIN': 'Nebraska Service Center',
                'SRC': 'Texas Service Center',
                'MSC': 'Missouri Service Center',
                'IOE': 'Electronic Filing',
            }
            return service_center_mapping.get(prefix, 'Unknown Service Center')
        return 'Unknown Service Center'


class TelegramNotificationService(NotificationService):
    """Telegram notification service using bot API (placeholder for future use)"""
    
    def __init__(self, config: Dict[str, Any]):
        self.bot_token = config.get("bot_token")
        self.chat_id = config.get("chat_id")
        
        if not all([self.bot_token, self.chat_id]):
            raise ValueError("Telegram configuration incomplete. Please check bot_token and chat_id.")
    
    def send_status_update(self, case_number: str, status: Dict[str, Any], eta: Dict[str, Any], employer_name: str) -> bool:
        """Send Telegram status update"""
        # Placeholder for future implementation
        logger.warning("Telegram notifications not yet implemented")
        return False


def get_notification_service(method: str, config: Dict[str, Any]) -> NotificationService:
    """Factory function to get the appropriate notification service"""
    if method.lower() == "email":
        return EmailNotificationService(config)
    elif method.lower() == "telegram":
        return TelegramNotificationService(config)
    else:
        raise ValueError(f"Unknown notification method: {method}") 