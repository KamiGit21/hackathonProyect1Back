from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field

class PunchType:
    IN = "IN"
    OUT = "OUT"

class Punch(BaseModel):
    """Modelo de marca de entrada/salida"""
    punch_id: str
    emp_id: str
    punch_type: Literal["IN", "OUT"]
    timestamp: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class DailyTimesheet(BaseModel):
    """Resumen de horas trabajadas en un día"""
    date: str  # YYYY-MM-DD
    emp_id: str
    punches: list[dict]  # Lista de {punch_type, timestamp}
    total_hours: float
    first_in: Optional[datetime] = None
    last_out: Optional[datetime] = None
    status: str = "open"  # open, closed
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class DailyTimeClosedEvent(BaseModel):
    """Evento emitido cuando se cierra el día"""
    event_type: str = "DailyTimeClosed"
    emp_id: str
    date: str
    total_hours: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }