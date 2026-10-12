from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Profile(Base, UUIDMixin, TimestampMixin):
    """Contexto del usuario."""
    __tablename__ = "profiles"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relaciones
    users = relationship(
        "User", secondary="user_profiles", back_populates="profiles"
    )


class UserProfile(Base):
    """Relación N:M entre usuarios y perfiles."""
    __tablename__ = "user_profiles"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), primary_key=True
    )
    profile_id: Mapped[UUID] = mapped_column(
        ForeignKey("profiles.id"), primary_key=True
    )