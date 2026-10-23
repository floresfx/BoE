import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import type {
  Supplier,
  SupplierCreate,
  SupplierListResponse,
  SupplierUpdate,
} from '../types/supplier'

export const supplierKeys = {
  all: ['suppliers'] as const,
  list: (params?: Record<string, unknown>) =>
    ['suppliers', 'list', params] as const,
  detail: (id: string) => ['suppliers', 'detail', id] as const,
}

export function useSuppliers(
  params: { is_active?: boolean; search?: string; limit?: number } = {},
) {
  return useQuery({
    queryKey: supplierKeys.list(params),
    queryFn: async () => {
      const { data } = await api.get<SupplierListResponse>('/suppliers', {
        params,
      })
      return data
    },
  })
}

export function useSupplier(id: string | null) {
  return useQuery({
    queryKey: supplierKeys.detail(id ?? ''),
    queryFn: async () => {
      const { data } = await api.get<Supplier>(`/suppliers/${id}`)
      return data
    },
    enabled: Boolean(id),
  })
}

export function useCreateSupplier() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: SupplierCreate) => {
      const { data } = await api.post<Supplier>('/suppliers', payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: supplierKeys.all })
    },
  })
}

export function useUpdateSupplier() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      id,
      payload,
    }: {
      id: string
      payload: SupplierUpdate
    }) => {
      const { data } = await api.put<Supplier>(`/suppliers/${id}`, payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: supplierKeys.all })
    },
  })
}

export function useDeleteSupplier() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/suppliers/${id}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: supplierKeys.all })
    },
  })
}

export function useAddSupplierResource() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      supplierId,
      resourceId,
      notes,
    }: {
      supplierId: string
      resourceId: string
      notes?: string | null
    }) => {
      const { data } = await api.post(
        `/suppliers/${supplierId}/resources`,
        { resource_id: resourceId, notes: notes ?? null },
      )
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: supplierKeys.all })
    },
  })
}

export function useRemoveSupplierResource() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      supplierId,
      resourceId,
    }: {
      supplierId: string
      resourceId: string
    }) => {
      await api.delete(`/suppliers/${supplierId}/resources/${resourceId}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: supplierKeys.all })
    },
  })
}
export function useUpdateSupplierResource() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      supplierId,
      resourceId,
      payload,
    }: {
      supplierId: string
      resourceId: string
      payload: import('../types/supplier').SupplierResourceUpdate
    }) => {
      const { data } = await api.put(
        `/suppliers/${supplierId}/resources/${resourceId}`,
        payload,
      )
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: supplierKeys.all })
    },
  })
}