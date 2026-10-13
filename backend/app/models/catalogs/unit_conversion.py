from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class UnitConversion(Base, UUIDMixin, TimestampMixin):
    """Conversiones entre unidades (global)."""
    __tablename__ = "unit_conversions"

    from_unit_id: Mapped[UUID] = mapped_column(
        ForeignKey("units.id"), nullable=False, index=True
    )
    to_unit_id: Mapped[UUID] = mapped_column(
        ForeignKey("units.id"), nullable=False, index=True
    )
    factor: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    is_base: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )