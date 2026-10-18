import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import type { BundleCostResponse } from '../types/bundle_cost'

export function useBundleCost(bundleId: string, multiplier = 1) {
  return useQuery({
    queryKey: ['bundle-cost', bundleId, multiplier],
    queryFn: async () => {
      const { data } = await api.get<BundleCostResponse>(
        `/bundles/${bundleId}/cost`,
        { params: { multiplier } },
      )
      return data
    },
    enabled: !!bundleId,
  })
}