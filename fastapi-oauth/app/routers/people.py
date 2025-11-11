from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.authz import require_roles, Role
from app.schemas_people import (
    EmployeeCreate, EmployeeOut, EmployeeUpdate,
    ContractCreate, ContractOut, ContractUpdate,
    PositionOut, PositionCreate, PositionUpdate
)
from app.repos import people_repo as repo
from app.events import emit_event

router = APIRouter(prefix="", tags=["people"])

# ------------ Employees ------------
@router.post("/employees", response_model=EmployeeOut,
             dependencies=[Depends(require_roles(Role.HR_ADMIN))])
def create_employee(payload: EmployeeCreate):
    try:
        emp = repo.create_employee(payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    emit_event("EmployeeCreated", {"employeeId": emp["id"], "email": emp["email"], "name": emp["name"]})
    return emp

@router.get("/employees", response_model=List[EmployeeOut])
def list_employees():
    return repo.list_employees()

@router.get("/employees/{emp_id}", response_model=EmployeeOut)
def get_employee(emp_id: str):
    emp = repo.get_employee(emp_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return emp

@router.patch("/employees/{emp_id}", response_model=EmployeeOut,
              dependencies=[Depends(require_roles(Role.HR_ADMIN))])
def update_employee(emp_id: str, payload: EmployeeUpdate):
    try:
        emp = repo.update_employee(emp_id, payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    if not emp:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return emp

# Soft delete por defecto (INACTIVE)
@router.delete("/employees/{emp_id}",
               dependencies=[Depends(require_roles(Role.HR_ADMIN))])
def delete_employee(emp_id: str, hard: Optional[bool] = False):
    ok = repo.delete_employee_hard(emp_id) if hard else repo.delete_employee_soft(emp_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return {"ok": True, "hard": bool(hard)}


# ------------ Positions ------------
@router.get("/positions", response_model=List[PositionOut])
def list_positions():
    return repo.list_positions()

@router.post("/positions", response_model=PositionOut,
             dependencies=[Depends(require_roles(Role.HR_ADMIN))])
def create_position(payload: PositionCreate):
    return repo.create_position(payload.model_dump())

@router.get("/positions/{position_id}", response_model=PositionOut)
def get_position(position_id: str):
    p = repo.get_position(position_id)
    if not p:
        raise HTTPException(status_code=404, detail="Posición no encontrada")
    return p

@router.patch("/positions/{position_id}", response_model=PositionOut,
              dependencies=[Depends(require_roles(Role.HR_ADMIN))])
def update_position(position_id: str, payload: PositionUpdate):
    p = repo.update_position(position_id, payload.model_dump())
    if not p:
        raise HTTPException(status_code=404, detail="Posición no encontrada")
    return p

@router.delete("/positions/{position_id}",
               dependencies=[Depends(require_roles(Role.HR_ADMIN))])
def delete_position(position_id: str):
    ok = repo.delete_position(position_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Posición no encontrada")
    return {"ok": True}


# ------------ Contracts ------------
@router.post("/employees/{emp_id}/contract", response_model=ContractOut,
             dependencies=[Depends(require_roles(Role.HR_ADMIN, Role.MANAGER))])
def assign_contract(emp_id: str, payload: ContractCreate):
    try:
        c = repo.create_contract(emp_id, payload.model_dump())
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    emit_event("ContractAssigned", {
        "employeeId": c["employeeId"],
        "contractId": c["id"],
        "positionId": c["positionId"],
        "baseSalary": c["baseSalary"],
        "currency": c["currency"],
        "startDate": c["startDate"],
        "endDate": c["endDate"],
    })
    return c

@router.get("/contracts/{contract_id}", response_model=ContractOut)
def get_contract(contract_id: str):
    c = repo.get_contract(contract_id)
    if not c:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    return c

@router.get("/employees/{emp_id}/contracts", response_model=List[ContractOut])
def list_contracts_by_employee(emp_id: str):
    return repo.list_contracts_by_employee(emp_id)

@router.patch("/contracts/{contract_id}", response_model=ContractOut,
              dependencies=[Depends(require_roles(Role.HR_ADMIN, Role.MANAGER))])
def update_contract(contract_id: str, payload: ContractUpdate):
    try:
        c = repo.update_contract(contract_id, payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not c:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    return c

@router.delete("/contracts/{contract_id}",
               dependencies=[Depends(require_roles(Role.HR_ADMIN))])
def delete_contract(contract_id: str):
    ok = repo.delete_contract(contract_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    return {"ok": True}
