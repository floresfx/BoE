from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class DateFormat(Base, UUIDMixin, TimestampMixin):
    """Formatos de fecha (global)."""
    __tablename__ = "date_formats"

    code: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, index=True
    )
    pattern: Mapped[str] = mapped_column(String(50), nullable=False)
    example: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )