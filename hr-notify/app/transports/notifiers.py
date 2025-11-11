from abc import ABC, abstractmethod
import logging
from typing import List
from datetime import datetime
import uuid

logger = logging.getLogger("hr-notify")

class Notifier(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, body: str) -> bool:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

class EmailNotifier(Notifier):
    def send(self, to: str, subject: str, body: str) -> bool:
        # Mock implementation - in production integrate with SMTP/Email service
        notification_id = str(uuid.uuid4())[:8]
        logger.info(f"📧 [EMAIL-{notification_id}] To: {to}, Subject: {subject}, Body: {body[:100]}...")
        
        # Simulate successful send
        print(f"🚀 EMAIL SENT: To: {to} | Subject: {subject}")
        return True

    def get_name(self) -> str:
        return "email"

class WhatsAppNotifier(Notifier):
    def send(self, to: str, subject: str, body: str) -> bool:
        # Mock implementation - in production integrate with WhatsApp Business API
        notification_id = str(uuid.uuid4())[:8]
        logger.info(f"💬 [WHATSAPP-{notification_id}] To: {to}, Subject: {subject}, Body: {body[:100]}...")
        
        # Simulate successful send
        print(f"🚀 WHATSAPP MESSAGE SENT: To: {to} | Subject: {subject}")
        return True

    def get_name(self) -> str:
        return "whatsapp"

class LogNotifier(Notifier):
    def send(self, to: str, subject: str, body: str) -> bool:
        # Simple log implementation
        notification_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        log_entry = f"""
📋 NOTIFICATION LOGGED [{timestamp}]
├── ID: {notification_id}
├── To: {to}
├── Subject: {subject}
└── Body: {body}
        """
        
        logger.info(log_entry)
        print(log_entry)
        return True

    def get_name(self) -> str:
        return "log"

class NotificationService:
    def __init__(self):
        self.notifiers = {
            "email": EmailNotifier(),
            "whatsapp": WhatsAppNotifier(),
            "log": LogNotifier()
        }
    
    def send_notification(self, to: str, subject: str, body: str, method: str = "log") -> dict:
        notifier = self.notifiers.get(method, self.notifiers["log"])
        
        try:
            success = notifier.send(to, subject, body)
            return {
                "id": str(uuid.uuid4()),
                "status": "sent" if success else "failed",
                "method": notifier.get_name(),
                "to": to,
                "subject": subject,
                "sent_at": datetime.now().isoformat(),
                "success": success
            }
        except Exception as e:
            logger.error(f"Notification failed: {e}")
            return {
                "id": str(uuid.uuid4()),
                "status": "failed",
                "method": notifier.get_name(),
                "to": to,
                "subject": subject,
                "sent_at": datetime.now().isoformat(),
                "error": str(e),
                "success": False
            }

# Global service instance
notification_service = NotificationService()