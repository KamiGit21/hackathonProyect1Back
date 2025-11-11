from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    API_VERSION: str = "v1"
    PROJECT_NAME: str = "Attendance Service"
    DEBUG: bool = False
    
    # Firebase Settings
    FIREBASE_PROJECT_ID: str
    
    # Auth Settings (si necesitas integración con tu servicio de auth)
    AUTH_SERVICE_URL: Optional[str] = None
    
    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Timezone
    TIMEZONE: str = "America/La_Paz"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()