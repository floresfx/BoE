import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import type { ReceiveRequest, ReceiveResponse } from '../types/purchase_request'
import { purchaseRequestKeys } from './usePurchaseRequests'

export function useReceivePurchaseRequest() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      requestId,
      payload,
    }: {
      requestId: string
      payload: ReceiveRequest
    }) => {
      const { data } = await api.post<ReceiveResponse>(
        `/purchase-requests/${requestId}/receive`,
        payload,
      )
      return data
    },
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: purchaseRequestKeys.all })
      qc.invalidateQueries({
        queryKey: purchaseRequestKeys.detail(variables.requestId),
      })
    },
  })
}