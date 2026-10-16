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
  params: { is_active?: boolean; search?: string } = {},
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
      resourceId,
      quantity,
      notes,
    }: {
      bundleId: string
      resourceId: string
      quantity: string
      notes?: string | null
    }) => {
      const { data } = await api.post(`/bundles/${bundleId}/components`, {
        resource_id: resourceId,
        quantity,
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
      resourceId,
      quantity,
      notes,
    }: {
      bundleId: string
      resourceId: string
      quantity?: string
      notes?: string | null
    }) => {
      const { data } = await api.put(
        `/bundles/${bundleId}/components/${resourceId}`,
        { quantity, notes },
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
      resourceId,
    }: {
      bundleId: string
      resourceId: string
    }) => {
      await api.delete(`/bundles/${bundleId}/components/${resourceId}`)
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
    }: {
      bundleId: string
      multiplier: string
    }) => {
      const { data } = await api.post<BundleExplodeResponse>(
        `/bundles/${bundleId}/explode`,
        null,
        { params: { multiplier } },
      )
      return data
    },
  })
}