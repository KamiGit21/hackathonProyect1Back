# app/authz.py
from enum import Enum
from fastapi import HTTPException, Depends, status
from typing import Iterable, List, Optional
from app.schemas import AuthUser
from app.deps import current_user

class Role(str, Enum):
    HR_ADMIN = "HR_ADMIN"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"

def has_any_role(user_roles: Iterable[str], allowed: Iterable[str]) -> bool:
    s = set(user_roles or [])
    return any(r in s for r in allowed)

def require_roles(*allowed: Role):
    """
    Uso:
      @router.post(..., dependencies=[Depends(require_roles(Role.HR_ADMIN))])
    o:
      def endpoint(user=Depends(require_roles(Role.MANAGER, Role.HR_ADMIN))):
          ...
    """
    allowed_str = [r.value if isinstance(r, Role) else str(r) for r in allowed]
    def _inner(user: AuthUser = Depends(current_user)) -> AuthUser:
        if not has_any_role(user.roles, allowed_str):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insuficientes permisos")
        return user
    return _inner

def require_self_or_roles(owner_id_param: str, *allowed: Role):
    """
    Verifica que el usuario sea dueño del recurso (comparando uid con un campo del path/query/body)
    o tenga uno de los roles permitidos.
    Uso:
      @router.get("/timesheet")
      def get_timesheet(empId: str, user=Depends(require_self_or_roles("empId", Role.MANAGER, Role.HR_ADMIN))):
          ...
    """
    allowed_str = [r.value if isinstance(r, Role) else str(r) for r in allowed]
    def _inner(user: AuthUser = Depends(current_user), **kwargs) -> AuthUser:
        owner = kwargs.get(owner_id_param)
        if owner and owner == user.uid:
            return user
        if has_any_role(user.roles, allowed_str):
            return user
        raise HTTPException(status_code=403, detail="Insuficientes permisos")
    return _inner
