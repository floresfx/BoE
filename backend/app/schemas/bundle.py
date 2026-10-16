"""Schemas Pydantic para Bundle."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


# ---------------------------------------------------------------------------
# Componente inline
# ---------------------------------------------------------------------------

class BundleComponentInline(BaseModel):
    resource_id: UUID
    quantity: Decimal = Field(..., gt=0)
    notes: str | None = None


# ---------------------------------------------------------------------------
# Bundle
# ---------------------------------------------------------------------------

class BundleBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    category_id: UUID | None = None
    is_active: bool = True


class BundleCreate(BundleBase):
    components: list[BundleComponentInline] = Field(default_factory=list)


class BundleUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    category_id: UUID | None = None
    is_active: bool | None = None


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class BundleComponentResponse(BaseModel):
    resource_id: UUID
    resource_name: str
    resource_unit_symbol: str | None
    quantity: Decimal
    notes: str | None


class BundleResponse(BundleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    components: list[BundleComponentResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class BundleListResponse(BaseSchema):
    items: list[BundleResponse]
    total: int


# ---------------------------------------------------------------------------
# Explode (resultado de la explosión)
# ---------------------------------------------------------------------------

class ExplodedComponent(BaseModel):
    """Un recurso requerido por el bundle."""
    resource_id: UUID
    resource_name: str
    resource_unit_symbol: str | None
    required_quantity: Decimal  # cantidad total requerida (componente × multiplicador)
    notes: str | None


class BundleExplodeResponse(BaseSchema):
    """Resultado de explotar un bundle."""
    bundle_id: UUID
    bundle_code: str
    bundle_name: str
    multiplier: Decimal  # cuántas veces se multiplica el bundle
    total_components: int
    components: list[ExplodedComponent]