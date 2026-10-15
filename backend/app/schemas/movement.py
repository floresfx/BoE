"""Schemas Pydantic para Movement."""

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema

MovementType = Literal["in", "out", "adjust", "loss"]


class MovementCreate(BaseModel):
    warehouse_id: UUID
    resource_id: UUID
    lot_code: str = Field(..., min_length=1, max_length=50)
    movement_type: MovementType
    quantity: Decimal = Field(..., gt=0)
    unit_cost: Decimal | None = Field(None, ge=0)
    expiration: datetime | None = None
    reference: str | None = Field(None, max_length=100)
    notes: str | None = None


class MovementResponse(BaseSchema):
    id: UUID
    warehouse_id: UUID
    resource_id: UUID
    lot_id: UUID | None
    movement_type: str
    quantity: Decimal
    unit_cost: Decimal | None
    reference: str | None
    notes: str | None
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class MovementListResponse(BaseSchema):
    items: list[MovementResponse]
    total: int