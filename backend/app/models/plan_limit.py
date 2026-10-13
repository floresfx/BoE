from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class PlanLimit(Base, UUIDMixin, TimestampMixin):
    """Limites por plan."""
    __tablename__ = "plan_limits"
    __table_args__ = (
        UniqueConstraint("plan_id", "limit_code", name="uq_plan_limit"),
    )

    plan_id: Mapped[UUID] = mapped_column(
        ForeignKey("plans.id"), nullable=False, index=True
    )
    limit_code: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relaciones
    plan = relationship("Plan", back_populates="limits")