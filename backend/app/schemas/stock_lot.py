"""Schemas Pydantic para StockLot."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class StockLotResponse(BaseSchema):
    id: UUID
    warehouse_id: UUID
    resource_id: UUID
    lot_code: str
    quantity: Decimal
    expiration: datetime | None
    unit_cost: Decimal | None
    received_at: datetime
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class StockLotListResponse(BaseSchema):
    items: list[StockLotResponse]
    total: int


class StockConsolidated(BaseSchema):
    """Vista consolidada de stock: un recurso en un warehouse."""
    warehouse_id: UUID
    warehouse_name: str
    resource_id: UUID
    resource_name: str
    unit_symbol: str
    total_quantity: Decimal
    lot_count: int
    nearest_expiration: datetime | None


class StockConsolidatedListResponse(BaseSchema):
    items: list[StockConsolidated]
    total: int


class ExpirationAlert(BaseSchema):
    """Alerta de caducidad próxima o pasada."""
    lot_id: UUID
    warehouse_id: UUID
    warehouse_name: str
    resource_id: UUID
    resource_name: str
    lot_code: str
    quantity: Decimal
    expiration: datetime
    days_until_expiration: int