from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class FeatureDependency(Base, UUIDMixin, TimestampMixin):
    """Dependencias entre features."""
    __tablename__ = "feature_dependencies"
    __table_args__ = (
        UniqueConstraint(
            "feature_id", "depends_on_id", name="uq_feature_dep"
        ),
    )

    feature_id: Mapped[UUID] = mapped_column(
        ForeignKey("features.id"), nullable=False, index=True
    )
    depends_on_id: Mapped[UUID] = mapped_column(
        ForeignKey("features.id"), nullable=False, index=True
    )