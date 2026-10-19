"""Modelo ProductionPlan — plan maestro de producción."""

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

PRODUCTION_PLAN_STATUSES = (
    "draft",
    "planned",
    "in_progress",
    "completed",
    "cancelled",
)


class ProductionPlan(TenantBase, UUIDMixin, TimestampMixin):
    """Plan maestro de producción.

    Agrupa varias órdenes de producción con una fecha objetivo.
    """

    __tablename__ = "production_plans"
    __table_args__ = (
        Index("ix_pp_status", "status"),
        Index("ix_pp_target_date", "target_date"),
    )

    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="draft"
    )
    target_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relaciones
    orders = relationship(
        "ProductionOrder",
        back_populates="plan",
        cascade="all, delete-orphan",
    )