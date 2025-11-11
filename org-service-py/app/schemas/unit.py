from pydantic import BaseModel
from typing import Optional

class UnitCreate(BaseModel):
    name: str
    parentId: Optional[str] = None

class AssignManagerRequest(BaseModel):
    unitId: str
    managerId: str