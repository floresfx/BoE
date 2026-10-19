import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import type {
  TenantSettings,
  TenantSettingsUpdate,
} from '../types/settings'

export function useTenantSettings(tenantId: string | null) {
  return useQuery({
    queryKey: ['tenant-settings', tenantId],
    queryFn: async () => {
      const { data } = await api.get<TenantSettings>(
        `/tenants/${tenantId}`,
      )
      return data
    },
    enabled: !!tenantId,
  })
}

export function useUpdateTenantSettings() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: TenantSettingsUpdate) => {
      const { data } = await api.put<TenantSettings>(
        '/tenants/settings',
        payload,
      )
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['tenant-settings'] })
      qc.invalidateQueries({ queryKey: ['auth', 'me'] })
    },
  })
}