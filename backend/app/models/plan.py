from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Numeric, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Plan(Base, UUIDMixin, TimestampMixin):
    """Planes de suscripcion."""
    __tablename__ = "plans"

    code: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency_id: Mapped[UUID] = mapped_column(
        ForeignKey("currencies.id"), nullable=False
    )
    interval: Mapped[str] = mapped_column(String(20), nullable=False)
    trial_days: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )

    # Relaciones
    currency = relationship("Currency")
    tenants = relationship("Tenant", back_populates="plan")
    features = relationship(
        "PlanFeature", back_populates="plan", cascade="all, delete-orphan"
    )
    limits = relationship(
        "PlanLimit", back_populates="plan", cascade="all, delete-orphan"
    )