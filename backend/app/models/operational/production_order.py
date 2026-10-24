"""Modelo ProductionOrder — orden de producción."""

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
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimestampMixin, UUIDMixin
from app.models.base_tenant import TenantBase

PRODUCTION_ORDER_STATUSES = (
    "draft",
    "planned",
    "in_progress",
    "completed",
    "cancelled",
    "not_executed",
    "partial",
    "with_deviation",
)


class ProductionOrder(TenantBase, UUIDMixin, TimestampMixin):
    """Orden de producción.

    Representa producir N unidades de un bundle.
    """

    __tablename__ = "production_orders"
    __table_args__ = (
        Index("ix_prod_order_status", "status"),
        Index("ix_prod_order_bundle", "bundle_id"),
    )

    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    plan_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("production_plans.id", ondelete="SET NULL"),
        nullable=True,
    )
    bundle_id: Mapped[UUID] = mapped_column(
        ForeignKey("bundles.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="draft"
    )
    start_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    end_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    exception_type: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )
    exception_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relaciones
    plan = relationship("ProductionPlan", back_populates="orders")
    bundle = relationship("Bundle")
    annexes = relationship("PlanItemAnnex", back_populates="production_order")