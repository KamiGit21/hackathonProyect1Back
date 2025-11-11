from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    # Firebase - Datos reales del proyecto
    firebase_credentials_path: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "secrets/auth/hr-notify-credentials.json")
    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "hr-notify-52866")
    use_firestore: bool = os.getenv("USE_FIRESTORE", "true").lower() == "true"
    firestore_users_collection: str = os.getenv("FIRESTORE_USERS_COLLECTION", "users")
    firestore_notifications_collection: str = os.getenv("FIRESTORE_NOTIFICATIONS_COLLECTION", "notifications")
    
    # HR Configuration
    hr_notification_emails: list[str] = [
        email.strip() 
        for email in os.getenv("HR_EMAILS", "hr@arca.ltd,admin@arca.ltd").split(",") 
        if email.strip()
    ]
    
    # Notification Settings
    default_notification_method: str = os.getenv("DEFAULT_NOTIFICATION_METHOD", "log")
    
    # API Security
    api_key: str = os.getenv("API_KEY", "hr-notify-dev-key-2024")
    
    # CORS
    cors_origins: list[str] = [
        origin.strip() 
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",") 
        if origin.strip()
    ]
    
    # Server Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8001"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

settings = Settings()