"""Schemas para órdenes de compra."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class PurchaseOrderLineResponse(BaseSchema):
    """Línea de una orden de compra."""

    id: UUID
    resource_id: UUID
    resource_name: str
    quantity: Decimal
    unit_price: Decimal
    subtotal: Decimal


class PurchaseOrderResponse(BaseSchema):
    """Respuesta de una orden de compra."""

    id: UUID
    code: str
    request_id: UUID | None
    supplier_id: UUID
    supplier_name: str
    status: str
    total: Decimal
    currency_code: str
    expected_delivery: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    lines: list[PurchaseOrderLineResponse]


class PurchaseOrderListResponse(BaseSchema):
    """Lista de órdenes de compra."""

    items: list[PurchaseOrderResponse]
    total: int