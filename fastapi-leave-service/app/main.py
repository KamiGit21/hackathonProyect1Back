# filepath: [main.py](http://_vscodecontentref_/10)
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.firebase import init_firebase
from app.routers import leave as leave_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_firebase()
    except Exception as e:
        print(f"[WARN] Firebase init skipped/failed: {e}")
    yield

app = FastAPI(title="Leave Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leave_router.router, prefix="/leave", tags=["leave"])

@app.get("/health")
def health():
    return {"status": "ok"}