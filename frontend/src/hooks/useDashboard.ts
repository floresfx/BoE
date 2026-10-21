import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'

export interface DashboardSummary {
  total_resources: number
  total_inventory_value: string
  total_stock_items: string
  pending_production_orders: number
  pending_purchase_requests: number
  expiring_soon_alerts: number
}

export function useDashboardSummary() {
  return useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: async () => {
      const { data } = await api.get<DashboardSummary>('/dashboard/summary')
      return data
    },
  })
}