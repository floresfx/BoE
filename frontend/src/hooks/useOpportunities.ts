import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'

export interface OpportunityBottleneck {
  resource_id: string
  resource_name: string
  required_quantity: string
  available_quantity: string
  missing_quantity: string
}

export interface Opportunity {
  bundle_id: string
  bundle_code: string
  bundle_name: string
  sale_price: string | null
  estimated_cost: string
  estimated_margin: string | null
  estimated_margin_percent: string | null
  coverage_percent: string
  max_producible: string
  bottleneck: OpportunityBottleneck | null
  components_covered: number
  components_total: number
}

export interface OpportunityListResponse {
  items: Opportunity[]
  total: number
}

export function useOpportunities(minCoverage: number = 50) {
  return useQuery({
    queryKey: ['opportunities', minCoverage],
    queryFn: async () => {
      const { data } = await api.get<OpportunityListResponse>('/opportunities', {
        params: { min_coverage: minCoverage },
      })
      return data
    },
  })
}