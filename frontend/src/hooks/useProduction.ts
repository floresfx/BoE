import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import type {
  ProductionOrder,
  ProductionOrderCreate,
  ProductionOrderListResponse,
  ProductionPlan,
  ProductionPlanListResponse,
} from '../types/production'

export const productionKeys = {
  plans: ['production-plans'] as const,
  planList: (params?: Record<string, unknown>) =>
    ['production-plans', 'list', params] as const,
  orders: ['production-orders'] as const,
  orderList: (params?: Record<string, unknown>) =>
    ['production-orders', 'list', params] as const,
  orderDetail: (id: string) => ['production-orders', 'detail', id] as const,
}

// --- Plans ---

export function useProductionPlans() {
  return useQuery({
    queryKey: productionKeys.plans,
    queryFn: async () => {
      const { data } = await api.get<ProductionPlanListResponse>(
        '/production/plans',
      )
      return data
    },
  })
}

export function useCreateProductionPlan() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: {
      code: string
      name: string
      description?: string | null
      target_date?: string | null
    }) => {
      const { data } = await api.post<ProductionPlan>(
        '/production/plans',
        payload,
      )
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: productionKeys.plans })
    },
  })
}

// --- Orders ---

export function useProductionOrders() {
  return useQuery({
    queryKey: productionKeys.orders,
    queryFn: async () => {
      const { data } = await api.get<ProductionOrderListResponse>(
        '/production/orders',
      )
      return data
    },
    refetchOnMount: 'always',
    refetchOnWindowFocus: true,
    staleTime: 0,
  })
}

export function useCreateProductionOrder() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: ProductionOrderCreate) => {
      const { data } = await api.post<ProductionOrder>(
        '/production/orders',
        payload,
      )
      return data
    },
    onSettled: async () => {
      await qc.invalidateQueries({ queryKey: productionKeys.orders })
    },
  })
}

export function useStartProductionOrder() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (orderId: string) => {
      const { data } = await api.post<ProductionOrder>(
        `/production/orders/${orderId}/start`,
      )
      return data
    },
    onSuccess: async () => {
      // Forzar refetch inmediato
      await qc.refetchQueries({ queryKey: productionKeys.orders })
    },
  })
}

export function useCompleteProductionOrder() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (orderId: string) => {
      const { data } = await api.post<ProductionOrder>(
        `/production/orders/${orderId}/complete`,
      )
      return data
    },
    onSuccess: async () => {
      await qc.refetchQueries({ queryKey: productionKeys.orders })
    },
  })
}

export function useUpdateProductionOrderStatus() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      orderId,
      status,
    }: {
      orderId: string
      status: string
    }) => {
      const { data } = await api.put<ProductionOrder>(
        `/production/orders/${orderId}/status`,
        { status },
      )
      return data
    },
    onSuccess: async () => {
      await qc.refetchQueries({ queryKey: productionKeys.orders })
    },
  })
}