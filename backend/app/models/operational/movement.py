"""Modelo Movement — movimiento inmutable de inventario."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimestampMixin, UUIDMixin
from app.models.base_tenant import TenantBase

MOVEMENT_TYPES = ("in", "out", "adjust", "loss")


class Movement(TenantBase, UUIDMixin, TimestampMixin):
    """Movimiento de inventario. INMUTABLE.

    Para revertir, se crea otro movimiento opuesto.
    """

    __tablename__ = "movements"
    __table_args__ = (
        Index("ix_movement_warehouse", "warehouse_id"),
        Index("ix_movement_resource", "resource_id"),
        Index("ix_movement_type", "movement_type"),
        Index("ix_movement_created_at", "created_at"),
    )

    warehouse_id: Mapped[UUID] = mapped_column(
        ForeignKey("warehouses.id"), nullable=False
    )
    resource_id: Mapped[UUID] = mapped_column(
        ForeignKey("resources.id"), nullable=False
    )
    lot_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("stock_lots.id"), nullable=True
    )
    movement_type: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False
    )
    unit_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4), nullable=True
    )
    reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    # Relaciones
    warehouse = relationship("Warehouse", back_populates="movements")
    lot = relationship("StockLot", back_populates="movements")