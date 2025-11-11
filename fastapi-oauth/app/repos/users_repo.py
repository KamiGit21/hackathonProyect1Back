# app/repos/users_repo.py
import time
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from app.firebase import get_firestore
from app.config import settings
from app.schemas import UserOut

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

def _is_first_user() -> bool:
    # Si no hay documentos aún, es el primero
    it = _users_col().limit(1).stream()
    return next(it, None) is None

def get_user_by_uid(uid: str) -> Optional[UserOut]:
    doc = _users_col().document(uid).get()
    if not doc.exists:
        return None
    return _to_user_out(doc.to_dict())

def get_user_doc(uid: str) -> Optional[Dict[str, Any]]:
    snap = _users_col().document(uid).get()
    return snap.to_dict() if snap.exists else None

def create_or_update_from_google(profile: Dict[str, Any], uid: str) -> UserOut:
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
        # ⛳ primer usuario del sistema => HR_ADMIN
        roles = ["EMPLOYEE"]
        if _is_first_user():
            roles = ["HR_ADMIN"]  # que admin arranque
        data["roles"] = roles
        data["created_at"] = now
        doc_ref.set(data)
    else:
        # no pisar roles existentes
        existing = snap.to_dict() or {}
        data["roles"] = existing.get("roles", ["EMPLOYEE"])
        doc_ref.set(data, merge=True)

    return _to_user_out({**snap.to_dict(), **data} if snap.exists else data)

def set_roles(uid: str, roles: list[str]) -> Dict[str, Any]:
    _users_col().document(uid).set({"roles": roles, "updated_at": int(time.time())}, merge=True)
    return get_user_doc(uid) or {}
