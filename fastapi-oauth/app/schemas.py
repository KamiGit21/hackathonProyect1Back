# app/schemas.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from enum import Enum
from typing import Optional


# === Documento de usuario (Firestore) ===
class UserDoc(BaseModel):
    uid: str
    email: EmailStr
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    username: str = Field(..., max_length=16)
    active: bool = True
    picture: Optional[str] = None
    provider: str = "google"
    provider_sub: Optional[str] = None
    created_at: Optional[int] = None  # epoch
    updated_at: Optional[int] = None  # epoch
    last_login: Optional[int] = None  # epoch

# === Salidas compatibles con tu API anterior ===
class UserOut(BaseModel):
    uid: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    username: str
    active: bool
    last_update: Optional[datetime] = None

# Alias de compatibilidad para no romper clientes
StaffOut = UserOut

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MeOut(BaseModel):
    user: StaffOut
    token: TokenOut

# === Entradas administrativas opcionales ===
class StaffCreateFromGoogle(BaseModel):
    email: EmailStr
    given_name: str
    family_name: str
    username: str = Field(..., max_length=16)

### PARA PAYROLL - LEAVE REQUESTS ###
class LeaveType(str, Enum):
    vacation = "vacation"
    sick = "sick"
    other = "other"

class LeaveStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class LeaveRequestIn(BaseModel):
    # employee_uid: uid del empleado en Firestore (puede ser email o uid)
    employee_uid: str
    type: LeaveType
    start_date: date
    end_date: date
    reason: Optional[str] = None

class LeaveRequestDoc(BaseModel):
    id: str  # document id en Firestore
    employee_uid: str
    type: LeaveType
    start_date: date
    end_date: date
    reason: Optional[str] = None
    status: LeaveStatus = LeaveStatus.pending
    requested_at: Optional[int] = None  # epoch
    approved_at: Optional[int] = None   # epoch
    approver_uid: Optional[str] = None
    approver_role: Optional[str] = None
    # campos auxiliares
    days: Optional[int] = None

class LeaveRequestOut(BaseModel):
    id: str
    employee_uid: str
    type: LeaveType
    start_date: date
    end_date: date
    reason: Optional[str] = None
    status: LeaveStatus
    requested_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    approver_uid: Optional[str] = None
    approver_role: Optional[str] = None
    days: Optional[int] = None

class LeaveBalanceOut(BaseModel):
    employee_uid: str
    year: int
    allowance: int
    used: int
    balance: int