from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.firebase import init_firebase
from app.routers import notifications, events

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hr-notify")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting HR-NOTIFY Microservice...")
    logger.info(f"📋 Project ID: {settings.firebase_project_id}")
    logger.info(f"🔐 API Key enabled: {'Yes' if settings.api_key else 'No'}")
    logger.info(f"📧 HR Emails: {settings.hr_notification_emails}")
    
    try:
        init_firebase()
        logger.info("✅ Firebase initialized successfully")
    except Exception as e:
        logger.error(f"❌ Firebase initialization failed: {e}")
        # En Docker, es mejor fallar rápido si Firebase no funciona
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down HR-NOTIFY Microservice")

app = FastAPI(
    title="HR-NOTIFY Microservice",
    description="Microservicio de notificaciones para ARCA LTDA - Proyecto: hr-notify-52866",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(notifications.router, prefix="/api/v1", tags=["notifications"])
app.include_router(events.router, prefix="/api/v1", tags=["events"])

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "HR-NOTIFY",
        "project_id": settings.firebase_project_id,
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    return {
        "message": "HR-NOTIFY Microservice - ARCA LTDA",
        "project": settings.firebase_project_id,
        "endpoints": {
            "notify": "POST /api/v1/notifications/notify",
            "events": {
                "leave_approved": "POST /api/v1/events/leave-approved",
                "payroll_preview_ready": "POST /api/v1/events/payroll-preview-ready"
            },
            "health": "GET /health"
        }
    }