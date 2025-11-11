from typing import List, Dict, Any, Optional
from datetime import datetime
from app.firebase import get_firestore
from app.config import settings

def _notifications_col():
    fs = get_firestore()
    return fs.collection(settings.firestore_notifications_collection)

def save_notification(notification_data: Dict[str, Any]) -> str:
    """
    Save notification to Firestore
    """
    col = _notifications_col()
    doc_ref = col.document()
    notification_data["id"] = doc_ref.id
    notification_data["created_at"] = datetime.now().isoformat()
    
    doc_ref.set(notification_data)
    return doc_ref.id

def get_notifications_by_user(user_email: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get notifications for a specific user
    """
    col = _notifications_col()
    query = col.where("to", "==", user_email).order_by("created_at", direction="DESCENDING").limit(limit)
    
    notifications = []
    for doc in query.stream():
        notification_data = doc.to_dict()
        notification_data["firestore_id"] = doc.id
        notifications.append(notification_data)
    
    return notifications

def get_notifications_by_status(status: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get notifications by status (sent, failed, pending)
    """
    col = _notifications_col()
    query = col.where("status", "==", status).order_by("created_at", direction="DESCENDING").limit(limit)
    
    notifications = []
    for doc in query.stream():
        notification_data = doc.to_dict()
        notification_data["firestore_id"] = doc.id
        notifications.append(notification_data)
    
    return notifications