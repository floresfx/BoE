"""Modelo Supplier — proveedor del tenant."""

from uuid import UUID

from sqlalchemy import Boolean, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimestampMixin, UUIDMixin
from app.models.base_tenant import TenantBase


class Supplier(TenantBase, UUIDMixin, TimestampMixin):
    """Proveedor de recursos (materiales, servicios, etc.)."""

    __tablename__ = "suppliers"
    __table_args__ = (
        UniqueConstraint("code", name="uq_supplier_code"),
        Index("ix_supplier_is_active", "is_active"),
        Index("ix_supplier_name", "name"),
    )

    code: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tax_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )

    # Relaciones
    resources = relationship(
        "SupplierResource",
        back_populates="supplier",
        cascade="all, delete-orphan",
    )