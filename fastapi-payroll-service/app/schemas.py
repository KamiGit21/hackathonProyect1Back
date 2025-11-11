from pydantic import BaseModel
from enum import Enum
from datetime import date, datetime
from typing import Optional, List

class PayrollSlip(BaseModel):
    employee_uid: str
    period: str  # YYYY-MM
    gross: float
    deductions: float
    net: float
    details: Optional[List[dict]] = None

class PayrollPreviewOut(BaseModel):
    slips: List[PayrollSlip]

# input for employee registration
class EmployeeDoc(BaseModel):
    uid: str
    full_name: Optional[str] = None
    monthly_salary: float  # currency units