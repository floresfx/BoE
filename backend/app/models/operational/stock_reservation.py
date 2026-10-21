"""Modelo para reservas de stock."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimestampMixin, UUIDMixin
from app.models.base_tenant import TenantBase

RESERVATION_STATUSES = ("pending", "confirmed", "fulfilled", "cancelled")


class StockReservation(TenantBase, UUIDMixin, TimestampMixin):
    """Una reserva de stock para un pedido futuro."""
    __tablename__ = "stock_reservations"

    warehouse_id: Mapped[UUID] = mapped_column(
        ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False
    )
    resource_id: Mapped[UUID] = mapped_column(
        ForeignKey("resources.id", ondelete="CASCADE"), nullable=False
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )
    reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    needed_by: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_by: Mapped[UUID | None] = mapped_column(nullable=True)

    # Relaciones
    warehouse = relationship("Warehouse")
    resource = relationship("Resource")