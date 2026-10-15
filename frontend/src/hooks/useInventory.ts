import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import type {
  ExpirationAlert,
  Movement,
  MovementCreate,
  MovementListResponse,
  StockConsolidatedListResponse,
  Warehouse,
  WarehouseCreate,
  WarehouseListResponse,
  WarehouseUpdate,
} from '../types/inventory'

export const inventoryKeys = {
  warehouses: ['warehouses'] as const,
  movements: (params?: Record<string, unknown>) =>
    ['movements', params] as const,
  stockConsolidated: (params?: Record<string, unknown>) =>
    ['stock-consolidated', params] as const,
  expirationAlerts: (days: number) => ['expiration-alerts', days] as const,
}

// ---------------------------------------------------------------------------
// Warehouses
// ---------------------------------------------------------------------------

export function useWarehouses(params: { is_active?: boolean; search?: string } = {}) {
  return useQuery({
    queryKey: [...inventoryKeys.warehouses, params],
    queryFn: async () => {
      const { data } = await api.get<WarehouseListResponse>('/warehouses', {
        params,
      })
      return data
    },
  })
}

export function useCreateWarehouse() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: WarehouseCreate) => {
      const { data } = await api.post<Warehouse>('/warehouses', payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: inventoryKeys.warehouses })
    },
  })
}

export function useUpdateWarehouse() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      id,
      payload,
    }: {
      id: string
      payload: WarehouseUpdate
    }) => {
      const { data } = await api.put<Warehouse>(`/warehouses/${id}`, payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: inventoryKeys.warehouses })
    },
  })
}

// ---------------------------------------------------------------------------
// Movements
// ---------------------------------------------------------------------------

export function useMovements(params: Record<string, unknown> = {}) {
  return useQuery({
    queryKey: inventoryKeys.movements(params),
    queryFn: async () => {
      const { data } = await api.get<MovementListResponse>('/movements', {
        params,
      })
      return data
    },
  })
}

export function useCreateMovement() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: MovementCreate) => {
      const { data } = await api.post<Movement>('/movements', payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['movements'] })
      qc.invalidateQueries({ queryKey: ['stock-consolidated'] })
      qc.invalidateQueries({ queryKey: ['expiration-alerts'] })
    },
  })
}

// ---------------------------------------------------------------------------
// Stock
// ---------------------------------------------------------------------------

export function useStockConsolidated(params: Record<string, unknown> = {}) {
  return useQuery({
    queryKey: inventoryKeys.stockConsolidated(params),
    queryFn: async () => {
      const { data } = await api.get<StockConsolidatedListResponse>(
        '/stock/consolidated',
        { params },
      )
      return data
    },
  })
}

export function useExpirationAlerts(daysAhead = 30) {
  return useQuery({
    queryKey: inventoryKeys.expirationAlerts(daysAhead),
    queryFn: async () => {
      const { data } = await api.get<ExpirationAlert[]>(
        '/stock/expiration-alerts',
        { params: { days_ahead: daysAhead } },
      )
      return data
    },
  })
}