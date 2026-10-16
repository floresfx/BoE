"""Modelos Bundle y BundleComponent.

Un Bundle es un paquete de recursos con cantidades específicas.
Ejemplo: "Pan artesanal - lote 100 unidades" contiene:
- 10 kg de harina
- 0.5 kg de levadura
- 1 kg de sal
"""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimestampMixin, UUIDMixin
from app.models.base_tenant import TenantBase


class Bundle(TenantBase, UUIDMixin, TimestampMixin):
    """Paquete de recursos."""

    __tablename__ = "bundles"
    __table_args__ = (
        UniqueConstraint("code", name="uq_bundle_code"),
        Index("ix_bundle_is_active", "is_active"),
        Index("ix_bundle_name", "name"),
    )

    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )

    # Relaciones
    components = relationship(
        "BundleComponent",
        back_populates="bundle",
        cascade="all, delete-orphan",
    )


class BundleComponent(TenantBase, UUIDMixin, TimestampMixin):
    """Componente de un bundle: un recurso + cantidad."""

    __tablename__ = "bundle_components"
    __table_args__ = (
        UniqueConstraint(
            "bundle_id", "resource_id",
            name="uq_bundle_component",
        ),
        Index("ix_bundle_component_bundle", "bundle_id"),
        Index("ix_bundle_component_resource", "resource_id"),
    )

    bundle_id: Mapped[UUID] = mapped_column(
        ForeignKey("bundles.id", ondelete="CASCADE"), nullable=False
    )
    resource_id: Mapped[UUID] = mapped_column(
        ForeignKey("resources.id", ondelete="CASCADE"), nullable=False
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relaciones
    bundle = relationship("Bundle", back_populates="components")