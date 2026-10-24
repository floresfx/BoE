"""Modelo PlanItemAnnex (Anexos a producción)."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimestampMixin, UUIDMixin
from app.models.base_tenant import TenantBase


class PlanItemAnnex(TenantBase, UUIDMixin, TimestampMixin):
    """Anexo a una orden de producción. No modifica el bundle original."""

    __tablename__ = "plan_item_annexes"

    production_order_id: Mapped[UUID] = mapped_column(
        ForeignKey("production_orders.id", ondelete="CASCADE"), nullable=False
    )
    annex_type: Mapped[str] = mapped_column(String(30), nullable=False)
    resource_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("resources.id", ondelete="SET NULL"), nullable=True
    )
    quantity: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 4), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


    production_order = relationship("ProductionOrder", back_populates="annexes")
    resource = relationship("Resource")