from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class StockReservationCreate(BaseModel):
    warehouse_id: UUID
    resource_id: UUID
    quantity: Decimal = Field(..., gt=0)
    reference: str | None = None
    notes: str | None = None
    needed_by: datetime | None = None


class StockReservationResponse(BaseSchema):
    id: UUID
    warehouse_id: UUID
    resource_id: UUID
    quantity: Decimal
    status: str
    reference: str | None
    notes: str | None
    needed_by: datetime | None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class StockReservationListResponse(BaseSchema):
    items: list[StockReservationResponse]
    total: int