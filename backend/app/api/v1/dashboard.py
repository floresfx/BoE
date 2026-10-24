"""Endpoints del dashboard (KPIs)."""

from decimal import Decimal
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant
from app.core.database import get_db
from app.models import (
    Bundle,
    ProductionOrder,
    PurchaseRequest,
    Resource,
    StockLot,
    Supplier,
    SupplierResource,
    Tenant,
)

from app.schemas.dashboard import ChartDataPoint, DashboardSummary

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

     # 7. Margen por Bundle (Top 5)
    # Asumimos un margen ficticio o calculado si tuvieras costos reales vs precio de venta
    bundles = db.query(Bundle).filter(Bundle.is_active == True).limit(5).all()
    bundle_margins = []
    for b in bundles:
        sale_price = b.sale_price or Decimal("0")
        # Aquí deberías calcular el costo real del bundle, por ahora simulamos un costo del 60% del precio
        estimated_cost = sale_price * Decimal("0.6")
        margin = sale_price - estimated_cost
        bundle_margins.append(ChartDataPoint(name=b.name[:15], value=margin))

    # 8. Top Proveedores (por cantidad de recursos ofrecidos)
    suppliers = (
        db.query(Supplier.name, func.count(SupplierResource.id).label("total"))
        .join(SupplierResource, Supplier.id == SupplierResource.supplier_id)
        .group_by(Supplier.name)
        .order_by(func.count(SupplierResource.id).desc())
        .limit(5)
        .all()
    )
    top_suppliers = [ChartDataPoint(name=s.name, value=Decimal(str(s.total))) for s in suppliers]

    # 9. Rotación de Inventario (Simulada con los últimos 6 meses de movimientos)
    # Como no tenemos una tabla de historial directa aquí, generamos datos de ejemplo para la gráfica
    inventory_rotation = [
        ChartDataPoint(name="May", value=Decimal("120")),
        ChartDataPoint(name="Jun", value=Decimal("150")),
        ChartDataPoint(name="Jul", value=Decimal("80")),
        ChartDataPoint(name="Ago", value=Decimal("200")),
        ChartDataPoint(name="Sep", value=Decimal("180")),
        ChartDataPoint(name="Oct", value=Decimal("250")),
    ]

    return DashboardSummary(
        total_resources=total_resources,
        total_inventory_value=total_inventory_value,
        total_stock_items=total_stock_items,
        pending_production_orders=pending_production_orders,
        pending_purchase_requests=pending_purchase_requests,
        expiring_soon_alerts=expiring_soon_alerts,
        bundle_margins=bundle_margins,
        top_suppliers=top_suppliers,
        inventory_rotation=inventory_rotation,
    )

    return DashboardSummary(
        total_resources=total_resources,
        total_inventory_value=total_inventory_value,
        total_stock_items=total_stock_items,
        pending_production_orders=pending_production_orders,
        pending_purchase_requests=pending_purchase_requests,
        expiring_soon_alerts=expiring_soon_alerts,
    )