from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class NumberFormat(Base, UUIDMixin, TimestampMixin):
    """Formatos de número (global)."""
    __tablename__ = "number_formats"

    code: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, index=True
    )
    thousands_sep: Mapped[str] = mapped_column(String(5), nullable=False)
    decimal_sep: Mapped[str] = mapped_column(String(5), nullable=False)
    example: Mapped[str] = mapped_column(String(30), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )