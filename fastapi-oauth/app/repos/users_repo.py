# app/repos/users_repo.py
import time
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from app.firebase import get_firestore
from app.config import settings
from app.schemas import UserOut, UserDoc

def _users_col():
    fs = get_firestore()
    return fs.collection(settings.firestore_users_collection)

def _epoch_to_dt(ts: Optional[int]) -> Optional[datetime]:
    return datetime.fromtimestamp(ts, tz=timezone.utc) if ts else None

def _to_user_out(data: Dict[str, Any]) -> UserOut:
    return UserOut(
        uid=data["uid"],
        first_name=data.get("given_name"),
        last_name=data.get("family_name"),
        email=data.get("email"),
        username=data["username"],
        active=bool(data.get("active", True)),
        last_update=_epoch_to_dt(data.get("updated_at")),
    )

def get_user_by_uid(uid: str) -> Optional[UserOut]:
    doc = _users_col().document(uid).get()
    if not doc.exists:
        return None
    return _to_user_out(doc.to_dict())

def get_user_by_email(email: str) -> Optional[UserOut]:
    q = _users_col().where("email", "==", email).limit(1).stream()
    for snap in q:
        return _to_user_out(snap.to_dict())
    return None

def create_or_update_from_google(profile: Dict[str, Any], uid: str) -> UserOut:
    """
    Upsert de usuario proveniente de Google OAuth.
    profile: { email, name, given_name, family_name, picture, sub, email_verified }
    uid: usualmente el sub de Google (o tu convención)
    """
    now = int(time.time())
    email = profile["email"]
    base_username = (profile.get("given_name") or email.split("@")[0]).strip().lower()[:16] or "user"

    data: Dict[str, Any] = {
        "uid": uid,
        "email": email,
        "name": profile.get("name"),
        "given_name": profile.get("given_name"),
        "family_name": profile.get("family_name"),
        "username": base_username,
        "active": True,
        "picture": profile.get("picture"),
        "provider": "google",
        "provider_sub": profile.get("sub"),
        "updated_at": now,
        "last_login": now,
    }

    doc_ref = _users_col().document(uid)
    snap = doc_ref.get()
    if not snap.exists:
        data["created_at"] = now
        doc_ref.set(data)
    else:
        doc_ref.set(data, merge=True)

    return _to_user_out(data)

def update_last_login(uid: str) -> None:
    _users_col().document(uid).set({"last_login": int(time.time())}, merge=True)
