from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Attribute(Base, UUIDMixin, TimestampMixin):
    """Atributos (global)."""
    __tablename__ = "attributes"

    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type_id: Mapped[UUID] = mapped_column(
        ForeignKey("attribute_types.id"), nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )

    type = relationship("AttributeType")
    verticals = relationship(
        "VerticalAttribute", back_populates="attribute"
    )