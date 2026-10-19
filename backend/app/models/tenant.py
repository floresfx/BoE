"""Modelo Tenant — cada empresa cliente del SaaS.

- Vive en public.tenants.
- Identificación externa: tax_id + name.
- admin_email: correo de contacto, no login directo.
- schema_name: generado por el sistema. No editable. No visible.
- Estados: activo, suspendido, cancelado.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from app.models.base import Base, TimestampMixin, UUIDMixin


class Tenant(Base, UUIDMixin, TimestampMixin):
    """Cada cliente (empresa) que usa la plataforma."""

    __tablename__ = "tenants"

    # Identificación
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tax_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    tax_id_type: Mapped[str] = mapped_column(String(20), nullable=False)
    admin_email: Mapped[str] = mapped_column(String(255), nullable=False)

    # Configuración
    vertical_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("verticals.id"), nullable=True
    )
    base_currency: Mapped[str] = mapped_column(
        String(10), nullable=False, default="USD"
    )
    timezone: Mapped[str] = mapped_column(
        String(50), nullable=False, default="America/Caracas"
    )
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    province: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Schema y estado
    schema_name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="activo"
    )

    # Suscripción
    plan_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("plans.id"), nullable=True
    )
    trial_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    subscription_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="sin_plan"
    )

    inventory_costing_method: Mapped[str] = mapped_column(
        String(20), nullable=False, default="fifo", server_default="fifo"
    )
    
    # Relaciones
    vertical = relationship("Vertical", back_populates="tenants")
    plan = relationship("Plan", back_populates="tenants")
    users = relationship("User", back_populates="tenant")