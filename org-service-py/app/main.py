from fastapi import FastAPI
from .routers import org

app = FastAPI(title="HR-ORG Service")
app.include_router(org.router)