from fastapi import APIRouter, Query, HTTPException, Response
from typing import List
from app.services.payroll_service import preview_payroll, get_slip_for_employee
from app.repos.payroll_repo import list_employees
import csv
import io

router = APIRouter()

@router.post("/run-preview", response_model=dict)
def run_preview(period: str = Query(..., regex=r"^\d{4}-\d{2}$")):
    slips = preview_payroll(period)
    return {"slips": [s.model_dump() for s in slips]}

@router.get("/slip/{empId}", response_model=dict)
def get_slip(empId: str, period: str = Query(..., regex=r"^\d{4}-\d{2}$")):
    slip = get_slip_for_employee(empId, period)
    if not slip:
        raise HTTPException(status_code=404, detail="employee or slip not found")
    return slip.model_dump()

@router.get("/export")
def export_csv(period: str = Query(..., regex=r"^\d{4}-\d{2}$")):
    slips = preview_payroll(period)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["employee_uid","period","gross","deductions","net","details"])
    for s in slips:
        writer.writerow([s.employee_uid, s.period, s.gross, s.deductions, s.net, s.details])
    resp = Response(content=buf.getvalue(), media_type="text/csv")
    resp.headers["Content-Disposition"] = f'attachment; filename="payroll_{period}.csv"'
    return resp