export interface BundleCostLine {
  resource_id: string
  resource_name: string
  quantity: string
  unit_cost: string
  line_cost: string
  waste_percent: string
  waste_cost: string
  supplier_used: string | null
}

export interface BundleCostBreakdown {
  materials_cost: string
  waste_cost: string
  labor_cost: string
  overhead_cost: string
}

export interface BundleCostResponse {
  bundle_id: string
  bundle_name: string
  multiplier: string
  total_cost: string
  currency_code: string
  breakdown: BundleCostBreakdown
  lines: BundleCostLine[]
}