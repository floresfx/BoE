from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class AttributeType(Base, UUIDMixin, TimestampMixin):
    """Tipos de atributo (global)."""
    __tablename__ = "attribute_types"

    code: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )