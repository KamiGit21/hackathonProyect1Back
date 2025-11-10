import time
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from app.firebase import get_firestore
from app.config import settings
from app.schemas import LeaveRequestOut, LeaveStatus, LeaveType
from app.repos.users_repo import _epoch_to_dt  # utilidad ya definida

# --- Simple fallback en memoria para desarrollo cuando Firestore no está disponible ---
# Estructura: _MEM_DB[collection_name] = { doc_id: doc_dict, ... }
_MEM_DB: Dict[str, Dict[str, Dict[str, Any]]] = {}

class _MemDocSnap:
    def __init__(self, data: Optional[Dict[str, Any]]):
        self._data = data or {}
        self.exists = bool(data)

    def to_dict(self):
        return dict(self._data)

class _MemDocRef:
    def __init__(self, coll: Dict[str, Dict[str, Any]], doc_id: str):
        self._coll = coll
        self._id = str(doc_id)

    def set(self, data: Dict[str, Any], merge: bool = False):
        if merge and self._id in self._coll:
            cur = self._coll[self._id].copy()
            cur.update(data)
            self._coll[self._id] = cur
        else:
            self._coll[self._id] = dict(data)

    def get(self):
        return _MemDocSnap(self._coll.get(self._id))

class _MemQuery:
    def __init__(self, coll: Dict[str, Dict[str, Any]]):
        self._coll = coll
        self._filters = []  # list of (field, op, value)
        self._limit = None

    def where(self, field: str, op: str, value: Any):
        # solo soportamos op "=="
        self._filters.append((field, op, value))
        return self

    def limit(self, n: int):
        self._limit = int(n)
        return self

    def stream(self):
        items = list(self._coll.values())
        # aplicar filtros simples
        for f, op, val in self._filters:
            if op == "==":
                items = [d for d in items if d.get(f) == val]
            else:
                # op no soportado, ignora -> no filtra
                pass
        if self._limit is not None:
            items = items[: self._limit]
        for d in items:
            yield _MemDocSnap(d)

def _mem_collection(name: str):
    if name not in _MEM_DB:
        _MEM_DB[name] = {}
    coll = _MEM_DB[name]

    class _ColWrapper:
        def document(self, doc_id: str):
            return _MemDocRef(coll, doc_id)

        def where(self, field: str, op: str, value: Any):
            return _MemQuery(coll).where(field, op, value)

        def limit(self, n: int):
            return _MemQuery(coll).limit(n)

        def stream(self):
            for d in list(coll.values()):
                yield _MemDocSnap(d)

    return _ColWrapper()

# --- Helpers reales / principal ---
def _leave_col():
    fs = get_firestore()
    if fs is None:
        # Firestore no inicializado: usar fallback en memoria (desarrollo / pruebas)
        # NOTA: en producción deberías asegurarte de tener credenciales y setear USE_FIRESTORE=true
        return _mem_collection(settings.firestore_leave_collection)
    return fs.collection(settings.firestore_leave_collection)

def _enum_to_value(v):
    # devuelve el value si es Enum, si no devuelve el valor tal cual (string)
    try:
        return v.value
    except Exception:
        return v

def _date_to_epoch(d: date) -> int:
    return int(datetime.combine(d, datetime.min.time()).timestamp())

def _count_days(start: date, end: date) -> int:
    # inclusive days
    return (end - start).days + 1

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
    """
    payload: dict con fields employee_uid, type, start_date (date obj or iso), end_date, reason
    """
    # normalizar fechas a epoch
    start = payload["start_date"]
    end = payload["end_date"]
    if isinstance(start, str):
        start = date.fromisoformat(start)
    if isinstance(end, str):
        end = date.fromisoformat(end)

    if end < start:
        raise ValueError("end_date debe ser igual o posterior a start_date")

    days = _count_days(start, end)
    now = int(time.time())

    # generar id por timestamp + uid simple
    base_id = f"{payload['employee_uid']}-{now}"
    doc = {
        "id": base_id,
        "employee_uid": payload["employee_uid"],
        # GUARDA EL .value DEL ENUM SI EXISTE
        "type": _enum_to_value(payload["type"]),
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

    doc_ref = _leave_col().document(base_id)
    doc_ref.set(doc)
    return _doc_to_out(doc)

def get_request(request_id: str) -> Optional[LeaveRequestOut]:
    snap = _leave_col().document(request_id).get()
    if not snap.exists:
        return None
    data = snap.to_dict()
    return _doc_to_out(data)

def list_requests(limit: int = 50, offset: int = 0, employee_uid: Optional[str] = None, status: Optional[str] = None) -> List[LeaveRequestOut]:
    col = _leave_col()
    q = col
    if employee_uid:
        q = q.where("employee_uid", "==", employee_uid)
    if status is not None:
        # acepta enum o strings con prefijo; normalizamos al value simple
        status_norm = _normalize_stored_enum(status)
        q = q.where("status", "==", status_norm)
    snaps = q.limit(limit + offset).stream()
    results = []
    idx = 0
    for snap in snaps:
        if idx < offset:
            idx += 1
            continue
        data = snap.to_dict()
        results.append(_doc_to_out(data))
    return results

def approve_request(request_id: str, approver_uid: str, approver_role: str) -> Optional[LeaveRequestOut]:
    doc_ref = _leave_col().document(request_id)
    snap = doc_ref.get()
    if not snap.exists:
        return None
    data = snap.to_dict()
    if data.get("status") == LeaveStatus.approved.value:
        # ya aprobado; devolvemos
        return _doc_to_out(data)

    now = int(time.time())
    data["status"] = LeaveStatus.approved.value
    data["approved_at"] = now
    data["approver_uid"] = approver_uid
    data["approver_role"] = approver_role

    doc_ref.set(data, merge=True)

    # Evento simple: en MVP dejamos que los consumidores lean esta colección y actúen.
    # Para integración con Pub/Sub o cola, aquí podrías publicar un mensaje.
    return _doc_to_out(data)

def get_balance(employee_uid: str, year: int, leave_days_per_year: Optional[int] = None) -> Dict[str, int]:
    """
    Calcula saldo simple: allowance - sum(approved vacation days en año)
    """
    allow = leave_days_per_year if leave_days_per_year is not None else settings.leave_days_per_year
    snaps = _leave_col().where("employee_uid", "==", employee_uid).where("status", "==", LeaveStatus.approved.value).stream()
    used = 0
    for snap in snaps:
        d = snap.to_dict()
        start = datetime.fromtimestamp(d["start_date"]).date()
        end = datetime.fromtimestamp(d["end_date"]).date()
        # contar solo días dentro del año
        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)
        effective_start = max(start, year_start)
        effective_end = min(end, year_end)
        if effective_end >= effective_start:
            if d.get("type") == LeaveType.vacation.value:
                used += _count_days(effective_start, effective_end)
    return {"employee_uid": employee_uid, "year": year, "allowance": allow, "used": used, "balance": max(allow - used, 0)}

# normalize stored enum-like values (acepta 'LeaveType.vacation', 'vacation', Enum, etc.)
def _normalize_stored_enum(val):
    if val is None:
        return None
    # si es Enum, devolver su .value
    try:
        return val.value
    except Exception:
        pass
    # si es string como "LeaveType.vacation" -> tomar parte posterior
    if isinstance(val, str) and "." in val:
        return val.split(".")[-1]
    return val