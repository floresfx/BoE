"""Schemas Pydantic para Supplier."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import BaseSchema


# ---------------------------------------------------------------------------
# Resource inline (para create/update)
# ---------------------------------------------------------------------------

class SupplierResourceInline(BaseModel):
    resource_id: UUID
    notes: str | None = None


# ---------------------------------------------------------------------------
# Supplier
# ---------------------------------------------------------------------------

class SupplierBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=30)
    name: str = Field(..., min_length=1, max_length=255)
    tax_id: str | None = Field(None, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)
    address: str | None = None
    contact_name: str | None = Field(None, max_length=200)
    notes: str | None = None
    is_active: bool = True


class SupplierCreate(SupplierBase):
    resources: list[SupplierResourceInline] = Field(default_factory=list)


class SupplierUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    tax_id: str | None = Field(None, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)
    address: str | None = None
    contact_name: str | None = Field(None, max_length=200)
    notes: str | None = None
    is_active: bool | None = None


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class SupplierResourceResponse(BaseModel):
    resource_id: UUID
    resource_name: str
    notes: str | None

    model_config = {"from_attributes": True}


class SupplierResponse(SupplierBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    resources: list[SupplierResourceResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class SupplierListResponse(BaseSchema):
    items: list[SupplierResponse]
    total: int