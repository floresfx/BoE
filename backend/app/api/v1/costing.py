"""Endpoints de costeo de inventario."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.api.permissions import require_permission
from app.core.database import get_db
from app.models import Movement, Resource, Tenant
from app.schemas.costing import CostingReportResponse, CostingReportLine

router = APIRouter(prefix="/inventory/costing", tags=["costing"])


@router.get(
    "/report",
    response_model=CostingReportResponse,
    dependencies=[Depends(require_permission("inventory", "ver_costos"))],
)
def costing_report(
    from_date: datetime | None = Query(None),
    to_date: datetime | None = Query(None),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Reporte de costo de ventas (COGS) en un período.

    Suma los movimientos `out` y `loss` con su costo real (FIFO/LIFO).
    """
    query = db.query(
        Movement.resource_id,
        func.sum(Movement.quantity).label("total_quantity"),
        func.sum(Movement.quantity * Movement.unit_cost).label("total_cost"),
    ).filter(
        Movement.movement_type.in_(["out", "loss"])
    )

    if from_date:
        query = query.filter(Movement.created_at >= from_date)
    if to_date:
        query = query.filter(Movement.created_at <= to_date)

    query = query.group_by(Movement.resource_id)

    rows = query.all()

    lines = []
    total_quantity = Decimal("0")
    total_cost = Decimal("0")

    for row in rows:
        resource = db.query(Resource).filter(Resource.id == row.resource_id).first()
        qty = row.total_quantity or Decimal("0")
        cost = row.total_cost or Decimal("0")
        lines.append(
            CostingReportLine(
                resource_id=row.resource_id,
                resource_name=resource.name if resource else "",
                total_quantity=qty,
                total_cost=cost,
                avg_unit_cost=cost / qty if qty > 0 else Decimal("0"),
            )
        )
        total_quantity += qty
        total_cost += cost

    return CostingReportResponse(
        method=current_tenant.inventory_costing_method or "fifo",
        from_date=from_date,
        to_date=to_date,
        lines=lines,
        total_quantity=total_quantity,
        total_cost=total_cost,
    )