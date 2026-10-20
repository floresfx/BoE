"""Endpoints de stock consolidado y alertas de caducidad."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.core.database import get_db
from app.models import Resource, StockLot, Tenant, Warehouse, Unit
from app.schemas.stock_lot import (
    ExpirationAlert,
    StockConsolidated,
    StockConsolidatedListResponse,
)

router = APIRouter(prefix="/stock", tags=["stock"])


@router.get("/consolidated", response_model=StockConsolidatedListResponse)
def stock_consolidated(
    warehouse_id: UUID | None = None,
    resource_id: UUID | None = None,
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Stock consolidado por (warehouse, resource) con nombres y unidad."""
    query = (
        db.query(
            StockLot.warehouse_id,
            Warehouse.name.label("warehouse_name"),
            StockLot.resource_id,
            Resource.name.label("resource_name"),
            Unit.symbol.label("unit_symbol"), # <--- NUEVO: Símbolo de la unidad
            func.sum(StockLot.quantity).label("total_quantity"),
            func.count(StockLot.id).label("lot_count"),
            func.min(StockLot.expiration).label("nearest_expiration"),
        )
        .join(Warehouse, StockLot.warehouse_id == Warehouse.id)
        .join(Resource, StockLot.resource_id == Resource.id)
        .join(Unit, Resource.base_unit_id == Unit.id) # <--- JOIN con Unit
    )
    if warehouse_id:
        query = query.filter(StockLot.warehouse_id == warehouse_id)
    if resource_id:
        query = query.filter(StockLot.resource_id == resource_id)
    
    query = query.group_by(
        StockLot.warehouse_id, 
        Warehouse.name, 
        StockLot.resource_id, 
        Resource.name,
        Unit.symbol # <--- Añadir a GROUP BY
    )

    rows = query.all()
    items = [
        StockConsolidated(
            warehouse_id=r.warehouse_id,
            warehouse_name=r.warehouse_name,
            resource_id=r.resource_id,
            resource_name=r.resource_name,
            unit_symbol=r.unit_symbol, # <--- Pasar al schema
            total_quantity=r.total_quantity or Decimal("0"),
            lot_count=r.lot_count,
            nearest_expiration=r.nearest_expiration,
        )
        for r in rows
    ]
    return StockConsolidatedListResponse(items=items, total=len(items))


@router.get("/expiration-alerts", response_model=list[ExpirationAlert])
def expiration_alerts(
    days_ahead: int = Query(30, ge=1, le=365),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Lotes con caducidad dentro de `days_ahead` días (o ya vencidos)."""
    limit_date = datetime.now(timezone.utc) + timedelta(days=days_ahead)
    lots = (
        db.query(StockLot)
        .filter(
            StockLot.expiration.isnot(None),
            StockLot.expiration <= limit_date,
            StockLot.quantity > 0,
        )
        .order_by(StockLot.expiration)
        .all()
    )
    now = datetime.now(timezone.utc)
    alerts = []
    for lot in lots:
        warehouse = db.query(Warehouse).filter(Warehouse.id == lot.warehouse_id).first()
        resource = db.query(Resource).filter(Resource.id == lot.resource_id).first()
        if not warehouse or not resource:
            continue
        exp = lot.expiration
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        days_until = (exp - now).days
        alerts.append(
            ExpirationAlert(
                lot_id=lot.id,
                warehouse_id=lot.warehouse_id,
                warehouse_name=warehouse.name,
                resource_id=lot.resource_id,
                resource_name=resource.name,
                lot_code=lot.lot_code,
                quantity=lot.quantity,
                expiration=lot.expiration,
                days_until_expiration=days_until,
            )
        )
    return alerts