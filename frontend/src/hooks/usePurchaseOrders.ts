import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import type {
  PurchaseOrder,
  PurchaseOrderListResponse,
} from '../types/purchase_order'

export const purchaseOrderKeys = {
  all: ['purchase-orders'] as const,
  list: () => ['purchase-orders', 'list'] as const,
}

export function usePurchaseOrders() {
  return useQuery({
    queryKey: purchaseOrderKeys.list(),
    queryFn: async () => {
      const { data } = await api.get<PurchaseOrderListResponse>('/purchase-orders')
      return data
    },
  })
}

export function useGenerateOrderFromQuote() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ requestId, quoteId }: { requestId: string; quoteId: string }) => {
      const { data } = await api.post<PurchaseOrder>('/purchase-orders/from-quote', null, {
        params: { request_id: requestId, quote_id: quoteId },
      })
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: purchaseOrderKeys.all })
      qc.refetchQueries({ queryKey: purchaseOrderKeys.all })
    },
  })
}

export function useConfirmOrder() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (orderId: string) => {
      const { data } = await api.post<PurchaseOrder>(
        `/purchase-orders/${orderId}/confirm`,
      )
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: purchaseOrderKeys.all })
      qc.refetchQueries({ queryKey: purchaseOrderKeys.all })  // <--- AÑADIR
    },
  })
}

export function useReceiveOrder() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      orderId,
      warehouseId,
    }: {
      orderId: string
      warehouseId: string
    }) => {
      const { data } = await api.post<PurchaseOrder>(
        `/purchase-orders/${orderId}/receive`,
        null,
        { params: { warehouse_id: warehouseId } },
      )
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: purchaseOrderKeys.all })
      qc.refetchQueries({ queryKey: purchaseOrderKeys.all })  // <--- AÑADIR
    },
  })
}