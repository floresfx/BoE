import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import type { CostingReportResponse } from '../types/costing'

export function useCostingReport(params: {
  from_date?: string
  to_date?: string
}) {
  return useQuery({
    queryKey: ['costing-report', params],
    queryFn: async () => {
      const { data } = await api.get<CostingReportResponse>(
        '/inventory/costing/report',
        { params },
      )
      return data
    },
  })
}