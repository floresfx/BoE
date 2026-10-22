"""Modelos Bundle, BundleComponent y BundlePhase.

Un Bundle es un paquete de recursos con cantidades específicas.
Ahora puede contener otros Bundles (multinivel) y organizarse en fases.
"""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimestampMixin, UUIDMixin
from app.models.base_tenant import TenantBase

COMPONENT_TYPES = ("resource", "bundle")


class Bundle(TenantBase, UUIDMixin, TimestampMixin):
    """Paquete de recursos (puede contener otros bundles)."""

    __tablename__ = "bundles"
    __table_args__ = (
        UniqueConstraint("code", "version", name="uq_bundle_code_version"),
        Index("ix_bundle_is_active", "is_active"),
        Index("ix_bundle_name", "name"),
    )

    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    bundle_type: Mapped[str] = mapped_column(
        String(30), nullable=False, default="production"
    )
    sale_price: Mapped[Decimal | None] = mapped_column(  # <--- NUEVO
        Numeric(12, 2), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )

    # Relaciones
    components = relationship(
        "BundleComponent",
        back_populates="bundle",
        cascade="all, delete-orphan",
        foreign_keys="BundleComponent.bundle_id",
    )
    phases = relationship(
        "BundlePhase",
        back_populates="bundle",
        cascade="all, delete-orphan",
    )


class BundlePhase(TenantBase, UUIDMixin, TimestampMixin):
    """Fase agrupada dentro de un bundle."""

    __tablename__ = "bundle_phases"
    __table_args__ = (
        Index("ix_bundle_phase_bundle", "bundle_id"),
    )

    bundle_id: Mapped[UUID] = mapped_column(
        ForeignKey("bundles.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relaciones
    bundle = relationship("Bundle", back_populates="phases")
    components = relationship("BundleComponent", back_populates="phase")


class BundleComponent(TenantBase, UUIDMixin, TimestampMixin):
    """Componente de un bundle. Puede ser un Resource o otro Bundle."""

    __tablename__ = "bundle_components"
    __table_args__ = (
        UniqueConstraint(
            "bundle_id", "resource_id", "component_bundle_id",
            name="uq_bundle_component",
        ),
        Index("ix_bundle_component_bundle", "bundle_id"),
        Index("ix_bundle_component_resource", "resource_id"),
        Index("ix_bundle_component_sub_bundle", "component_bundle_id"),
    )

    bundle_id: Mapped[UUID] = mapped_column(
        ForeignKey("bundles.id", ondelete="CASCADE"), nullable=False
    )
    component_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="resource"
    )
    resource_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("resources.id", ondelete="CASCADE"), nullable=True
    )
    component_bundle_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("bundles.id", ondelete="CASCADE"), nullable=True
    )
    phase_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("bundle_phases.id", ondelete="SET NULL"), nullable=True
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    waste_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=0
    )
    season: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relaciones
    bundle = relationship(
        "Bundle", back_populates="components", foreign_keys=[bundle_id]
    )
    resource = relationship("Resource")
    component_bundle = relationship("Bundle", foreign_keys=[component_bundle_id])
    phase = relationship("BundlePhase", back_populates="components")