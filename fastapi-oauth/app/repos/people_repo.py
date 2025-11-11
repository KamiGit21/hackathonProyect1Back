from typing import Dict, Any, List, Optional
from app.firebase import get_firestore

EMPLOYEES = "employees"
POSITIONS = "positions"
CONTRACTS = "contracts"

def fs():
    return get_firestore()

# ---------------- Positions ----------------
def list_positions() -> List[Dict[str, Any]]:
    col = fs().collection(POSITIONS).stream()
    out = []
    for doc in col:
        d = doc.to_dict() or {}
        d["id"] = doc.id
        out.append(d)
    return out

def seed_positions_if_empty():
    col_ref = fs().collection(POSITIONS)
    docs = list(col_ref.limit(1).stream())
    if docs:
        return
    col_ref.document().set({"name": "Analista", "unitId": None, "grade": "P1"})
    col_ref.document().set({"name": "Jefe de Operaciones", "unitId": None, "grade": "M1"})
    col_ref.document().set({"name": "Gerente de RRHH", "unitId": None, "grade": "M2"})

def position_exists(position_id: str) -> bool:
    return fs().collection(POSITIONS).document(position_id).get().exists

def create_position(payload: Dict[str, Any]) -> Dict[str, Any]:
    data = {
        "name": payload["name"],
        "unitId": payload.get("unitId"),
        "grade": payload.get("grade"),
    }
    doc_ref = fs().collection(POSITIONS).document()
    doc_ref.set(data)
    return {"id": doc_ref.id, **data}

def get_position(position_id: str) -> Optional[Dict[str, Any]]:
    snap = fs().collection(POSITIONS).document(position_id).get()
    if not snap.exists:
        return None
    d = snap.to_dict() or {}
    d["id"] = snap.id
    return d

def update_position(position_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    doc_ref = fs().collection(POSITIONS).document(position_id)
    if not doc_ref.get().exists:
        return None
    # solo mergea campos presentes
    data = {k: v for k, v in payload.items() if v is not None}
    if not data:
        return get_position(position_id)
    doc_ref.set(data, merge=True)
    return get_position(position_id)

def delete_position(position_id: str) -> bool:
    doc_ref = fs().collection(POSITIONS).document(position_id)
    if not doc_ref.get().exists:
        return False
    doc_ref.delete()
    return True


# ---------------- Employees ----------------
def create_employee(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Email único (MVP)
    dup = fs().collection(EMPLOYEES).where("email", "==", payload["email"]).limit(1).stream()
    if next(dup, None):
        raise ValueError("Email ya registrado")

    data = {
        "ci": payload.get("ci"),
        "name": payload["name"],
        "email": payload["email"],
        "phone": payload.get("phone"),
        "status": "ACTIVE",
    }
    doc_ref = fs().collection(EMPLOYEES).document()
    doc_ref.set(data)
    return {"id": doc_ref.id, **data}

def list_employees() -> List[Dict[str, Any]]:
    col = fs().collection(EMPLOYEES).stream()
    out = []
    for doc in col:
        d = doc.to_dict() or {}
        d["id"] = doc.id
        out.append(d)
    return out

def get_employee(emp_id: str) -> Optional[Dict[str, Any]]:
    snap = fs().collection(EMPLOYEES).document(emp_id).get()
    if not snap.exists:
        return None
    d = snap.to_dict() or {}
    d["id"] = snap.id
    return d

def update_employee(emp_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    doc_ref = fs().collection(EMPLOYEES).document(emp_id)
    snap = doc_ref.get()
    if not snap.exists:
        return None

    current = snap.to_dict() or {}
    data = {k: v for k, v in payload.items() if v is not None}

    # Validación email único si cambia
    new_email = data.get("email")
    if new_email and new_email != current.get("email"):
        q = fs().collection(EMPLOYEES).where("email", "==", new_email).limit(1).stream()
        other = next(q, None)
        if other and other.id != emp_id:
            raise ValueError("Email ya registrado por otro empleado")

    if data:
        doc_ref.set(data, merge=True)
    return get_employee(emp_id)

def delete_employee_soft(emp_id: str) -> bool:
    doc_ref = fs().collection(EMPLOYEES).document(emp_id)
    if not doc_ref.get().exists:
        return False
    doc_ref.set({"status": "INACTIVE"}, merge=True)
    return True

def delete_employee_hard(emp_id: str) -> bool:
    doc_ref = fs().collection(EMPLOYEES).document(emp_id)
    if not doc_ref.get().exists:
        return False
    doc_ref.delete()
    return True


# ---------------- Contracts ----------------
def create_contract(emp_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if not get_employee(emp_id):
        raise LookupError("Empleado no encontrado")
    if not position_exists(payload["positionId"]):
        raise ValueError("positionId inválido")

    data = {
        "employeeId": emp_id,
        "positionId": payload["positionId"],
        "baseSalary": float(payload["baseSalary"]),
        "currency": payload.get("currency", "BOB"),
        "startDate": payload["startDate"],
        "endDate": payload.get("endDate"),
    }
    doc_ref = fs().collection(CONTRACTS).document()
    doc_ref.set(data)
    return {"id": doc_ref.id, **data}

def get_contract(contract_id: str) -> Optional[Dict[str, Any]]:
    snap = fs().collection(CONTRACTS).document(contract_id).get()
    if not snap.exists:
        return None
    d = snap.to_dict() or {}
    d["id"] = snap.id
    return d

def list_contracts_by_employee(emp_id: str) -> List[Dict[str, Any]]:
    col = fs().collection(CONTRACTS).where("employeeId", "==", emp_id).stream()
    out = []
    for doc in col:
        d = doc.to_dict() or {}
        d["id"] = doc.id
        out.append(d)
    return out

def update_contract(contract_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    doc_ref = fs().collection(CONTRACTS).document(contract_id)
    snap = doc_ref.get()
    if not snap.exists:
        return None

    data = {k: v for k, v in payload.items() if v is not None}

    # si cambian positionId, validarlo
    if "positionId" in data and data["positionId"] is not None:
        if not position_exists(data["positionId"]):
            raise ValueError("positionId inválido")

    if data:
        doc_ref.set(data, merge=True)
    return get_contract(contract_id)

def delete_contract(contract_id: str) -> bool:
    doc_ref = fs().collection(CONTRACTS).document(contract_id)
    if not doc_ref.get().exists:
        return False
    doc_ref.delete()
    return True
