from typing import List, Optional
from uuid import uuid4
import logging
from .database import store
from .models import Unit

logger = logging.getLogger("uvicorn")

def create_unit(name: str, parentId: Optional[str]) -> Unit:
    if parentId and parentId not in store:
        raise ValueError("Parent not found")
    unit = Unit(id=str(uuid4()), name=name, parentId=parentId)
    store[unit.id] = unit
    logger.info(f"OrgEvent: UnitCreated id={unit.id} name={name}")
    return unit

def assign_manager(unitId: str, managerId: str) -> Unit:
    if unitId not in store:
        raise ValueError("Unit not found")
    store[unitId].managerId = managerId
    logger.info(f"OrgEvent: ManagerAssigned unit={unitId} manager={managerId}")
    logger.info(f"Notify: to={managerId} subject='Asignado como jefe'")
    return store[unitId]

def get_units_flat() -> List[Unit]:
    return list(store.values())

def get_units_tree() -> List[Unit]:
    units = {k: Unit(**v.dict()) for k, v in store.items()}
    roots = []
    for u in units.values():
        if u.parentId is None:
            roots.append(u)
        else:
            p = units.get(u.parentId)
            if p: p.children.append(u)
    return roots