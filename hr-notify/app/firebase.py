import os
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
from app.config import settings
import logging

logger = logging.getLogger("hr-notify")

# Global instances
firebase_app = None
firestore_client = None

def init_firebase():
    global firebase_app, firestore_client

    if firebase_app is not None:
        return

    try:
        # En Docker, la ruta es relativa al WORKDIR (/app)
        cred_path = Path(settings.firebase_credentials_path)
        
        logger.info(f"🔧 Initializing Firebase with project: {settings.firebase_project_id}")
        logger.info(f"📁 Credentials path: {cred_path}")

        if not cred_path.exists():
            raise FileNotFoundError(f"Firebase credentials file not found at: {cred_path}")

        # Inicializar Firebase Admin SDK
        cred = credentials.Certificate(str(cred_path))
        firebase_app = firebase_admin.initialize_app(cred, {
            "projectId": settings.firebase_project_id
        })

        # Inicializar Firestore
        if settings.use_firestore:
            firestore_client = firestore.client(app=firebase_app)
            logger.info("✅ Firebase Firestore initialized successfully")

    except Exception as e:
        logger.error(f"❌ Firebase initialization failed: {e}")
        raise

def get_firestore():
    if firestore_client is None:
        init_firebase()
    return firestore_client

def get_firebase_app():
    if firebase_app is None:
        init_firebase()
    return firebase_app