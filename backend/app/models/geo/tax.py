from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Tax(Base, UUIDMixin, TimestampMixin):
    """Impuestos por pais (global)."""
    __tablename__ = "taxes"
    __table_args__ = (
        UniqueConstraint("country_id", "code", name="uq_tax_country_code"),
    )

    country_id: Mapped[UUID] = mapped_column(
        ForeignKey("countries.id"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    applies_to: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )