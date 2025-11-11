# Reutiliza el mismo repositorio de usuarios del proyecto principal
import time
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from app.firebase import get_firestore
from app.config import settings

def _users_col():
    fs = get_firestore()
    return fs.collection(settings.firestore_users_collection)

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    q = _users_col().where("email", "==", email).limit(1).stream()
    for snap in q:
        return snap.to_dict()
    return None