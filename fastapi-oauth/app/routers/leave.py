# filepath: /workspaces/hackathonProyect1Back/fastapi-oauth/app/routers/leave.py
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import List, Optional
from datetime import date
from app.schemas import (
    LeaveRequestIn,
    LeaveRequestOut,
    LeaveBalanceOut,
)
from app.repos.leave_repo import (
    create_request,
    get_request,
    list_requests,
    approve_request,
    get_balance,
)
from app.deps import current_user
from app.config import settings

router = APIRouter(prefix="/leave", tags=["leave"])

@router.post("/requests", response_model=LeaveRequestOut, status_code=201)
def api_create_request(payload: LeaveRequestIn):
    try:
        return create_request(payload.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/requests", response_model=List[LeaveRequestOut])
def api_list_requests(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0), employee_uid: Optional[str] = None, status: Optional[str] = None):
    try:
        return list_requests(limit=limit, offset=offset, employee_uid=employee_uid, status=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/requests/{request_id}", response_model=LeaveRequestOut)
def api_get_request(request_id: str = Path(...)):
    r = get_request(request_id)
    if not r:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return r

def _has_approval_role(user) -> Optional[str]:
    """
    Devuelve 'HR' o 'MANAGER' si el usuario está autorizado, o None.
    """
    if not user or not getattr(user, "email", None):
        return None
    email = user.email.lower()
    if email in [e.lower() for e in settings.hr_emails]:
        return "HR"
    if email in [e.lower() for e in settings.manager_emails]:
        return "MANAGER"
    return None

@router.post("/requests/{request_id}/approve", response_model=LeaveRequestOut)
def api_approve_request(request_id: str, user = Depends(current_user)):
    role = _has_approval_role(user)
    if not role:
        raise HTTPException(status_code=403, detail="No autorizado para aprobar (HR/Manager)")
    updated = approve_request(request_id=request_id, approver_uid=user.uid, approver_role=role)
    if not updated:
        raise HTTPException(status_code=404, detail="Leave request not found")
    # Aquí podrías publicar un evento LeaveApproved para otros microservicios (nómina/calendar).
    return updated

@router.get("/balance", response_model=LeaveBalanceOut)
def api_balance(employee_uid: str = Query(...), year: int = Query(None)):
    if year is None:
        year = date.today().year
    bal = get_balance(employee_uid, year)
    return LeaveBalanceOut(**bal)
