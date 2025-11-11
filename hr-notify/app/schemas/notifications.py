from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from datetime import datetime

class NotifyRequest(BaseModel):
    to: str  # email or phone number
    subject: str
    body: str
    method: Literal["email", "whatsapp", "log"] = "log"

class NotificationResponse(BaseModel):
    id: str
    status: str
    method: str
    to: str
    subject: str
    sent_at: datetime

class LeaveApprovedEvent(BaseModel):
    employee_email: EmailStr
    employee_name: str
    leave_request_id: str
    start_date: str
    end_date: str
    approved_by: str
    approved_at: str

class PayrollPreviewEvent(BaseModel):
    payroll_period: str
    preview_id: str
    generated_by: str
    generated_at: str
    total_employees: int
    preview_url: Optional[str] = None