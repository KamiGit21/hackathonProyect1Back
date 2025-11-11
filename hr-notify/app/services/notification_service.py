from typing import List, Dict, Any
from app.transports.notifiers import notification_service
from app.repos.users_repo import get_user_by_email
from app.repos.notifications_repo import save_notification
import logging

logger = logging.getLogger("hr-notify")

class HRNotificationService:
    
    @staticmethod
    async def notify_employee(employee_email: str, subject: str, body: str, method: str = "email") -> Dict[str, Any]:
        """
        Send notification to employee with validation
        """
        print(f"📨 Notifying employee: {employee_email}")
        
        # Verify employee exists in system
        employee = get_user_by_email(employee_email)
        if not employee:
            logger.warning(f"Employee not found with email: {employee_email}")
            return {
                "error": "Employee not found", 
                "sent": False,
                "employee_email": employee_email
            }
        
        # Send notification
        result = notification_service.send_notification(
            to=employee_email,
            subject=subject,
            body=body,
            method=method
        )
        
        # Save to database
        save_notification({
            **result,
            "employee_email": employee_email,
            "notification_type": "employee"
        })
        
        print(f"✅ Employee notification sent: {result['id']}")
        return result
    
    @staticmethod
    async def notify_hr_team(subject: str, body: str, method: str = "email") -> List[Dict[str, Any]]:
        """
        Send notification to entire HR team
        """
        from app.config import settings
        
        print(f"👥 Notifying HR team: {len(settings.hr_notification_emails)} recipients")
        
        results = []
        for hr_email in settings.hr_notification_emails:
            result = notification_service.send_notification(
                to=hr_email,
                subject=subject,
                body=body,
                method=method
            )
            
            # Save to database
            save_notification({
                **result,
                "hr_email": hr_email,
                "notification_type": "hr_team"
            })
            
            results.append(result)
        
        print(f"✅ HR team notifications sent: {len(results)} successful")
        return results

    @staticmethod
    async def broadcast_notification(to_list: List[str], subject: str, body: str, method: str = "email") -> Dict[str, Any]:
        """
        Send notification to multiple recipients
        """
        print(f"📢 Broadcasting to {len(to_list)} recipients")
        
        results = []
        for recipient in to_list:
            result = notification_service.send_notification(
                to=recipient,
                subject=subject,
                body=body,
                method=method
            )
            results.append(result)
        
        success_count = sum(1 for r in results if r.get("success", False))
        
        return {
            "total_recipients": len(to_list),
            "successful_sends": success_count,
            "failed_sends": len(to_list) - success_count,
            "results": results
        }

# Global service instance
hr_notification_service = HRNotificationService()