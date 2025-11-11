from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    firebase_credentials_path: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "secrets/payroll-sa.json")
    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "")
    use_firestore: bool = os.getenv("USE_FIRESTORE", "true").lower() == "true"

    firestore_employee_collection: str = os.getenv("FIRESTORE_EMPLOYEE_COLLECTION", "payroll_employees")
    firestore_events_collection: str = os.getenv("FIRESTORE_EVENTS_COLLECTION", "payroll_events")

    jwt_secret: str = os.getenv("JWT_SECRET", "change-me")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")

    pubsub_push_verification_token: str = os.getenv("PUBSUB_PUSH_VERIFICATION_TOKEN", "")

    cors_origins: list[str] = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]

settings = Settings()