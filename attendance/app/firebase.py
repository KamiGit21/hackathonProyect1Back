import firebase_admin
from firebase_admin import credentials, firestore
from app.config import settings
import os

_db = None

def initialize_firebase():
    """Inicializa Firebase con las credenciales"""
    global _db
    
    if not firebase_admin._apps:
        # Ruta al archivo de credenciales
        cred_path = os.path.join("secrets", "attendance", "firebase-credentials.json")
        
        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Firebase credentials not found at {cred_path}")
        
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'projectId': settings.FIREBASE_PROJECT_ID,
        })
    
    _db = firestore.client()
    return _db

def get_db():
    """Obtiene la instancia de Firestore"""
    global _db
    if _db is None:
        _db = initialize_firebase()
    return _db

# Colecciones de Firestore
PUNCHES_COLLECTION = "punches"
TIMESHEETS_COLLECTION = "timesheets"
EVENTS_COLLECTION = "events"