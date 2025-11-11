#app/models.py
from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    String, Integer, SmallInteger, ForeignKey, Boolean, DateTime
)
from sqlalchemy.dialects.mysql import BLOB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base


class Staff(Base):
    __tablename__ = "staff"

    staff_id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(45), nullable=False)
    last_name: Mapped[str] = mapped_column(String(45), nullable=False)
    email: Mapped[str | None] = mapped_column(String(50))
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    username: Mapped[str] = mapped_column(String(16), nullable=False)
    password: Mapped[str | None] = mapped_column(String(40))  # sakila lo define así
    picture: Mapped[bytes | None] = mapped_column(BLOB)
    # 👇 IMPORTANTE: tipado con Mapped[datetime]
    last_update: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )

    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(
        "OAuthAccount", back_populates="staff", cascade="all, delete-orphan"
    )


class OAuthAccount(Base):
    __tablename__ = "oauth_account"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_sub: Mapped[str] = mapped_column(String(255), nullable=False)
    staff_id: Mapped[int] = mapped_column(SmallInteger, ForeignKey("staff.staff_id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )

    staff: Mapped[Staff] = relationship("Staff", back_populates="oauth_accounts")
