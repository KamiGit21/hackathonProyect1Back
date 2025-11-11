from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
from app.config import settings

firebase_app = None
firestore_client = None

def init_firebase():
    global firebase_app, firestore_client
    cred_path = Path(settings.firebase_credentials_path).expanduser().resolve()
    if not cred_path.is_file():
        raise FileNotFoundError(f"Firebase credentials file not found: {cred_path}")
    if firebase_app is None:
        cred = credentials.Certificate(str(cred_path))
        firebase_app = firebase_admin.initialize_app(cred, {"projectId": settings.firebase_project_id or None})
    if settings.use_firestore and firestore_client is None:
        firestore_client = firestore.client(app=firebase_app)

def get_firestore():
    if not settings.use_firestore:
        return None
    if firestore_client is None:
        init_firebase()
    return firestore_client