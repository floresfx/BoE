"""Modelo ExchangeRate (tasas de cambio)."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class ExchangeRate(Base, UUIDMixin, TimestampMixin):
    """Tasa de cambio entre dos monedas."""

    __tablename__ = "exchange_rates"

    from_currency_id: Mapped[UUID] = mapped_column(
        ForeignKey("currencies.id"), nullable=False
    )
    to_currency_id: Mapped[UUID] = mapped_column(
        ForeignKey("currencies.id"), nullable=False
    )
    rate: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    valid_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    from_currency = relationship("Currency", foreign_keys=[from_currency_id])
    to_currency = relationship("Currency", foreign_keys=[to_currency_id])