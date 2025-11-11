from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.firebase import init_firebase
from app.routers import payroll, events

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_firebase()
    except Exception as e:
        print(f"[WARN] Firebase init skipped/failed: {e}")
    yield

app = FastAPI(title="Payroll Lite Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(payroll.router, prefix="/payroll", tags=["payroll"])
app.include_router(events.router, prefix="", tags=["events"])

@app.get("/health")
def health():
    return {"status": "ok"}