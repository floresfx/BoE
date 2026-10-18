import { useMutation } from '@tanstack/react-query'
import { api } from '../lib/api'
import type {
  AvailabilityResponse,
  BundleAvailabilityResponse,
} from '../types/availability'

export function useCheckAvailability() {
  return useMutation({
    mutationFn: async ({
      resourceId,
      quantity,
    }: {
      resourceId: string
      quantity: number
    }) => {
      const { data } = await api.post<AvailabilityResponse>(
        '/availability/check',
        { resource_id: resourceId, quantity },
      )
      return data
    },
  })
}

export function useCheckBundleAvailability() {
  return useMutation({
    mutationFn: async ({
      bundleId,
      multiplier,
    }: {
      bundleId: string
      multiplier: number
    }) => {
      const { data } = await api.post<BundleAvailabilityResponse>(
        '/availability/check-bundle',
        { bundle_id: bundleId, multiplier },
      )
      return data
    },
  })
}