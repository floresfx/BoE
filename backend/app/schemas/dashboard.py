from decimal import Decimal
from pydantic import BaseModel

class ChartDataPoint(BaseModel):
    name: str
    value: Decimal


class DashboardSummary(BaseModel):
    """Resumen de KPIs para el dashboard."""
    total_resources: int
    total_inventory_value: Decimal
    total_stock_items: Decimal
    pending_production_orders: int
    pending_purchase_requests: int
    expiring_soon_alerts: int
    bundle_margins: list[ChartDataPoint] = []
    top_suppliers: list[ChartDataPoint] = []
    inventory_rotation: list[ChartDataPoint] = []