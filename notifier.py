"""
Notifications Module
Handles email notifications for PERM status updates
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


class NotificationService:
    """Base class for notification services"""
    
    def send_status_update(self, case_number: str, status: Dict[str, Any], eta: Dict[str, Any], employer_name: str) -> bool:
        """Send PERM status update notification"""
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
            subject = f"PERM Status Update – {current_status}"
            body = self._create_email_body(case_number, status, eta, employer_name)
            
            # Create MIME message
            msg = MIMEMultipart()
            # Set display name for sender
            msg['From'] = f"PERM Tracker Bot <{self.sender_email}>"
            msg['To'] = ', '.join(self.recipient_emails)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"PERM status update sent successfully to {len(self.recipient_emails)} recipients: {', '.join(self.recipient_emails)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send PERM status update email: {e}")
            return False
    
    def _create_email_body(self, case_number: str, status: Dict[str, Any], eta: Dict[str, Any], employer_name: str) -> str:
        """Create HTML email body for PERM status update (approval status only, other details commented)"""
        current_status = status.get('status', 'Unknown')
        status_color = '#007bff'  # Default blue
        if 'approved' in current_status.lower():
            status_color = '#28a745'  # Green
        elif 'denied' in current_status.lower():
            status_color = '#dc3545'  # Red
        elif 'pending' in current_status.lower():
            status_color = '#ffc107'  # Yellow
        html_body = f"""
        <html>
        <body style='font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px;'>
            <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid {status_color};'>
                <h2 style='color: {status_color}; margin-top: 0;'>PERM Status Update – {case_number}</h2>
                <p style='color: #333; font-size: 1.2em;'><strong>Current Status:</strong> <span style='color: {status_color};'>{current_status}</span></p>
                <!--
                <p><strong>Position in Queue:</strong> {status.get('position_in_queue', 'Unknown')} of {status.get('total_applications', 'Unknown')}</p>
                <p><strong>Processing Rate:</strong> {status.get('processing_rate', 'Unknown')} applications/day</p>
                <p><strong>Last Processed Date:</strong> {status.get('last_processed_date', 'Unknown')}</p>
                <p><strong>Employer:</strong> {employer_name}</p>
                <p><strong>Estimated Processing Date:</strong> {eta.get('estimated_processing_date', 'Unknown')}</p>
                <p><strong>Estimated Approval Date:</strong> {eta.get('estimated_approval_date', 'Unknown')}</p>
                <p><strong>Days Remaining:</strong> {eta.get('days_remaining', 'Unknown')} days</p>
                <p><strong>Confidence Level:</strong> {eta.get('confidence_level', 'Unknown')}</p>
                <p><strong>Progress:</strong> {eta.get('progress_percentage', 'Unknown')}%</p>
                -->
                <p style='color: #666; font-size: 12px; margin-top: 20px;'>Report generated on {(datetime.now(tz=ZoneInfo('America/Los_Angeles')).strftime('%B %d, %Y at %I:%M %p %Z'))}</p>
            </div>
        </body>
        </html>
        """
        return html_body


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