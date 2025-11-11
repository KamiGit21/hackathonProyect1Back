# app/schemas.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from enum import Enum
from typing import Optional
from enum import Enum
from typing import List

class Role(str, Enum):
    HR_ADMIN = "HR_ADMIN"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"

class AuthUser(BaseModel):
    uid: str
    email: Optional[str] = None
    roles: List[str] = []

# === Documento de usuario (Firestore) ===
class UserDoc(BaseModel):
    uid: str
    email: EmailStr
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    username: str = Field(..., max_length=16)
    active: bool = True
    picture: Optional[str] = None
    provider: str = "google"
    provider_sub: Optional[str] = None
    roles: List[str] = []
    created_at: Optional[int] = None  # epoch
    updated_at: Optional[int] = None  # epoch
    last_login: Optional[int] = None  # epoch

# === Salidas compatibles con tu API anterior ===
class UserOut(BaseModel):
    uid: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    username: str
    active: bool
    last_update: Optional[datetime] = None
    roles: List[str] = []

# Alias de compatibilidad para no romper clientes
StaffOut = UserOut

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MeOut(BaseModel):
    user: StaffOut
    token: TokenOut
    roles: List[str] = []

# === Entradas administrativas opcionales ===
class StaffCreateFromGoogle(BaseModel):
    email: EmailStr
    given_name: str
    family_name: str
    username: str = Field(..., max_length=16)