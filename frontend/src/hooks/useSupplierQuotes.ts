import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import type {
  PurchaseRequest,
  SupplierQuote,
  SupplierQuoteCreate,
  SupplierQuoteListResponse,
  SupplierQuoteUpdate,
} from '../types/purchase_request'
import { purchaseRequestKeys } from './usePurchaseRequests'

export const quoteKeys = {
  all: ['supplier-quotes'] as const,
  list: (requestId: string) =>
    ['supplier-quotes', 'list', requestId] as const,
}

export function useSupplierQuotes(requestId: string | null) {
  return useQuery({
    queryKey: quoteKeys.list(requestId ?? ''),
    queryFn: async () => {
      const { data } = await api.get<SupplierQuoteListResponse>(
        `/purchase-requests/${requestId}/quotes`,
      )
      return data
    },
    enabled: Boolean(requestId),
  })
}

export function useSendToSuppliers() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (requestId: string) => {
      const { data } = await api.post<PurchaseRequest>(
        `/purchase-requests/${requestId}/send`,
      )
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: purchaseRequestKeys.all })
    },
  })
}

export function useCreateSupplierQuote() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      requestId,
      payload,
    }: {
      requestId: string
      payload: SupplierQuoteCreate
    }) => {
      const { data } = await api.post<SupplierQuote>(
        `/purchase-requests/${requestId}/quotes`,
        payload,
      )
      return data
    },
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: quoteKeys.all })
      qc.invalidateQueries({
        queryKey: quoteKeys.list(variables.requestId),
      })
      qc.invalidateQueries({ queryKey: purchaseRequestKeys.all })
    },
  })
}

export function useUpdateSupplierQuote() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      requestId,
      quoteId,
      payload,
    }: {
      requestId: string
      quoteId: string
      payload: SupplierQuoteUpdate
    }) => {
      const { data } = await api.put<SupplierQuote>(
        `/purchase-requests/${requestId}/quotes/${quoteId}`,
        payload,
      )
      return data
    },
    onSuccess: (_, variables) => {
      qc.invalidateQueries({
        queryKey: quoteKeys.list(variables.requestId),
      })
    },
  })
}

export function useDeleteSupplierQuote() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      requestId,
      quoteId,
    }: {
      requestId: string
      quoteId: string
    }) => {
      await api.delete(
        `/purchase-requests/${requestId}/quotes/${quoteId}`,
      )
    },
    onSuccess: (_, variables) => {
      qc.invalidateQueries({
        queryKey: quoteKeys.list(variables.requestId),
      })
    },
  })
}

export function useSelectSupplierQuote() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      requestId,
      quoteId,
    }: {
      requestId: string
      quoteId: string
    }) => {
      const { data } = await api.post<SupplierQuote>(
        `/purchase-requests/${requestId}/quotes/${quoteId}/select`,
      )
      return data
    },
    onSuccess: (_, variables) => {
      qc.invalidateQueries({
        queryKey: quoteKeys.list(variables.requestId),
      })
      qc.invalidateQueries({ queryKey: purchaseRequestKeys.all })
    },
  })
}