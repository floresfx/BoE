from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Unit(Base, UUIDMixin, TimestampMixin):
    """Unidades de medida (global)."""
    __tablename__ = "units"

    code: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False)
    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("unit_categories.id"), nullable=False
    )
    is_base: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )

    category = relationship("UnitCategory", back_populates="units")