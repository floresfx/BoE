from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Timezone(Base, UUIDMixin, TimestampMixin):
    """Zonas horarias (global).

    Usa nombres IANA estándar.
    """
    __tablename__ = "timezones"

    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    friendly_name: Mapped[str] = mapped_column(String(100), nullable=False)
    utc_offset: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )