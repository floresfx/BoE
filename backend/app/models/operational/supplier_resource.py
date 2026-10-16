"""Modelo SupplierResource — N:M entre Supplier y Resource.

Incluye datos de la oferta: precio, lead time, cantidad mínima.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimestampMixin, UUIDMixin
from app.models.base_tenant import TenantBase


class SupplierResource(TenantBase, UUIDMixin, TimestampMixin):
    """Un proveedor puede suministrar varios recursos, con oferta."""

    __tablename__ = "supplier_resources"
    __table_args__ = (
        UniqueConstraint(
            "supplier_id", "resource_id",
            name="uq_supplier_resource",
        ),
        Index("ix_supplier_resource_supplier", "supplier_id"),
        Index("ix_supplier_resource_resource", "resource_id"),
    )

    supplier_id: Mapped[UUID] = mapped_column(
        ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False
    )
    resource_id: Mapped[UUID] = mapped_column(
        ForeignKey("resources.id", ondelete="CASCADE"), nullable=False
    )

    # Datos de la oferta
    unit_price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4), nullable=True
    )
    currency_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("currencies.id"), nullable=True
    )
    lead_time_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    min_quantity: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 4), nullable=True
    )
    valid_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relaciones
    supplier = relationship("Supplier", back_populates="resources")