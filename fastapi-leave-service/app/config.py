
# filepath: [config.py](http://_vscodecontentref_/12)
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "")
    firebase_credentials_path: str = FIREBASE_CREDENTIALS_PATH
    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "")
    use_firestore: bool = os.getenv("USE_FIRESTORE", "true").lower() == "true"
    firestore_leave_collection: str = os.getenv("FIRESTORE_LEAVE_COLLECTION", "leave_requests")

    jwt_secret: str = os.getenv("JWT_SECRET", "change-me")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")

    pubsub_topic: str = os.getenv("PUBSUB_TOPIC", "")

    hr_emails: list[str] = [e.strip() for e in os.getenv("HR_EMAILS", "").split(",") if e.strip()]
    manager_emails: list[str] = [e.strip() for e in os.getenv("MANAGER_EMAILS", "").split(",") if e.strip()]

    leave_days_per_year: int = int(os.getenv("LEAVE_DAYS_PER_YEAR", "15"))

    cors_origins: list[str] = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]

settings = Settings()