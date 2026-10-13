from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Subcategory(Base, UUIDMixin, TimestampMixin):
    """Subcategorías (global)."""
    __tablename__ = "subcategories"
    __table_args__ = (
        UniqueConstraint(
            "category_id", "code", name="uq_subcategory_category_code"
        ),
    )

    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("categories.id"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )

    category = relationship("Category", back_populates="subcategories")