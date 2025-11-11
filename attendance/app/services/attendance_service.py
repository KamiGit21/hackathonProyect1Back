from datetime import datetime, timedelta
from typing import List
import uuid

from app.repos.attendance_repo import AttendanceRepository
from app.models import Punch, DailyTimesheet, DailyTimeClosedEvent
from app.schemas import PunchRequest, TimesheetRequest

class AttendanceService:
    def __init__(self):
        self.repo = AttendanceRepository()
    
    async def register_punch(self, punch_req: PunchRequest) -> Punch:
        """Registra una marca de entrada o salida"""
        punch = Punch(
            punch_id=str(uuid.uuid4()),
            emp_id=punch_req.emp_id,
            punch_type=punch_req.punch_type,
            timestamp=punch_req.timestamp
        )
        
        await self.repo.create_punch(punch)
        
        # Actualizar el timesheet del día
        date_str = punch.timestamp.strftime("%Y-%m-%d")
        await self._update_daily_timesheet(punch_req.emp_id, date_str)
        
        return punch
    
    async def get_timesheet(self, timesheet_req: TimesheetRequest) -> dict:
        """Obtiene el timesheet de un empleado en un rango de fechas"""
        from_date = datetime.fromisoformat(timesheet_req.from_date)
        to_date = datetime.fromisoformat(timesheet_req.to_date)
        
        # Obtener todas las marcas del período
        punches = await self.repo.get_punches_by_employee(
            timesheet_req.emp_id,
            from_date,
            to_date
        )
        
        # Agrupar por día y calcular horas
        days_data = await self._group_punches_by_day(punches, from_date, to_date)
        
        total_hours = sum(day['total_hours'] for day in days_data)
        
        return {
            "emp_id": timesheet_req.emp_id,
            "from_date": timesheet_req.from_date,
            "to_date": timesheet_req.to_date,
            "days": days_data,
            "total_hours": round(total_hours, 2),
            "total_days": len(days_data)
        }
    
    async def close_day(self, emp_id: str, date: str) -> DailyTimesheet:
        """Cierra el día y emite evento para nómina"""
        timesheet = await self.repo.get_daily_timesheet(emp_id, date)
        
        if not timesheet:
            await self._update_daily_timesheet(emp_id, date)
            timesheet = await self.repo.get_daily_timesheet(emp_id, date)
        
        if timesheet['status'] == 'closed':
            raise ValueError(f"Day {date} already closed for employee {emp_id}")
        
        # Actualizar estado a cerrado
        timesheet['status'] = 'closed'
        daily_timesheet = DailyTimesheet(**timesheet)
        await self.repo.save_daily_timesheet(daily_timesheet)
        
        # Emitir evento
        event = DailyTimeClosedEvent(
            emp_id=emp_id,
            date=date,
            total_hours=timesheet['total_hours']
        )
        await self.repo.publish_event(event)
        
        return daily_timesheet
    
    async def _update_daily_timesheet(self, emp_id: str, date: str) -> None:
        """Actualiza el resumen diario de horas"""
        punches = await self.repo.get_punches_by_day(emp_id, date)
        
        if not punches:
            return
        
        total_hours = self._calculate_hours(punches)
        
        first_in = None
        last_out = None
        
        for punch in punches:
            timestamp = datetime.fromisoformat(punch['timestamp'])
            if punch['punch_type'] == 'IN' and (not first_in or timestamp < first_in):
                first_in = timestamp
            if punch['punch_type'] == 'OUT' and (not last_out or timestamp > last_out):
                last_out = timestamp
        
        # Obtener estado actual si existe
        existing = await self.repo.get_daily_timesheet(emp_id, date)
        status = existing['status'] if existing else 'open'
        
        timesheet = DailyTimesheet(
            date=date,
            emp_id=emp_id,
            punches=[{
                'punch_type': p['punch_type'],
                'timestamp': p['timestamp']
            } for p in punches],
            total_hours=total_hours,
            first_in=first_in,
            last_out=last_out,
            status=status
        )
        
        await self.repo.save_daily_timesheet(timesheet)
    
    def _calculate_hours(self, punches: List[dict]) -> float:
        """Calcula las horas trabajadas basándose en las marcas IN/OUT"""
        total_seconds = 0
        last_in = None
        
        for punch in punches:
            timestamp = datetime.fromisoformat(punch['timestamp'])
            
            if punch['punch_type'] == 'IN':
                last_in = timestamp
            elif punch['punch_type'] == 'OUT' and last_in:
                duration = (timestamp - last_in).total_seconds()
                total_seconds += duration
                last_in = None
        
        return round(total_seconds / 3600, 2)  # Convertir a horas
    
    async def _group_punches_by_day(
        self, 
        punches: List[dict], 
        from_date: datetime,
        to_date: datetime
    ) -> List[dict]:
        """Agrupa las marcas por día y calcula horas"""
        days_dict = {}
        
        for punch in punches:
            timestamp = datetime.fromisoformat(punch['timestamp'])
            date_key = timestamp.strftime("%Y-%m-%d")
            
            if date_key not in days_dict:
                days_dict[date_key] = []
            
            days_dict[date_key].append(punch)
        
        days_data = []
        
        for date_key, day_punches in sorted(days_dict.items()):
            total_hours = self._calculate_hours(day_punches)
            
            first_in = None
            last_out = None
            
            for punch in day_punches:
                timestamp = datetime.fromisoformat(punch['timestamp'])
                if punch['punch_type'] == 'IN' and (not first_in or timestamp < first_in):
                    first_in = timestamp
                if punch['punch_type'] == 'OUT' and (not last_out or timestamp > last_out):
                    last_out = timestamp
            
            days_data.append({
                "date": date_key,
                "emp_id": day_punches[0]['emp_id'],
                "punches": [{
                    'punch_type': p['punch_type'],
                    'timestamp': p['timestamp']
                } for p in day_punches],
                "total_hours": total_hours,
                "first_in": first_in.isoformat() if first_in else None,
                "last_out": last_out.isoformat() if last_out else None,
                "status": "open"
            })
        
        return days_data