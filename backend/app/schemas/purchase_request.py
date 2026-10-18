"""Schemas Pydantic para PurchaseRequest."""

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema

PurchaseRequestStatus = Literal[
    "draft", "pending", "approved", "rejected", "completed", "cancelled"
]


# ---------------------------------------------------------------------------
# Línea inline
# ---------------------------------------------------------------------------

class PurchaseRequestLineInline(BaseModel):
    resource_id: UUID
    quantity: Decimal = Field(..., gt=0)
    supplier_id: UUID | None = None
    notes: str | None = None


# ---------------------------------------------------------------------------
# PurchaseRequest
# ---------------------------------------------------------------------------

class PurchaseRequestBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    needed_by: datetime | None = None
    notes: str | None = None


class PurchaseRequestCreate(PurchaseRequestBase):
    lines: list[PurchaseRequestLineInline] = Field(default_factory=list)


class PurchaseRequestUpdate(BaseModel):
    needed_by: datetime | None = None
    notes: str | None = None


class PurchaseRequestStatusUpdate(BaseModel):
    status: PurchaseRequestStatus


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class PurchaseRequestLineResponse(BaseModel):
    id: UUID
    resource_id: UUID
    resource_name: str
    quantity: Decimal
    quantity_received: Decimal = Decimal("0")
    supplier_id: UUID | None
    supplier_name: str | None
    notes: str | None


class PurchaseRequestResponse(PurchaseRequestBase):
    id: UUID
    status: str
    lines: list[PurchaseRequestLineResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PurchaseRequestListResponse(BaseSchema):
    items: list[PurchaseRequestResponse]
    total: int


# ---------------------------------------------------------------------------
# From Bundle
# ---------------------------------------------------------------------------

class PurchaseRequestFromBundleRequest(BaseModel):
    """Crea una solicitud desde un bundle explotado."""
    bundle_id: UUID
    multiplier: Decimal = Field(default=Decimal("1"), gt=0)
    code: str | None = Field(None, min_length=1, max_length=50)
    needed_by: datetime | None = None
    notes: str | None = None