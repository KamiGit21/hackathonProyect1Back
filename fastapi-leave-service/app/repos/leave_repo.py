# filepath: [leave_repo.py](http://_vscodecontentref_/18)
import time
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from app.firebase import get_firestore
from app.config import settings
from app.schemas import LeaveRequestOut, LeaveStatus, LeaveType
from app.repos._util import _epoch_to_dt  # helper we'll add

# Fallback in-memory (like earlier) for dev if Firestore not available
_MEM_DB: Dict[str, Dict[str, Dict[str, Any]]] = {}

def _mem_collection(name: str):
    if name not in _MEM_DB:
        _MEM_DB[name] = {}
    coll = _MEM_DB[name]

    class _Col:
        def document(self, doc_id: str):
            class DocRef:
                def __init__(self, coll, doc_id):
                    self.coll = coll
                    self.id = str(doc_id)
                def set(self, data, merge=False):
                    if merge and self.id in self.coll:
                        cur = self.coll[self.id].copy(); cur.update(data); self.coll[self.id] = cur
                    else:
                        self.coll[self.id] = dict(data)
                def get(self):
                    data = self.coll.get(self.id)
                    class Snap:
                        def __init__(self, d):
                            self._d = d
                            self.exists = bool(d)
                        def to_dict(self):
                            return dict(self._d) if self._d else {}
                    return Snap(data)
            return DocRef(coll, doc_id)
        def where(self, field, op, value):
            class Q:
                def __init__(self, coll, field, value):
                    self._coll = coll; self._field = field; self._val = value
                def limit(self, n):
                    self._limit = n; return self
                def stream(self):
                    items = [d for d in self._coll.values() if d.get(self._field) == self._val]
                    for d in items:
                        class Snap:
                            def __init__(self, d): self._d=d; self.exists=True
                            def to_dict(self): return dict(self._d)
                        yield Snap(d)
            return Q(coll, field, value)
        def limit(self, n):
            class Q2:
                def __init__(self, coll, n):
                    self._coll = coll; self._n = n
                def stream(self):
                    for d in list(self._coll.values())[: self._n]:
                        class Snap:
                            def __init__(self, d): self._d=d; self.exists=True
                            def to_dict(self): return dict(self._d)
                        yield Snap(d)
            return Q2(coll, n)
    return _Col()

def _leave_col():
    fs = get_firestore()
    if fs is None:
        return _mem_collection(settings.firestore_leave_collection)
    return fs.collection(settings.firestore_leave_collection)

def _date_to_epoch(d: date) -> int:
    return int(datetime.combine(d, datetime.min.time()).timestamp())

def _count_days(start: date, end: date) -> int:
    return (end - start).days + 1

def _normalize_stored_enum(val):
    if val is None:
        return None
    try:
        return val.value
    except Exception:
        pass
    if isinstance(val, str) and "." in val:
        return val.split(".")[-1]
    return val

def _doc_to_out(doc: Dict[str, Any]) -> LeaveRequestOut:
    type_str = _normalize_stored_enum(doc.get("type"))
    status_str = _normalize_stored_enum(doc.get("status", LeaveStatus.pending.value))
    return LeaveRequestOut(
        id=doc["id"],
        employee_uid=doc["employee_uid"],
        type=LeaveType(type_str),
        start_date=datetime.fromtimestamp(doc["start_date"]).date(),
        end_date=datetime.fromtimestamp(doc["end_date"]).date(),
        reason=doc.get("reason"),
        status=LeaveStatus(status_str),
        requested_at=_epoch_to_dt(doc.get("requested_at")),
        approved_at=_epoch_to_dt(doc.get("approved_at")),
        approver_uid=doc.get("approver_uid"),
        approver_role=doc.get("approver_role"),
        days=doc.get("days"),
    )

def create_request(payload: dict) -> LeaveRequestOut:
    start = payload["start_date"]
    end = payload["end_date"]
    if isinstance(start, str):
        start = date.fromisoformat(start)
    if isinstance(end, str):
        end = date.fromisoformat(end)
    if end < start:
        raise ValueError("end_date must be >= start_date")
    days = _count_days(start, end)
    now = int(time.time())
    base_id = f"{payload['employee_uid']}-{now}"
    doc = {
        "id": base_id,
        "employee_uid": payload["employee_uid"],
        "type": (payload["type"].value if hasattr(payload["type"], "value") else str(payload["type"])),
        "start_date": _date_to_epoch(start),
        "end_date": _date_to_epoch(end),
        "reason": payload.get("reason"),
        "status": LeaveStatus.pending.value,
        "requested_at": now,
        "approved_at": None,
        "approver_uid": None,
        "approver_role": None,
        "days": days,
    }
    _leave_col().document(base_id).set(doc)
    return _doc_to_out(doc)

def get_request(request_id: str) -> Optional[LeaveRequestOut]:
    snap = _leave_col().document(request_id).get()
    if not snap.exists:
        return None
    return _doc_to_out(snap.to_dict())

def list_requests(limit: int = 50, offset: int = 0, employee_uid: Optional[str] = None, status: Optional[str] = None) -> List[LeaveRequestOut]:
    col = _leave_col()
    q = col
    if employee_uid:
        q = q.where("employee_uid", "==", employee_uid)
    if status is not None:
        # normalize status param
        stat = status.value if hasattr(status, "value") else status
        if "." in str(stat):
            stat = stat.split(".")[-1]
        q = q.where("status", "==", stat)
    snaps = q.limit(limit + offset).stream()
    res = []
    idx = 0
    for snap in snaps:
        if idx < offset:
            idx += 1
            continue
        res.append(_doc_to_out(snap.to_dict()))
    return res

def approve_request(request_id: str, approver_uid: str, approver_role: str) -> Optional[LeaveRequestOut]:
    doc_ref = _leave_col().document(request_id)
    snap = doc_ref.get()
    if not snap.exists:
        return None
    data = snap.to_dict()
    if data.get("status") == LeaveStatus.approved.value:
        return _doc_to_out(data)
    now = int(time.time())
    data["status"] = LeaveStatus.approved.value
    data["approved_at"] = now
    data["approver_uid"] = approver_uid
    data["approver_role"] = approver_role
    doc_ref.set(data, merge=True)
    return _doc_to_out(data)

def get_balance(employee_uid: str, year: int, leave_days_per_year: Optional[int] = None) -> Dict[str, int]:
    allow = leave_days_per_year if leave_days_per_year is not None else settings.leave_days_per_year
    snaps = _leave_col().where("employee_uid", "==", employee_uid).where("status", "==", LeaveStatus.approved.value).stream()
    used = 0
    for snap in snaps:
        d = snap.to_dict()
        start = datetime.fromtimestamp(d["start_date"]).date()
        end = datetime.fromtimestamp(d["end_date"]).date()
        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)
        eff_start = max(start, year_start)
        eff_end = min(end, year_end)
        if eff_end >= eff_start:
            if d.get("type") == LeaveType.vacation.value:
                used += _count_days(eff_start, eff_end)
    return {"employee_uid": employee_uid, "year": year, "allowance": allow, "used": used, "balance": max(allow - used, 0)}