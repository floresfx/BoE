from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field
from app.schemas.common import BaseSchema

class PlanItemAnnexCreate(BaseModel):
    annex_type: str = Field(..., description="quantity_adjustment, extra_resource, removed_resource, supplier_change, waste_change")
    resource_id: UUID | None = None
    quantity: Decimal | None = Field(None, description="Cantidad del ajuste o insumo extra")
    notes: str | None = None

class PlanItemAnnexResponse(BaseSchema):
    id: UUID
    production_order_id: UUID
    annex_type: str
    resource_id: UUID | None
    resource_name: str | None = None
    quantity: Decimal | None
    notes: str | None