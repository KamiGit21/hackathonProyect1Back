# app/services/auth_service.py
from sqlalchemy.orm import Session
from app.models import Staff, OAuthAccount
from app.schemas import StaffOut
from app.config import settings
from typing import TypedDict


class GoogleProfile(TypedDict):
    sub: str
    email: str
    given_name: str
    family_name: str
    picture: str | None


PROVIDER = "google"


def get_or_create_staff_from_google(db: Session, profile: GoogleProfile) -> Staff:
    # 1) ¿ya existe vínculo oauth?
    link = db.query(OAuthAccount).filter_by(provider=PROVIDER, provider_sub=profile["sub"]).first()
    if link:
        return link.staff

    # 2) ¿existe staff con ese email? (puede ya existir en sakila)
    staff = db.query(Staff).filter(Staff.email == profile["email"]).first()
    if not staff:
        # Crear un nuevo staff con defaults configurables
        # username: hasta 16 chars en sakila; derivamos de email si cabe
        base_user = profile["email"].split("@")[0][:16]
        staff = Staff(
            first_name=profile["given_name"] or "Google",
            last_name=profile["family_name"] or "User",
            email=profile["email"],
            username=base_user,
            active=bool(settings.default_active),
            password=None,    # no usamos password local
        )
        db.add(staff)
        db.flush()  # para obtener staff_id

    # 3) crear vínculo oauth
    link = OAuthAccount(provider=PROVIDER, provider_sub=profile["sub"], staff_id=staff.staff_id)
    db.add(link)
    db.commit()
    db.refresh(staff)
    return staff


def staff_to_out(staff: Staff) -> StaffOut:
    return StaffOut.model_validate(staff)
