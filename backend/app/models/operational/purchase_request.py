
"""Modelos PurchaseRequest y PurchaseRequestLine.

Una solicitud de compra agrupa varios recursos que se necesitan
comprar. Cada solicitud tiene varias líneas (una por recurso).
"""

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

PURCHASE_REQUEST_STATUSES = (
    "draft",
    "pending",
    "approved",
    "rejected",
    "completed",
    "cancelled",
)


class PurchaseRequest(TenantBase, UUIDMixin, TimestampMixin):
    """Solicitud de compra."""

    __tablename__ = "purchase_requests"
    __table_args__ = (
        UniqueConstraint("code", name="uq_purchase_request_code"),
        Index("ix_purchase_request_status", "status"),
        Index("ix_purchase_request_needed_by", "needed_by"),
    )

    code: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="draft"
    )
    needed_by: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relaciones
    lines = relationship(
        "PurchaseRequestLine",
        back_populates="request",
        cascade="all, delete-orphan",
    )


class PurchaseRequestLine(TenantBase, UUIDMixin, TimestampMixin):
    """Línea de una solicitud de compra: un recurso + cantidad."""

    __tablename__ = "purchase_request_lines"
    __table_args__ = (
        UniqueConstraint(
            "request_id", "resource_id",
            name="uq_purchase_request_line",
        ),
        Index("ix_purchase_request_line_request", "request_id"),
    )

    request_id: Mapped[UUID] = mapped_column(
        ForeignKey("purchase_requests.id", ondelete="CASCADE"), nullable=False
    )
    resource_id: Mapped[UUID] = mapped_column(
        ForeignKey("resources.id"), nullable=False
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False
    )
    supplier_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relaciones
    request = relationship("PurchaseRequest", back_populates="lines")