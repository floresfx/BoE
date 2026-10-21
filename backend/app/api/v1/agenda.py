"""Endpoints de la agenda (calendario)."""

from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.core.database import get_db
from app.models import (
    ProductionOrder,
    PurchaseRequest,
    Tenant,
)
from app.schemas.agenda import CalendarEvent, CalendarResponse

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("", response_model=CalendarResponse)
def get_calendar_events(
    from_date: datetime = Query(..., alias="from"),
    to_date: datetime = Query(..., alias="to"),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Obtiene los eventos del calendario en un rango de fechas."""
    events = []

    # 1. Órdenes de Producción
    prod_orders = (
        db.query(ProductionOrder)
        .filter(
            or_(
                ProductionOrder.start_date.between(from_date, to_date),
                ProductionOrder.end_date.between(from_date, to_date),
            )
        )
        .all()
    )

    for order in prod_orders:
        start = order.start_date or order.end_date
        end = order.end_date or order.start_date
        if start:
            events.append(
                CalendarEvent(
                    id=order.id,
                    title=f"Prod: {order.code}",
                    start=start,
                    end=end,
                    type="production_order",
                    status=order.status,
                    color="#3b82f6",  # Azul
                )
            )

    # 2. Solicitudes de Compra
    purchase_reqs = (
        db.query(PurchaseRequest)
        .filter(
            PurchaseRequest.needed_by.between(from_date, to_date),
            PurchaseRequest.status.notin_(["cancelled", "received"]),
        )
        .all()
    )

    for req in purchase_reqs:
        if req.needed_by:
            events.append(
                CalendarEvent(
                    id=req.id,
                    title=f"Compra: {req.code}",
                    start=req.needed_by,
                    end=None,
                    type="purchase_request",
                    status=req.status,
                    color="#f97316",  # Naranja
                )
            )

    events.sort(key=lambda x: x.start)
    return CalendarResponse(events=events)