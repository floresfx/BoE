"""Schemas para producción (MPS)."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema
# Importamos la respuesta de anexos arriba para evitar el NameError
from app.schemas.production_annex import PlanItemAnnexResponse 


# --- Production Plans ---

class ProductionPlanCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    target_date: datetime | None = None


class ProductionPlanUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    target_date: datetime | None = None
    status: str | None = None


class ProductionPlanResponse(BaseSchema):
    id: UUID
    code: str
    name: str
    description: str | None
    status: str
    target_date: datetime | None
    created_at: datetime
    updated_at: datetime


class ProductionPlanListResponse(BaseSchema):
    items: list[ProductionPlanResponse]
    total: int


# --- Production Orders ---

class ProductionOrderCreate(BaseModel):
    code: str | None = None
    plan_id: UUID | None = None
    bundle_id: UUID
    quantity: Decimal = Field(..., gt=0)
    notes: str | None = None


class ProductionOrderResponse(BaseSchema):
    id: UUID
    code: str
    plan_id: UUID | None
    bundle_id: UUID
    bundle_name: str
    quantity: Decimal
    status: str
    start_date: datetime | None
    end_date: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    exception_type: str | None = None
    exception_notes: str | None = None
    annexes: list[PlanItemAnnexResponse] = []


class ProductionOrderListResponse(BaseSchema):
    items: list[ProductionOrderResponse]
    total: int


# --- Generate Orders from Plan ---

class GenerateOrdersRequest(BaseModel):
    items: list[dict]  # [{"bundle_id": uuid, "quantity": decimal}]