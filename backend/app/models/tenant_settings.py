from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.catalogs import Attribute, Category, Unit
from app.models.geo import Tax


class TenantActiveUnit(Base, UUIDMixin, TimestampMixin):
    """Unidades de medida activadas por un tenant."""
    __tablename__ = "tenant_active_units"
    __table_args__ = (UniqueConstraint("tenant_id", "unit_id", name="uq_tenant_unit"),)

    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    unit_id: Mapped[UUID] = mapped_column(ForeignKey("units.id"), nullable=False)

    unit: Mapped[Unit] = relationship()


class TenantActiveCategory(Base, UUIDMixin, TimestampMixin):
    """Categorías activadas por un tenant."""
    __tablename__ = "tenant_active_categories"
    __table_args__ = (UniqueConstraint("tenant_id", "category_id", name="uq_tenant_category"),)

    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[UUID] = mapped_column(ForeignKey("categories.id"), nullable=False)

    category: Mapped[Category] = relationship()


class TenantActiveAttribute(Base, UUIDMixin, TimestampMixin):
    """Atributos activados por un tenant."""
    __tablename__ = "tenant_active_attributes"
    __table_args__ = (UniqueConstraint("tenant_id", "attribute_id", name="uq_tenant_attribute"),)

    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    attribute_id: Mapped[UUID] = mapped_column(ForeignKey("attributes.id"), nullable=False)

    attribute: Mapped[Attribute] = relationship()

class TenantActiveTax(Base, UUIDMixin, TimestampMixin):
    """Impuestos activados por un tenant."""
    __tablename__ = "tenant_active_taxes"
    __table_args__ = (UniqueConstraint("tenant_id", "tax_id", name="uq_tenant_tax"),)

    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    tax_id: Mapped[UUID] = mapped_column(ForeignKey("taxes.id"), nullable=False)

    tax: Mapped[Tax] = relationship()