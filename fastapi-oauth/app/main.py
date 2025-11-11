# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.config import settings
from app.firebase import init_firebase  # si usas Firebase Admin como te propuse
from app.routers import auth as auth_router
from app.routers import auth_roles
from app.routers import people as people_router
from app.repos.people_repo import seed_positions_if_empty

# Lifespan: inicializa servicios (Firebase, etc.)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔹 Inicializa Firebase una vez al arrancar
    try:
        init_firebase()
    except Exception as e:
        # Evita crashear el servidor por fallos en secretos; loguéalo si tienes logger
        print(f"[WARN] Firebase init skipped/failed: {e}")
    yield
    # 🔹 Cierre/limpieza si hicieras conexiones persistentes (DB, clientes, etc.)


app = FastAPI(
    title="Auth Service (Sakila + Google OAuth)",
    lifespan=lifespan,
)


# ✅ (Opcional) Restringe hosts de confianza en producción
# app.add_middleware(TrustedHostMiddleware, allowed_hosts=["example.com", "*.example.com", "localhost"])


# ✅ Session middleware (requerido por Authlib / flujos basados en sesión)
#    IMPORTANTE: en producción, usa https_only=True y same_site="none" si sirves desde un dominio distinto al frontend
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    same_site="lax",     # "none" si frontend y backend están en dominios distintos y tienes HTTPS
    https_only=False,    # True en prod detrás de HTTPS
    # session_cookie="session",  # opcional, personaliza el nombre
    # max_age=14 * 24 * 60 * 60, # opcional
)


# ✅ CORS
allowed_origins = settings.cors_origins or ["http://localhost:3000", "http://127.0.0.1:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ Rutas
# Si tu router ya define prefix internamente, déjalo así;
# si no, puedes darle un prefix aquí:
app.include_router(auth_router.router, tags=["auth"])
app.include_router(people_router.router, tags=["people"])
app.include_router(auth_roles.router, tags=["roles"])

# ✅ Healthcheck
@app.get("/health")
def health():
    return {"status": "ok"}
