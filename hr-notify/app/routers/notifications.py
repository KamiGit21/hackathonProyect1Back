from fastapi import APIRouter, HTTPException, BackgroundTasks, Header, Query
from typing import List, Optional

from app.schemas.notifications import NotifyRequest, NotificationResponse
from app.transports.notifiers import notification_service
from app.repos.notifications_repo import save_notification, get_notifications_by_user
from app.deps import verify_api_key

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.post("/notify", response_model=NotificationResponse)
async def send_notification(
    request: NotifyRequest,
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(..., alias="X-API-Key")
):
    """
    Send a notification via specified method (email/whatsapp/log)
    """
    # Verify API key
    verify_api_key(x_api_key)
    
    # Send notification
    result = notification_service.send_notification(
        to=request.to,
        subject=request.subject,
        body=request.body,
        method=request.method
    )
    
    # Save to database
    save_notification(result)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail="Failed to send notification")
    
    return NotificationResponse(**result)

@router.get("/history")
async def get_notification_history(
    user_email: str = Query(..., description="User email to filter notifications"),
    limit: int = Query(50, description="Number of notifications to return"),
    x_api_key: str = Header(..., alias="X-API-Key")
):
    """
    Get notification history for a user
    """
    verify_api_key(x_api_key)
    
    notifications = get_notifications_by_user(user_email, limit)
    return {
        "user_email": user_email,
        "count": len(notifications),
        "notifications": notifications
    }

@router.get("/test")
async def test_notification(
    x_api_key: str = Header(..., alias="X-API-Key")
):
    """
    Test endpoint to verify the service is working
    """
    verify_api_key(x_api_key)
    
    test_result = notification_service.send_notification(
        to="test@arca.ltd",
        subject="Test Notification",
        body="This is a test notification from HR-NOTIFY service",
        method="log"
    )
    
    return {
        "service": "HR-NOTIFY",
        "status": "operational", 
        "test_notification": test_result
    }