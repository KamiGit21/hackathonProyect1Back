# app/deps.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.config import settings
from app.schemas import AuthUser
from app.repos.users_repo import get_user_doc

security = HTTPBearer(auto_error=False)

def current_user(creds: HTTPAuthorizationCredentials = Depends(security)) -> AuthUser:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Falta token Bearer")

    token = creds.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        uid = str(payload.get("sub"))
        if not uid:
            raise HTTPException(status_code=401, detail="Token sin 'sub'")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    doc = get_user_doc(uid)
    if not doc or not doc.get("active", True):
        raise HTTPException(status_code=401, detail="Usuario no encontrado o inactivo")

    return AuthUser(uid=uid, email=doc.get("email"), roles=doc.get("roles", []))
