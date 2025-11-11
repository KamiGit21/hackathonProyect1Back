from typing import Optional, Dict, Any, List
from datetime import datetime, date
from app.firebase import get_firestore
from app.config import settings

# simple in-memory fallback
_MEM_DB = {"employees": {}, "events": {}}

def _emp_col():
    fs = get_firestore()
    if fs is None:
        class Col:
            def document(self, doc_id):
                class DocRef:
                    def __init__(self, store, doc_id):
                        self.store = store; self.id = str(doc_id)
                    def set(self, data, merge=False):
                        if merge and self.id in self.store:
                            cur = self.store[self.id].copy(); cur.update(data); self.store[self.id] = cur
                        else:
                            self.store[self.id] = dict(data)
                    def get(self):
                        d = self.store.get(self.id)
                        class Snap:
                            def __init__(self,d): self._d=d; self.exists=bool(d)
                            def to_dict(self): return dict(self._d) if self._d else {}
                        return Snap(d)
                return DocRef(_MEM_DB["employees"], doc_id)
            def stream(self):
                for d in list(_MEM_DB["employees"].values()):
                    class Snap:
                        def __init__(self,d): self._d=d; self.exists=bool(d)
                        def to_dict(self): return dict(self._d)
                    yield Snap(d)
        return Col()
    return fs.collection(settings.firestore_employee_collection)

def _events_col():
    fs = get_firestore()
    if fs is None:
        class Col:
            def document(self, doc_id):
                class DocRef:
                    def __init__(self, store, doc_id):
                        self.store = store; self.id = str(doc_id)
                    def set(self, data, merge=False):
                        if merge and self.id in self.store:
                            cur = self.store[self.id].copy(); cur.update(data); self.store[self.id] = cur
                        else:
                            self.store[self.id] = dict(data)
                    def get(self):
                        d = self.store.get(self.id)
                        class Snap:
                            def __init__(self,d): self._d=d; self.exists=bool(d)
                            def to_dict(self): return dict(self._d) if self._d else {}
                        return Snap(d)
                return DocRef(_MEM_DB["events"], doc_id)
            def where(self, field, op, value):
                class Q:
                    def __init__(self, coll, field, value):
                        self.coll = coll; self.field = field; self.value = value
                    def stream(self):
                        for d in list(_MEM_DB["events"].values()):
                            if d.get(self.field) == self.value:
                                class Snap:
                                    def __init__(self,d): self._d=d; self.exists=True
                                    def to_dict(self): return dict(self._d)
                                yield Snap(d)
                return Q(_MEM_DB["events"], field, value)
            def stream(self):
                for d in list(_MEM_DB["events"].values()):
                    class Snap:
                        def __init__(self,d): self._d=d; self.exists=True
                        def to_dict(self): return dict(self._d)
                    yield Snap(d)
        return Col()
    return fs.collection(settings.firestore_events_collection)

# employee helpers
def upsert_employee(emp: Dict[str, Any]):
    doc_id = emp["uid"]
    _emp_col().document(doc_id).set(emp)
    return emp

def get_employee(uid: str) -> Optional[Dict[str, Any]]:
    snap = _emp_col().document(uid).get()
    if not snap.exists:
        return None
    return snap.to_dict()

def list_employees() -> List[Dict[str, Any]]:
    return [snap.to_dict() for snap in _emp_col().stream()]

# events
def add_event(event: Dict[str, Any]):
    # generate id from timestamp + randomish
    eid = event.get("id") or f"{event.get('employee_uid')}-{int(datetime.utcnow().timestamp())}"
    _events_col().document(eid).set(event)
    return event

def list_events_for_employee_period(employee_uid: str, period_ym: str):
    # simple filter: employee_uid and period field if present, else check date fields
    results = []
    for snap in _events_col().stream():
        d = snap.to_dict()
        if d.get("employee_uid") != employee_uid:
            continue
        # expect events to have start_date/end_date or date fields in ISO `YYYY-MM-DD`
        results.append(d)
    return results

def list_events_period(period_ym: str):
    res = []
    for snap in _events_col().stream():
        d = snap.to_dict()
        res.append(d)
    return res