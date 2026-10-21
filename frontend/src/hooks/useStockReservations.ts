import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'

export interface StockReservation {
  id: string
  warehouse_id: string
  resource_id: string
  quantity: string
  status: string
  reference: string | null
  notes: string | null
  needed_by: string | null
  created_at: string
  updated_at: string
}

export interface StockReservationCreate {
  warehouse_id: string
  resource_id: string
  quantity: string
  reference?: string | null
  notes?: string | null
  needed_by?: string | null
}

export function useStockReservations() {
  return useQuery({
    queryKey: ['stock-reservations'],
    queryFn: async () => {
      const { data } = await api.get<{ items: StockReservation[]; total: number }>('/stock/reservations')
      return data
    },
  })
}

export function useCreateStockReservation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: StockReservationCreate) => {
      const { data } = await api.post<StockReservation>('/stock/reservations', payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['stock-reservations'] })
    },
  })
}

export function useCancelStockReservation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await api.post<StockReservation>(`/stock/reservations/${id}/cancel`)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['stock-reservations'] })
    },
  })
}