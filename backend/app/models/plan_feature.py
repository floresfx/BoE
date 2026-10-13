from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class PlanFeature(Base, UUIDMixin, TimestampMixin):
    """Features por plan."""
    __tablename__ = "plan_features"
    __table_args__ = (
        UniqueConstraint("plan_id", "feature_id", name="uq_plan_feature"),
    )

    plan_id: Mapped[UUID] = mapped_column(
        ForeignKey("plans.id"), nullable=False, index=True
    )
    feature_id: Mapped[UUID] = mapped_column(
        ForeignKey("features.id"), nullable=False, index=True
    )

    # Relaciones
    plan = relationship("Plan", back_populates="features")
    feature = relationship("Feature")