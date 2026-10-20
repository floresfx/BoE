import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import type {
  TenantSettings,
  TenantSettingsUpdate,
  CatalogItem,
} from '../types/settings'

// --- CONFIGURACIÓN DEL TENANT ---

export function useTenantSettings() {
  return useQuery({
    queryKey: ['tenant-settings'],
    queryFn: async () => {
      const { data } = await api.get<TenantSettings>('/tenant/settings/')
      return data
    },
  })
}

export function useUpdateTenantSettings() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: TenantSettingsUpdate) => {
      const { data } = await api.put<TenantSettings>(
        '/tenant/settings/',
        payload,
      )
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['tenant-settings'] })
    },
  })
}

// --- CATÁLOGOS GLOBALES ---

export function useCatalogCurrencies() {
  return useQuery({
    queryKey: ['catalogs', 'currencies'],
    queryFn: async () => {
      const { data } = await api.get<CatalogItem[]>('/catalogs/currencies')
      return data
    },
  })
}

export function useCatalogUnits() {
  return useQuery({
    queryKey: ['catalogs', 'units'],
    queryFn: async () => {
      const { data } = await api.get<CatalogItem[]>('/catalogs/units')
      return data
    },
  })
}

export function useCatalogCategories() {
  return useQuery({
    queryKey: ['catalogs', 'categories'],
    queryFn: async () => {
      const { data } = await api.get<CatalogItem[]>('/catalogs/categories')
      return data
    },
  })
}

export function useCatalogAttributes() {
  return useQuery({
    queryKey: ['catalogs', 'attributes'],
    queryFn: async () => {
      const { data } = await api.get<CatalogItem[]>('/catalogs/attributes')
      return data
    },
  })
}