export type CostingMethod = 'fifo' | 'lifo'

export interface CostingReportLine {
  resource_id: string
  resource_name: string
  total_quantity: string
  total_cost: string
  avg_unit_cost: string
}

export interface CostingReportResponse {
  method: CostingMethod
  from_date: string | null
  to_date: string | null
  lines: CostingReportLine[]
  total_quantity: string
  total_cost: string
}