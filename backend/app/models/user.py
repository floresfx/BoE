from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    """Personas que acceden al sistema.

    - Viven en public.users (global).
    - Email único global.
    - Pertenecen a un único tenant.
    - Estados: activo, inactivo, suspendido.
    """
    __tablename__ = "users"

    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id"), nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    phone_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    # activo | inactivo | suspendido
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="activo"
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relaciones
    tenant = relationship("Tenant", back_populates="users")
    roles = relationship(
        "Role", secondary="user_roles", back_populates="users"
    )
    profiles = relationship(
        "Profile", secondary="user_profiles", back_populates="users"
    )
    secure_devices = relationship("SecureDevice", back_populates="user")
    access_logs = relationship("AccessLog", back_populates="user")