# app/deps.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.config import settings
from app.repos.users_repo import get_user_by_uid
from app.schemas import StaffOut

security = HTTPBearer(auto_error=False)

def current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
) -> StaffOut:
    """
    - Lee Authorization: Bearer <JWT> (emitido por nuestro servicio)
    - Decodifica y valida JWT
    - Carga el usuario desde Firestore (colección users)
    """
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Falta token Bearer")

    token = creds.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=401, detail="Token sin 'sub'")
        uid = str(sub)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = get_user_by_uid(uid)
    if not user or not user.active:
        raise HTTPException(status_code=401, detail="Usuario no encontrado o inactivo")

    return user
