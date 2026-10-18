"""Schemas para cotizaciones de proveedores."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class SupplierQuoteCreate(BaseModel):
    """Crear una cotización."""

    line_id: UUID
    supplier_id: UUID
    unit_price: Decimal = Field(..., gt=0)
    currency_code: str = Field(default="USD", max_length=10)
    lead_time_days: int = Field(default=0, ge=0)
    valid_until: datetime | None = None
    notes: str | None = None


class SupplierQuoteUpdate(BaseModel):
    """Actualizar una cotización (solo si está pending)."""

    unit_price: Decimal | None = Field(None, gt=0)
    currency_code: str | None = Field(None, max_length=10)
    lead_time_days: int | None = Field(None, ge=0)
    valid_until: datetime | None = None
    notes: str | None = None


class SupplierQuoteResponse(BaseSchema):
    """Respuesta de una cotización."""

    id: UUID
    request_id: UUID
    line_id: UUID
    supplier_id: UUID
    supplier_name: str
    unit_price: Decimal
    currency_code: str
    lead_time_days: int
    valid_until: datetime | None
    notes: str | None
    status: str
    is_selected: bool
    created_at: datetime
    updated_at: datetime


class SupplierQuoteListResponse(BaseSchema):
    """Lista de cotizaciones."""

    items: list[SupplierQuoteResponse]
    total: int