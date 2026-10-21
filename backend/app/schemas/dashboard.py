from decimal import Decimal
from pydantic import BaseModel


class DashboardSummary(BaseModel):
    """Resumen de KPIs para el dashboard."""
    total_resources: int
    total_inventory_value: Decimal
    total_stock_items: Decimal  # Suma de todas las cantidades (sin importar unidad)
    pending_production_orders: int
    pending_purchase_requests: int
    expiring_soon_alerts: int