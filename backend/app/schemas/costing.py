"""Schemas para el reporte de costeo."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.schemas.common import BaseSchema


class CostingReportLine(BaseSchema):
    """Línea del reporte de costeo."""

    resource_id: UUID
    resource_name: str
    total_quantity: Decimal
    total_cost: Decimal
    avg_unit_cost: Decimal


class CostingReportResponse(BaseSchema):
    """Respuesta del reporte de costeo."""

    method: str
    from_date: datetime | None
    to_date: datetime | None
    lines: list[CostingReportLine]
    total_quantity: Decimal
    total_cost: Decimal