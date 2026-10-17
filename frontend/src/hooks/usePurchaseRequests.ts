import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import type {
  PurchaseRequest,
  PurchaseRequestCreate,
  PurchaseRequestFromBundleRequest,
  PurchaseRequestListResponse,
  PurchaseRequestStatus,
  PurchaseRequestUpdate,
} from '../types/purchase_request'

export const purchaseRequestKeys = {
  all: ['purchase-requests'] as const,
  list: (params?: Record<string, unknown>) =>
    ['purchase-requests', 'list', params] as const,
  detail: (id: string) => ['purchase-requests', 'detail', id] as const,
}

export function usePurchaseRequests(
  params: { status?: PurchaseRequestStatus; search?: string } = {},
) {
  return useQuery({
    queryKey: purchaseRequestKeys.list(params),
    queryFn: async () => {
      const { data } = await api.get<PurchaseRequestListResponse>(
        '/purchase-requests',
        { params },
      )
      return data
    },
  })
}

export function usePurchaseRequest(id: string | null) {
  return useQuery({
    queryKey: purchaseRequestKeys.detail(id ?? ''),
    queryFn: async () => {
      const { data } = await api.get<PurchaseRequest>(
        `/purchase-requests/${id}`,
      )
      return data
    },
    enabled: Boolean(id),
  })
}

export function useCreatePurchaseRequest() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: PurchaseRequestCreate) => {
      const { data } = await api.post<PurchaseRequest>(
        '/purchase-requests',
        payload,
      )
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: purchaseRequestKeys.all })
    },
  })
}

export function useCreateFromBundle() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: PurchaseRequestFromBundleRequest) => {
      const { data } = await api.post<PurchaseRequest>(
        '/purchase-requests/from-bundle',
        payload,
      )
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: purchaseRequestKeys.all })
    },
  })
}

export function useUpdatePurchaseRequest() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      id,
      payload,
    }: {
      id: string
      payload: PurchaseRequestUpdate
    }) => {
      const { data } = await api.put<PurchaseRequest>(
        `/purchase-requests/${id}`,
        payload,
      )
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: purchaseRequestKeys.all })
    },
  })
}

export function useUpdateStatus() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      id,
      status,
    }: {
      id: string
      status: PurchaseRequestStatus
    }) => {
      const { data } = await api.put<PurchaseRequest>(
        `/purchase-requests/${id}/status`,
        { status },
      )
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: purchaseRequestKeys.all })
    },
  })
}

export function useDeletePurchaseRequest() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/purchase-requests/${id}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: purchaseRequestKeys.all })
    },
  })
}

export function useAddLine() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      requestId,
      resourceId,
      quantity,
      supplierId,
      notes,
    }: {
      requestId: string
      resourceId: string
      quantity: string
      supplierId?: string | null
      notes?: string | null
    }) => {
      const { data } = await api.post(
        `/purchase-requests/${requestId}/lines`,
        {
          resource_id: resourceId,
          quantity,
          supplier_id: supplierId ?? null,
          notes: notes ?? null,
        },
      )
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: purchaseRequestKeys.all })
    },
  })
}

export function useRemoveLine() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      requestId,
      lineId,
    }: {
      requestId: string
      lineId: string
    }) => {
      await api.delete(`/purchase-requests/${requestId}/lines/${lineId}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: purchaseRequestKeys.all })
    },
  })
}