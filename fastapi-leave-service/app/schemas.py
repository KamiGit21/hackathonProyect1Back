# filepath: [schemas.py](http://_vscodecontentref_/16)
from pydantic import BaseModel
from enum import Enum
from datetime import date, datetime
from typing import Optional

class LeaveType(str, Enum):
    vacation = "vacation"
    sick = "sick"
    other = "other"

class LeaveStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class LeaveRequestIn(BaseModel):
    employee_uid: str
    type: LeaveType
    start_date: date
    end_date: date
    reason: Optional[str] = None

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