from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Role(Base, UUIDMixin, TimestampMixin):
    """Roles del sistema. Globales y fijos.

    Admin, Editor, Lector. No se personalizan por tenant.
    """
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relaciones
    users = relationship(
        "User", secondary="user_roles", back_populates="roles"
    )
    permissions = relationship(
        "Permission", secondary="role_permissions", back_populates="roles"
    )