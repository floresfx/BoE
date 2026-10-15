"""Modelo Warehouse — ubicación física de inventario por tenant."""

from uuid import UUID

from sqlalchemy import Boolean, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimestampMixin, UUIDMixin
from app.models.base_tenant import TenantBase


class Warehouse(TenantBase, UUIDMixin, TimestampMixin):
    """Almacén, bodega o ubicación física de inventario."""

    __tablename__ = "warehouses"
    __table_args__ = (
        UniqueConstraint("code", name="uq_warehouse_code"),
        Index("ix_warehouse_is_active", "is_active"),
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )

    # Relaciones
    lots = relationship("StockLot", back_populates="warehouse")
    movements = relationship("Movement", back_populates="warehouse")