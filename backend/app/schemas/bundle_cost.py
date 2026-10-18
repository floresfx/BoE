"""Schemas Pydantic para el Cálculo de Costos de Bundle."""

from decimal import Decimal
from uuid import UUID

from app.schemas.common import BaseSchema


class BundleCostLine(BaseSchema):
    """Línea de costo de un componente del bundle."""

    resource_id: UUID
    resource_name: str
    quantity: Decimal
    unit_cost: Decimal
    line_cost: Decimal
    waste_percent: Decimal
    waste_cost: Decimal
    supplier_used: str | None


class BundleCostBreakdown(BaseSchema):
    """Desglose de costos del bundle."""

    materials_cost: Decimal
    waste_cost: Decimal
    labor_cost: Decimal
    overhead_cost: Decimal


class BundleCostResponse(BaseSchema):
    """Respuesta del cálculo de costos de un bundle."""

    bundle_id: UUID
    bundle_name: str
    multiplier: Decimal
    total_cost: Decimal
    currency_code: str
    breakdown: BundleCostBreakdown
    lines: list[BundleCostLine]