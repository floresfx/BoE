"""Schemas para el Motor de Oportunidades (Matching Inverso)."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class OpportunityBottleneck(BaseModel):
    """El recurso que limita la producción de un bundle."""
    resource_id: UUID
    resource_name: str
    required_quantity: Decimal
    available_quantity: Decimal
    missing_quantity: Decimal


class OpportunityResponse(BaseModel):
    """Una oportunidad detectada."""
    bundle_id: UUID
    bundle_code: str
    bundle_name: str
    sale_price: Decimal | None
    estimated_cost: Decimal
    estimated_margin: Decimal | None
    estimated_margin_percent: Decimal | None
    coverage_percent: Decimal  # 0-100
    max_producible: Decimal  # cuántos bundles se pueden producir con el stock actual
    bottleneck: OpportunityBottleneck | None
    components_covered: int
    components_total: int


class OpportunityListResponse(BaseSchema):
    items: list[OpportunityResponse]
    total: int