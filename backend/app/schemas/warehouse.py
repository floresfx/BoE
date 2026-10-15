"""Schemas Pydantic para Warehouse."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class WarehouseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    address: str | None = None
    is_active: bool = True


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    address: str | None = None
    is_active: bool | None = None


class WarehouseResponse(WarehouseBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class WarehouseListResponse(BaseSchema):
    items: list[WarehouseResponse]
    total: int