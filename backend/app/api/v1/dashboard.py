"""Endpoints del dashboard (KPIs)."""

from decimal import Decimal
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.core.database import get_db
from app.models import (
    ProductionOrder,
    PurchaseRequest,
    Resource,
    StockLot,
    Tenant,
)
from app.schemas.dashboard import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Obtiene un resumen de KPIs para el dashboard."""
    
    # 1. Total de recursos activos
    total_resources = (
        db.query(func.count(Resource.id))
        .filter(Resource.is_active == True)
        .scalar() or 0
    )

    # 2. Valor total del inventario (cantidad * costo_unitario por lote)
    total_inventory_value = (
        db.query(func.sum(StockLot.quantity * StockLot.unit_cost))
        .scalar() or Decimal("0")
    )

    # 3. Total de items en stock (suma simple de cantidades)
    total_stock_items = (
        db.query(func.sum(StockLot.quantity)).scalar() or Decimal("0")
    )

    # 4. Órdenes de producción pendientes (draft o in_progress)
    pending_production_orders = (
        db.query(func.count(ProductionOrder.id))
        .filter(ProductionOrder.status.in_(["draft", "in_progress"]))
        .scalar() or 0
    )

    # 5. Solicitudes de compra pendientes (draft o sent)
    pending_purchase_requests = (
        db.query(func.count(PurchaseRequest.id))
        .filter(PurchaseRequest.status.in_(["draft", "sent"]))
        .scalar() or 0
    )

    # 6. Alertas de caducidad (lotes que vencen en los próximos 30 días)
    limit_date = datetime.now(timezone.utc) + timedelta(days=30)
    expiring_soon_alerts = (
        db.query(func.count(StockLot.id))
        .filter(
            StockLot.expiration.isnot(None),
            StockLot.expiration <= limit_date,
            StockLot.quantity > 0,
        )
        .scalar() or 0
    )

    return DashboardSummary(
        total_resources=total_resources,
        total_inventory_value=total_inventory_value,
        total_stock_items=total_stock_items,
        pending_production_orders=pending_production_orders,
        pending_purchase_requests=pending_purchase_requests,
        expiring_soon_alerts=expiring_soon_alerts,
    )