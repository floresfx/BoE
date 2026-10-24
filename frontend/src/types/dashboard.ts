export interface ChartDataPoint {
  name: string;
  value: number;
}

export interface DashboardSummary {
  total_resources: number;
  total_inventory_value: string;
  total_stock_items: string;
  pending_production_orders: number;
  pending_purchase_requests: number;
  expiring_soon_alerts: number;
  bundle_margins: ChartDataPoint[];
  top_suppliers: ChartDataPoint[];
  inventory_rotation: ChartDataPoint[];
}