import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import { productionKeys } from './useProduction'

export interface PlanItemAnnexPayload {
  annex_type: string // 'quantity_adjustment', 'extra_resource', etc.
  resource_id?: string
  quantity?: number
  notes?: string
}

export function useCreateAnnex() {
  const qc = useQueryClient()

  return useMutation({
    mutationFn: async ({ orderId, payload }: { orderId: string; payload: PlanItemAnnexPayload }) => {
      const { data } = await api.post(
        `/production/orders/${orderId}/annexes`,
        payload,
      )
      return data
    },
    onSuccess: () => {
      // Refresca el Kanban para que se vea el nuevo anexo
      qc.invalidateQueries({ queryKey: productionKeys.orders, exact: false })
      qc.refetchQueries({ queryKey: productionKeys.orders, exact: false })
    },
  })
}