"""Modelo SupplierQuote — cotización de un proveedor para una solicitud."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimestampMixin, UUIDMixin
from app.models.base_tenant import TenantBase


class SupplierQuote(TenantBase, UUIDMixin, TimestampMixin):
    """Cotización de un proveedor para una línea de solicitud.

    Un proveedor puede cotizar varias líneas de la misma solicitud.
    Cada cotización es por (solicitud, línea, proveedor).
    """

    __tablename__ = "supplier_quotes"
    __table_args__ = (
        Index("ix_quote_request", "request_id"),
        Index("ix_quote_supplier", "supplier_id"),
        Index("ix_quote_status", "status"),
    )

    request_id: Mapped[UUID] = mapped_column(
        ForeignKey("purchase_requests.id", ondelete="CASCADE"),
        nullable=False,
    )
    line_id: Mapped[UUID] = mapped_column(
        ForeignKey("purchase_request_lines.id", ondelete="CASCADE"),
        nullable=False,
    )
    supplier_id: Mapped[UUID] = mapped_column(
        ForeignKey("suppliers.id", ondelete="CASCADE"),
        nullable=False,
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False
    )
    currency_code: Mapped[str] = mapped_column(
        String(10), nullable=False, default="USD"
    )
    lead_time_days: Mapped[int] = mapped_column(
        nullable=False, default=0
    )
    valid_until: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )
    # estados: pending | accepted | rejected
    is_selected: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # Relaciones
    supplier = relationship("Supplier")
    request = relationship("PurchaseRequest")
    line = relationship("PurchaseRequestLine")