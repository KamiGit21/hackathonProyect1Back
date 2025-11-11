from pydantic import BaseModel
from typing import Optional, List

class Unit(BaseModel):
    id: str
    name: str
    parentId: Optional[str] = None
    managerId: Optional[str] = None
    children: List['Unit'] = []

    class Config:
        from_attributes = True