import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import type {
  Bundle,
  BundleCreate,
  BundleExplodeResponse,
  BundleListResponse,
  BundleUpdate,
} from '../types/bundle'

export const bundleKeys = {
  all: ['bundles'] as const,
  list: (params?: Record<string, unknown>) =>
    ['bundles', 'list', params] as const,
  detail: (id: string) => ['bundles', 'detail', id] as const,
}

export function useBundles(
  params: { is_active?: boolean; search?: string; limit?: number } = {},
) {
  return useQuery({
    queryKey: bundleKeys.list(params),
    queryFn: async () => {
      const { data } = await api.get<BundleListResponse>('/bundles', { params })
      return data
    },
  })
}

export function useCreateBundle() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: BundleCreate) => {
      const { data } = await api.post<Bundle>('/bundles', payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: bundleKeys.all })
    },
  })
}

export function useUpdateBundle() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      id,
      payload,
    }: {
      id: string
      payload: BundleUpdate
    }) => {
      const { data } = await api.put<Bundle>(`/bundles/${id}`, payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: bundleKeys.all })
    },
  })
}

export function useDeleteBundle() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/bundles/${id}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: bundleKeys.all })
    },
  })
}

export function useAddBundleComponent() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      bundleId,
      componentType,
      resourceId,
      componentBundleId,
      quantity,
      wastePercent,
      season,
      notes,
    }: {
      bundleId: string
      componentType: 'resource' | 'bundle'
      resourceId?: string
      componentBundleId?: string
      quantity: string
      wastePercent?: string
      season?: string | null
      notes?: string | null
    }) => {
      const { data } = await api.post(`/bundles/${bundleId}/components`, {
        component_type: componentType,
        resource_id: resourceId ?? null,
        component_bundle_id: componentBundleId ?? null,
        quantity,
        waste_percent: wastePercent ?? '0',
        season: season ?? null,
        notes: notes ?? null,
      })
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: bundleKeys.all })
    },
  })
}

export function useUpdateBundleComponent() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      bundleId,
      componentType,
      resourceId,
      componentBundleId,
      quantity,
      wastePercent,
      season,
      notes,
    }: {
      bundleId: string
      componentType: 'resource' | 'bundle'
      resourceId?: string
      componentBundleId?: string
      quantity?: string
      wastePercent?: string
      season?: string | null
      notes?: string | null
    }) => {
      const identifier = componentType === 'resource' ? resourceId : componentBundleId
      const { data } = await api.put(
        `/bundles/${bundleId}/components/${identifier}`,
        { quantity, waste_percent: wastePercent, season, notes },
      )
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: bundleKeys.all })
    },
  })
}

export function useRemoveBundleComponent() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      bundleId,
      componentType,
      resourceId,
      componentBundleId,
    }: {
      bundleId: string
      componentType: 'resource' | 'bundle'
      resourceId?: string
      componentBundleId?: string
    }) => {
      const identifier = componentType === 'resource' ? resourceId : componentBundleId
      await api.delete(`/bundles/${bundleId}/components/${identifier}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: bundleKeys.all })
    },
  })
}

export function useExplodeBundle() {
  return useMutation({
    mutationFn: async ({
      bundleId,
      multiplier,
      season,
    }: {
      bundleId: string
      multiplier: string
      season?: string | null
    }) => {
      const { data } = await api.post<BundleExplodeResponse>(
        `/bundles/${bundleId}/explode`,
        null,
        { params: { multiplier, season } },
      )
      return data
    },
  })
}