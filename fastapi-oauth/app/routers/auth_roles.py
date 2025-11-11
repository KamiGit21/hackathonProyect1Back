# app/routers/auth_roles.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List
from app.authz import require_roles, Role
from app.deps import current_user
from app.repos.users_repo import set_roles, get_user_doc

router = APIRouter(prefix="/auth/roles", tags=["roles"])

class SetRolesIn(BaseModel):
    uid: str
    roles: List[Role]

@router.post("/set", dependencies=[Depends(require_roles(Role.HR_ADMIN))])
def set_user_roles(payload: SetRolesIn, _=Depends(current_user)):
    doc = get_user_doc(payload.uid)
    if not doc:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    updated = set_roles(payload.uid, [r.value for r in payload.roles])
    return {"ok": True, "user": {"uid": payload.uid, "roles": updated.get("roles", [])}}
