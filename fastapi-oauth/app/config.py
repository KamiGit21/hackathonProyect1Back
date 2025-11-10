# app/config.py
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    
    # Firebase Admin
    firebase_credentials_path: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "secrets/auth/auth-service-credentials.json")
    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "")  # opcional; suele venir en el JSON
    use_firestore: bool = os.getenv("USE_FIRESTORE", "true").lower() == "true"
    firestore_users_collection: str = os.getenv("FIRESTORE_USERS_COLLECTION", "users")

    default_active: int = int(os.getenv("DEFAULT_ACTIVE", "1"))

    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    google_redirect_uri: str = os.getenv("GOOGLE_REDIRECT_URI", "")

    jwt_secret: str = os.getenv("JWT_SECRET", "change-me")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expires_minutes: int = int(os.getenv("JWT_EXPIRES_MINUTES", "120"))

    cors_origins: list[str] = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
    session_secret: str = os.getenv("SESSION_SECRET", "dev-session-secret-change-me")

settings = Settings()
