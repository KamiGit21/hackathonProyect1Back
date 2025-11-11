from fastapi import Header, HTTPException
from app.config import settings

def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """
    Dependency to verify API key for microservice communication
    """
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=401, 
            detail="Invalid API Key"
        )
    return True