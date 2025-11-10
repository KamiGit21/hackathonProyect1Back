# app/routers/auth.py
from fastapi import APIRouter, Request, HTTPException, Depends
from authlib.integrations.starlette_client import OAuth, OAuthError

from app.config import settings
from app.security import create_access_token
from app.schemas import TokenOut, MeOut, StaffOut
from app.firebase import get_auth
from app.repos.users_repo import (
    create_or_update_from_google,
    get_user_doc,
)
from app.deps import current_user  # valida tu JWT y carga usuario desde Firestore

router = APIRouter(prefix="/auth", tags=["auth"])

# ──────────────────────────────────────────────────────────────────────────────
# OAuth cliente (Google)
# ──────────────────────────────────────────────────────────────────────────────
oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# ──────────────────────────────────────────────────────────────────────────────
# Rutas
# ──────────────────────────────────────────────────────────────────────────────
@router.get("/google/login")
async def google_login(request: Request):
    """
    Inicia el flujo de OAuth en Google (redirección al consentimiento).
    """
    return await oauth.google.authorize_redirect(request, settings.google_redirect_uri)


@router.get("/google/callback", response_model=MeOut)
async def google_callback(request: Request):
    """
    Callback de Google:
      1) Intercambia 'code' por tokens y userinfo
      2) Asegura usuario en Firebase Auth
      3) Upsert del perfil en Firestore (colección 'users')
      4) Emite JWT propio con sub=uid y roles
    """
    # 1) Intercambiar code por tokens y obtener userinfo
    try:
        token = await oauth.google.authorize_access_token(request)

        userinfo = None
        # intentar decodificar id_token primero (OIDC)
        if token and "id_token" in token:
            try:
                userinfo = await oauth.google.parse_id_token(request, token)
            except Exception:
                userinfo = None

        # fallback: userinfo endpoint
        if not userinfo:
            userinfo_endpoint = oauth.google.server_metadata.get(
                "userinfo_endpoint",
                "https://openidconnect.googleapis.com/v1/userinfo"
            )
            resp = await oauth.google.get(userinfo_endpoint, token=token)
            data = resp.json()
            userinfo = {
                "sub": data.get("sub"),
                "email": data.get("email"),
                "name": data.get("name"),
                "given_name": data.get("given_name") or (data.get("name") or "").split(" ")[0],
                "family_name": data.get("family_name"),
                "picture": data.get("picture"),
                "email_verified": data.get("email_verified"),
            }
            if not userinfo.get("sub"):
                raise HTTPException(status_code=400, detail="Google userinfo sin 'sub'")
    except OAuthError as e:
        # Error propio de Authlib/OAuth
        raise HTTPException(
            status_code=400,
            detail={"error": e.error, "description": e.description, "uri": getattr(e, "uri", None)},
        )

    # 2) Firebase Auth: asegurar el usuario (uid = sub de Google)
    fb_auth = get_auth()
    uid = userinfo["sub"]

    try:
        fb_auth.get_user(uid)
        # si ya existe, refrescamos datos básicos
        fb_auth.update_user(
            uid=uid,
            email=userinfo.get("email"),
            email_verified=bool(userinfo.get("email_verified")),
            display_name=userinfo.get("name"),
            photo_url=userinfo.get("picture"),
            disabled=False,
        )
    except Exception:
        # si no existe, lo creamos
        fb_auth.create_user(
            uid=uid,
            email=userinfo.get("email"),
            email_verified=bool(userinfo.get("email_verified")),
            display_name=userinfo.get("name"),
            photo_url=userinfo.get("picture"),
            disabled=False,
        )

    # 3) Firestore: upsert del perfil en colección users
    user_out = create_or_update_from_google(userinfo, uid)

    # Cargar doc completo para extraer roles
    doc = get_user_doc(uid) or {}
    roles = doc.get("roles", ["EMPLOYEE"])

    # 4) Emite tu JWT propio incluyendo roles (útil para BFF/UI)
    access = create_access_token({"sub": uid, "email": userinfo.get("email"), "roles": roles})

    return {"user": user_out, "token": TokenOut(access_token=access)}


@router.get("/me", response_model=StaffOut)
def me(user: StaffOut = Depends(current_user)):
    """
    Devuelve el perfil del usuario autenticado (según tu JWT + Firestore).
    """
    return user
