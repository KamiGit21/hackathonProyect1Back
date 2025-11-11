from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from ..services.org_service import create_unit, assign_manager, get_units_flat, get_units_tree
from ..schemas.unit import UnitCreate, AssignManagerRequest

router = APIRouter(prefix="/org", tags=["org"])

def require_role(roles: list, x_user_role: Optional[str] = Header(None)):
    if not x_user_role or x_user_role not in roles:
        raise HTTPException(403, f"Requires: {', '.join(roles)}")

@router.get("/units")
def get_units(tree: bool = False):
    return get_units_tree() if tree else get_units_flat()

@router.post("/units")
def create(unit: UnitCreate, x_user_role: Optional[str] = Header(None)):
    require_role(["HR_ADMIN"], x_user_role)
    return create_unit(unit.name, unit.parentId)

@router.post("/assign-manager")
def assign(req: AssignManagerRequest, x_user_role: Optional[str] = Header(None)):
    require_role(["HR_ADMIN", "MANAGER"], x_user_role)
    return assign_manager(req.unitId, req.managerId)