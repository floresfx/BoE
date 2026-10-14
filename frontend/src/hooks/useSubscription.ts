import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import type {
  PlanSummary,
  SelectPlanResponse,
  SubscriptionInfo,
} from '../types/auth'

export const subscriptionKeys = {
  plans: ['subscription', 'plans'] as const,
  current: ['subscription', 'current'] as const,
}

// ---------------------------------------------------------------------------
// Planes disponibles (público)
// ---------------------------------------------------------------------------

export function useAvailablePlans() {
  return useQuery({
    queryKey: subscriptionKeys.plans,
    queryFn: async () => {
      const { data } = await api.get<PlanSummary[]>('/subscription/plans')
      return data
    },
    staleTime: 1000 * 60 * 30, // 30 min
  })
}

// ---------------------------------------------------------------------------
// Suscripción actual del tenant
// ---------------------------------------------------------------------------

export function useCurrentSubscription(enabled = true) {
  return useQuery({
    queryKey: subscriptionKeys.current,
    queryFn: async () => {
      const { data } = await api.get<SubscriptionInfo>('/subscription/current')
      return data
    },
    enabled,
    staleTime: 1000 * 60 * 5,
  })
}

// ---------------------------------------------------------------------------
// Seleccionar plan
// ---------------------------------------------------------------------------

export function useSelectPlan() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (planId: string) => {
      const { data } = await api.post<SelectPlanResponse>(
        '/subscription/select-plan',
        { plan_id: planId },
      )
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: subscriptionKeys.current })
    },
  })
}