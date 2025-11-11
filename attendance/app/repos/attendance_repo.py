from datetime import datetime, timedelta
from typing import List, Optional
from google.cloud.firestore_v1 import FieldFilter
import uuid

from app.firebase import get_db, PUNCHES_COLLECTION, TIMESHEETS_COLLECTION, EVENTS_COLLECTION
from app.models import Punch, DailyTimesheet, DailyTimeClosedEvent

class AttendanceRepository:
    def __init__(self):
        self.db = get_db()
        self.punches_ref = self.db.collection(PUNCHES_COLLECTION)
        self.timesheets_ref = self.db.collection(TIMESHEETS_COLLECTION)
        self.events_ref = self.db.collection(EVENTS_COLLECTION)
    
    async def create_punch(self, punch: Punch) -> Punch:
        """Crea una nueva marca de entrada/salida"""
        punch_dict = punch.model_dump()
        punch_dict['timestamp'] = punch.timestamp.isoformat()
        punch_dict['created_at'] = punch.created_at.isoformat()
        
        doc_ref = self.punches_ref.document(punch.punch_id)
        doc_ref.set(punch_dict)
        
        return punch
    
    async def get_punches_by_employee(
        self, 
        emp_id: str, 
        from_date: datetime, 
        to_date: datetime
    ) -> List[dict]:
        """Obtiene todas las marcas de un empleado en un rango de fechas"""
        query = (
            self.punches_ref
            .where(filter=FieldFilter("emp_id", "==", emp_id))
            .where(filter=FieldFilter("timestamp", ">=", from_date.isoformat()))
            .where(filter=FieldFilter("timestamp", "<=", to_date.isoformat()))
            .order_by("timestamp")
        )
        
        docs = query.stream()
        punches = []
        
        for doc in docs:
            punch_data = doc.to_dict()
            punches.append(punch_data)
        
        return punches
    
    async def get_punches_by_day(self, emp_id: str, date: str) -> List[dict]:
        """Obtiene todas las marcas de un empleado en un día específico"""
        start = datetime.fromisoformat(f"{date}T00:00:00")
        end = datetime.fromisoformat(f"{date}T23:59:59")
        
        query = (
            self.punches_ref
            .where(filter=FieldFilter("emp_id", "==", emp_id))
            .where(filter=FieldFilter("timestamp", ">=", start.isoformat()))
            .where(filter=FieldFilter("timestamp", "<=", end.isoformat()))
            .order_by("timestamp")
        )
        
        docs = query.stream()
        punches = []
        
        for doc in docs:
            punch_data = doc.to_dict()
            punches.append(punch_data)
        
        return punches
    
    async def save_daily_timesheet(self, timesheet: DailyTimesheet) -> None:
        """Guarda el resumen diario de horas"""
        timesheet_id = f"{timesheet.emp_id}_{timesheet.date}"
        timesheet_dict = timesheet.model_dump()
        
        if timesheet_dict.get('first_in'):
            timesheet_dict['first_in'] = timesheet.first_in.isoformat()
        if timesheet_dict.get('last_out'):
            timesheet_dict['last_out'] = timesheet.last_out.isoformat()
        
        doc_ref = self.timesheets_ref.document(timesheet_id)
        doc_ref.set(timesheet_dict)
    
    async def get_daily_timesheet(self, emp_id: str, date: str) -> Optional[dict]:
        """Obtiene el timesheet de un día específico"""
        timesheet_id = f"{emp_id}_{date}"
        doc_ref = self.timesheets_ref.document(timesheet_id)
        doc = doc_ref.get()
        
        if doc.exists:
            return doc.to_dict()
        return None
    
    async def publish_event(self, event: DailyTimeClosedEvent) -> None:
        """Publica un evento de cierre de día"""
        event_id = str(uuid.uuid4())
        event_dict = event.model_dump()
        event_dict['timestamp'] = event.timestamp.isoformat()
        
        doc_ref = self.events_ref.document(event_id)
        doc_ref.set(event_dict)