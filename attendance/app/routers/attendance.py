from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional

from app.schemas import (
    PunchRequest, 
    PunchResponse, 
    TimesheetRequest,
    TimesheetResponse
)
from app.services.attendance_service import AttendanceService

router = APIRouter(
    prefix="/attendance",
    tags=["attendance"]
)

# Dependency para el servicio
def get_attendance_service() -> AttendanceService:
    return AttendanceService()

@router.post("/punch", response_model=PunchResponse, status_code=201)
async def register_punch(
    punch_req: PunchRequest,
    service: AttendanceService = Depends(get_attendance_service)
):
    """
    Registra una marca de entrada (IN) o salida (OUT).
    
    - **emp_id**: ID del empleado
    - **punch_type**: IN o OUT
    - **timestamp**: Opcional, usa la hora actual si no se proporciona
    """
    try:
        punch = await service.register_punch(punch_req)
        
        return PunchResponse(
            punch_id=punch.punch_id,
            emp_id=punch.emp_id,
            punch_type=punch.punch_type,
            timestamp=punch.timestamp,
            message="Punch registered successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/timesheet", response_model=TimesheetResponse)
async def get_timesheet(
    empId: str = Query(..., description="Employee ID"),
    from_date: str = Query(..., alias="from", description="Start date (YYYY-MM-DD)"),
    to_date: str = Query(..., alias="to", description="End date (YYYY-MM-DD)"),
    service: AttendanceService = Depends(get_attendance_service)
):
    """
    Obtiene el registro de horas de un empleado en un rango de fechas.
    
    - **empId**: ID del empleado
    - **from**: Fecha de inicio (YYYY-MM-DD)
    - **to**: Fecha de fin (YYYY-MM-DD)
    """
    try:
        timesheet_req = TimesheetRequest(
            emp_id=empId,
            from_date=from_date,
            to_date=to_date
        )
        
        result = await service.get_timesheet(timesheet_req)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/close-day/{emp_id}/{date}")
async def close_day(
    emp_id: str,
    date: str,
    service: AttendanceService = Depends(get_attendance_service)
):
    """
    Cierra el día para un empleado y emite evento DailyTimeClosed.
    
    - **emp_id**: ID del empleado
    - **date**: Fecha a cerrar (YYYY-MM-DD)
    """
    try:
        timesheet = await service.close_day(emp_id, date)
        
        return {
            "message": "Day closed successfully",
            "emp_id": emp_id,
            "date": date,
            "total_hours": timesheet.total_hours,
            "status": timesheet.status
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "attendance"
    }