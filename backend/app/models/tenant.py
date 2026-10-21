"""Modelo Tenant — cada empresa cliente del SaaS.

- Vive en public.tenants.
- Identificación externa: tax_id + name.
- admin_email: correo de contacto, no login directo.
- schema_name: generado por el sistema. No editable. No visible.
- Estados: activo, suspendido, cancelado.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.tenant_settings import (
    TenantActiveAttribute,
    TenantActiveCategory,
    TenantActiveUnit,
    TenantActiveTax,
)


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
    
    # NOTA: base_currency (String) ha sido eliminada porque la columna
    # fue borrada de la base de datos. Ahora solo usamos base_currency_id.
    
    timezone: Mapped[str] = mapped_column(
        String(50), nullable=False, default="America/Caracas"
    )
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    province: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)

    date_format_id: Mapped[UUID | None] = mapped_column(ForeignKey("date_formats.id"), nullable=True)
    number_format_id: Mapped[UUID | None] = mapped_column(ForeignKey("number_formats.id"), nullable=True)

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

    # --- Nueva columna para la Fundación ---
    base_currency_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("currencies.id"), nullable=True
    )

    # --- Nuevas relaciones para la Fundación ---
    active_units: Mapped[list[TenantActiveUnit]] = relationship(
        cascade="all, delete-orphan"
    )
    active_categories: Mapped[list[TenantActiveCategory]] = relationship(
        cascade="all, delete-orphan"
    )
    active_attributes: Mapped[list[TenantActiveAttribute]] = relationship(
        cascade="all, delete-orphan"
    )

    # --- Nuevas relaciones para la Fundación ---
    active_units: Mapped[list[TenantActiveUnit]] = relationship(
        cascade="all, delete-orphan"
    )
    active_categories: Mapped[list[TenantActiveCategory]] = relationship(
        cascade="all, delete-orphan"
    )
    active_attributes: Mapped[list[TenantActiveAttribute]] = relationship(
        cascade="all, delete-orphan"
    )
    active_taxes: Mapped[list["TenantActiveTax"]] = relationship(  # <--- AÑADIR ESTA LÍNEA
        cascade="all, delete-orphan"
    )

    # Relaciones existentes
    vertical = relationship("Vertical", back_populates="tenants")
    plan = relationship("Plan", back_populates="tenants")
    users = relationship("User", back_populates="tenant")