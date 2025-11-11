from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import httpx

from app.config import settings

security = HTTPBearer()

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Verifica el token con el servicio de autenticación.
    Si no tienes servicio de auth, puedes comentar esta función.
    """
    if not settings.AUTH_SERVICE_URL:
        # Si no hay servicio de auth configurado, saltamos la validación
        # Esto es útil para desarrollo
        return {"emp_id": "test_user"}
    
    token = credentials.credentials
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/verify",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return response.json()
    
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable"
        )

async def get_current_user(
    user_data: dict = Depends(verify_token)
) -> dict:
    """Obtiene el usuario actual desde el token"""
    return user_data

# Dependency opcional para endpoints que requieren autenticación
def require_auth():
    """
    Usa esta dependencia en los endpoints que requieren autenticación:
    @router.get("/protected", dependencies=[Depends(require_auth())])
    """
    return Depends(get_current_user)