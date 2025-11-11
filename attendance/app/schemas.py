from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, validator

class PunchRequest(BaseModel):
    """Request para registrar entrada/salida"""
    emp_id: str = Field(..., description="Employee ID")
    punch_type: Literal["IN", "OUT"] = Field(..., description="Tipo de marca: IN o OUT")
    timestamp: Optional[datetime] = Field(default=None, description="Timestamp opcional, usa la hora actual si no se proporciona")
    
    @validator('timestamp', pre=True, always=True)
    def set_timestamp(cls, v):
        return v or datetime.utcnow()
    
    class Config:
        json_schema_extra = {
            "example": {
                "emp_id": "emp_123",
                "punch_type": "IN",
                "timestamp": "2025-11-10T08:00:00Z"
            }
        }

class PunchResponse(BaseModel):
    """Response de marca registrada"""
    punch_id: str
    emp_id: str
    punch_type: str
    timestamp: datetime
    message: str = "Punch registered successfully"
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TimesheetRequest(BaseModel):
    """Query params para obtener timesheet"""
    emp_id: str = Field(..., description="Employee ID")
    from_date: str = Field(..., alias="from", description="Fecha inicio YYYY-MM-DD")
    to_date: str = Field(..., alias="to", description="Fecha fin YYYY-MM-DD")
    
    class Config:
        populate_by_name = True

class DayTimesheetResponse(BaseModel):
    """Timesheet de un día específico"""
    date: str
    emp_id: str
    punches: list[dict]
    total_hours: float
    first_in: Optional[str] = None
    last_out: Optional[str] = None
    status: str

class TimesheetResponse(BaseModel):
    """Response completo de timesheet"""
    emp_id: str
    from_date: str
    to_date: str
    days: list[DayTimesheetResponse]
    total_hours: float
    total_days: int