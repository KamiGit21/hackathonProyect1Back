from datetime import datetime, date
import calendar
from typing import List, Dict, Any
from app.repos.payroll_repo import get_employee, list_employees, list_events_for_employee_period
from app.schemas import PayrollSlip

def _days_in_period(period_ym: str) -> int:
    year, month = [int(x) for x in period_ym.split("-")]
    return calendar.monthrange(year, month)[1]

def _parse_iso(d):
    if not d:
        return None
    if isinstance(d, date):
        return d
    return date.fromisoformat(d)

def _count_unjustified_absences(events: List[Dict[str, Any]], period_ym: str) -> int:
    year, month = [int(x) for x in period_ym.split("-")]
    period_start = date(year, month, 1)
    period_end = date(year, month, _days_in_period(period_ym))
    total = 0
    for ev in events:
        etype = ev.get("event") or ev.get("type")
        if etype == "TimeAbsent" or ev.get("event") == "TimeAbsent":
            # expect ev has date or start_date/end_date and 'justified' boolean
            justified = ev.get("justified", False)
            if justified:
                continue
            # get date(s)
            if ev.get("date"):
                d = _parse_iso(ev["date"])
                if period_start <= d <= period_end:
                    total += 1
            else:
                s = ev.get("start_date")
                e = ev.get("end_date", s)
                if s:
                    s = _parse_iso(s); e = _parse_iso(e)
                    # count overlapping days in month
                    eff_s = max(s, period_start)
                    eff_e = min(e, period_end)
                    if eff_e >= eff_s:
                        total += (eff_e - eff_s).days + 1
    return total

def _count_leave_days(events: List[Dict[str, Any]], period_ym: str) -> int:
    # approved leaves are paid -> not counted as unpaid
    return 0

def preview_payroll(period_ym: str) -> List[PayrollSlip]:
    slips = []
    employees = list_employees()
    days_in_month = _days_in_period(period_ym)
    for emp in employees:
        monthly = float(emp.get("monthly_salary", 0.0))
        events = list_events_for_employee_period(emp["uid"], period_ym)
        unpaid_days = _count_unjustified_absences(events, period_ym)
        daily = monthly / days_in_month if days_in_month else 0
        deduction = unpaid_days * daily
        net = max(monthly - deduction, 0.0)
        slip = PayrollSlip(
            employee_uid=emp["uid"],
            period=period_ym,
            gross=round(monthly,2),
            deductions=round(deduction,2),
            net=round(net,2),
            details=[{"unpaid_days": unpaid_days, "days_in_month": days_in_month}]
        )
        slips.append(slip)
    return slips

def get_slip_for_employee(emp_uid: str, period_ym: str) -> PayrollSlip | None:
    employees = [e for e in list_employees() if e["uid"] == emp_uid]
    if not employees:
        return None
    emp = employees[0]
    days_in_month = _days_in_period(period_ym)
    monthly = float(emp.get("monthly_salary", 0.0))
    events = list_events_for_employee_period(emp_uid, period_ym)
    unpaid_days = _count_unjustified_absences(events, period_ym)
    daily = monthly / days_in_month if days_in_month else 0
    deduction = unpaid_days * daily
    net = max(monthly - deduction, 0.0)
    return PayrollSlip(
        employee_uid=emp_uid,
        period=period_ym,
        gross=round(monthly,2),
        deductions=round(deduction,2),
        net=round(net,2),
        details=[{"unpaid_days": unpaid_days, "days_in_month": days_in_month}]
    )