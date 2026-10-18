import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import { useAuth } from './useAuth'

export interface Permission {
  id: string
  module: string
  action: string
  description: string | null
}

/**
 * Hook que devuelve los permisos del usuario actual.
 *
 * Uso:
 *   const { can, permissions, isLoading } = usePermissions()
 *   if (can('resource', 'crear')) { ... }
 */
export function usePermissions() {
  const { user } = useAuth()

  const { data, isLoading, error } = useQuery({
    queryKey: ['permissions', 'me', user?.id],
    queryFn: async () => {
      // El backend debe exponer GET /api/v1/auth/me/permissions
      const { data } = await api.get<Permission[]>('/auth/me/permissions')
      return data
    },
    enabled: !!user,
    staleTime: 1000 * 60 * 5, // 5 min de caché
  })

  const permissions = data ?? []

  const can = (module: string, action: string): boolean => {
    if (isLoading) return false
    return permissions.some((p) => p.module === module && p.action === action)
  }

  return { permissions, can, isLoading, error }
}