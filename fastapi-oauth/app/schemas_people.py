from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Literal

# === Positions ===
class PositionOut(BaseModel):
    id: str
    name: str
    unitId: Optional[str] = None
    grade: Optional[str] = None

class PositionCreate(BaseModel):
    name: str
    unitId: Optional[str] = None
    grade: Optional[str] = None

class PositionUpdate(BaseModel):
    name: Optional[str] = None
    unitId: Optional[str] = None
    grade: Optional[str] = None


# === Employees ===
class EmployeeCreate(BaseModel):
    ci: Optional[str] = None
    name: str = Field(..., min_length=3)
    email: EmailStr
    phone: Optional[str] = None

class EmployeeOut(BaseModel):
    id: str
    ci: Optional[str] = None
    name: str
    email: EmailStr
    phone: Optional[str] = None
    status: Literal["ACTIVE", "INACTIVE"]

class EmployeeUpdate(BaseModel):
    ci: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: Optional[Literal["ACTIVE", "INACTIVE"]] = None


# === Contracts ===
class ContractCreate(BaseModel):
    positionId: str
    baseSalary: float
    currency: str = "BOB"
    startDate: str           # "YYYY-MM-DD"
    endDate: Optional[str] = None

class ContractOut(BaseModel):
    id: str
    employeeId: str
    positionId: str
    baseSalary: float
    currency: str
    startDate: str
    endDate: Optional[str] = None

class ContractUpdate(BaseModel):
    positionId: Optional[str] = None
    baseSalary: Optional[float] = None
    currency: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
