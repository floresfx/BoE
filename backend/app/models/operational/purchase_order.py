"""Modelos PurchaseOrder y PurchaseOrderLine."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    DateTime,
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

PURCHASE_ORDER_STATUSES = (
    "draft",
    "sent",
    "confirmed",
    "received",
    "completed",
    "cancelled",
)


class PurchaseOrder(TenantBase, UUIDMixin, TimestampMixin):
    """Orden de compra formal a un proveedor."""

    __tablename__ = "purchase_orders"
    __table_args__ = (
        UniqueConstraint("code", name="uq_purchase_order_code"),
        Index("ix_po_request", "request_id"),
        Index("ix_po_supplier", "supplier_id"),
        Index("ix_po_status", "status"),
    )

    code: Mapped[str] = mapped_column(String(50), nullable=False)
    request_id: Mapped[UUID] = mapped_column(
        ForeignKey("purchase_requests.id", ondelete="SET NULL"),
        nullable=True,
    )
    supplier_id: Mapped[UUID] = mapped_column(
        ForeignKey("suppliers.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="draft"
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False, default=0
    )
    currency_code: Mapped[str] = mapped_column(
        String(10), nullable=False, default="USD"
    )
    expected_delivery: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relaciones
    lines = relationship(
        "PurchaseOrderLine",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    supplier = relationship("Supplier")
    request = relationship("PurchaseRequest")


class PurchaseOrderLine(TenantBase, UUIDMixin, TimestampMixin):
    """Línea de una orden de compra."""

    __tablename__ = "purchase_order_lines"
    __table_args__ = (
        Index("ix_pol_order", "order_id"),
        Index("ix_pol_resource", "resource_id"),
    )

    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("purchase_orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    resource_id: Mapped[UUID] = mapped_column(
        ForeignKey("resources.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False
    )
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False
    )

    # Relaciones
    order = relationship("PurchaseOrder", back_populates="lines")
    resource = relationship("Resource")