# app/firebase.py
import os
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, auth as fb_auth, firestore
from .config import settings

firebase_app = None
firestore_client = None

def init_firebase():
    global firebase_app, firestore_client

    # ✅ Resolver ruta absoluta aunque en settings sea relativa
    cred_path = Path(settings.firebase_credentials_path).expanduser().resolve()

    if not cred_path.is_file():
        raise FileNotFoundError(
            f"Firebase credentials file not found: {cred_path}\n"
            f"Tip: coloca el archivo ahí o ajusta FIREBASE_CREDENTIALS_PATH en .env"
        )

    if firebase_app is None:
        cred = credentials.Certificate(str(cred_path))
        firebase_app = firebase_admin.initialize_app(cred, {
            "projectId": settings.firebase_project_id or None
        })

    if settings.use_firestore and firestore_client is None:
        firestore_client = firestore.client(app=firebase_app)


def get_auth():
    if firebase_app is None:
        init_firebase()
    return fb_auth


def get_firestore():
    if settings.use_firestore:
        if firestore_client is None:
            init_firebase()
        return firestore_client
    return None
