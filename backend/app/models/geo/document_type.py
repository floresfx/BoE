from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class DocumentType(Base, UUIDMixin, TimestampMixin):
    """Tipos de documento (global)."""
    __tablename__ = "document_types"

    code: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    country_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("countries.id"), nullable=True, index=True
    )
    format: Mapped[str | None] = mapped_column(String(50), nullable=True)
    regex: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )