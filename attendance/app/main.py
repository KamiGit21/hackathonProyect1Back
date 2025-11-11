from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.firebase import initialize_firebase
from app.routers import attendance

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events"""
    # Startup
    initialize_firebase()
    print("🔥 Firebase initialized")
    yield
    # Shutdown
    print("👋 Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(attendance.router, prefix=f"/api/{settings.API_VERSION}")

@app.get("/")
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.API_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}