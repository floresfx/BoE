import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import { productionKeys } from './useProduction' // <-- Importamos las keys reales de tu proyecto

export interface MarkExceptionPayload {
  exception_type: 'not_executed' | 'partial' | 'with_deviation'
  notes?: string
  actual_quantity?: number
}

export interface ExceptionResponse {
  order_id: string
  order_code: string
  exception_type: string
  message: string
  restored_quantity: number
}

export function useMarkException() {
  const qc = useQueryClient()

  return useMutation({
    mutationFn: async ({ orderId, payload }: { orderId: string; payload: MarkExceptionPayload }) => {
      const { data } = await api.post<ExceptionResponse>(
        `/production/orders/${orderId}/exception`,
        payload,
      )
      return data
    },
   onSuccess: () => {
      // El 'true' al final fuerza a que todas las sub-queries (list, detail) se invaliden
      qc.invalidateQueries({ queryKey: productionKeys.orders, exact: false })
      qc.refetchQueries({ queryKey: productionKeys.orders, exact: false })
    },
  })
}