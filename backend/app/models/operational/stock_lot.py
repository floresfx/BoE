"""Modelo StockLot — lote de inventario con caducidad opcional."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimestampMixin, UUIDMixin
from app.models.base_tenant import TenantBase


class StockLot(TenantBase, UUIDMixin, TimestampMixin):
    """Lote de un recurso dentro de un warehouse.

    Un recurso puede tener varios lotes en el mismo warehouse si tienen
    distinta caducidad o costo.
    """

    __tablename__ = "stock_lots"
    __table_args__ = (
        UniqueConstraint(
            "warehouse_id", "resource_id", "lot_code",
            name="uq_lot_warehouse_resource_code",
        ),
        Index("ix_lot_warehouse_resource", "warehouse_id", "resource_id"),
        Index("ix_lot_expiration", "expiration"),
    )

    warehouse_id: Mapped[UUID] = mapped_column(
        ForeignKey("warehouses.id"), nullable=False
    )
    resource_id: Mapped[UUID] = mapped_column(
        ForeignKey("resources.id"), nullable=False
    )
    lot_code: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False, default=0
    )
    expiration: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    unit_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4), nullable=True
    )
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Relaciones
    warehouse = relationship("Warehouse", back_populates="lots")
    movements = relationship("Movement", back_populates="lot")