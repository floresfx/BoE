import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import type {
  AdminAttribute,
  AdminCategory,
  AdminCountry,
  AdminCurrency,
  AdminDocumentType,
  AdminFeature,
  AdminPlan,
  AdminService,
  AdminTax,
  AdminUnit,
  AdminVertical,
} from '../types/admin'

// ---------------------------------------------------------------------------
// Query keys
// ---------------------------------------------------------------------------

export const adminKeys = {
  verticals: ['admin', 'verticals'] as const,
  features: ['admin', 'features'] as const,
  plans: ['admin', 'plans'] as const,
  attributes: ['admin', 'attributes'] as const,
  taxes: ['admin', 'taxes'] as const,
  services: ['admin', 'services'] as const,
  currencies: ['admin', 'currencies'] as const,
  units: ['admin', 'units'] as const,
  categories: ['admin', 'categories'] as const,
  countries: ['admin', 'countries'] as const,
  documentTypes: ['admin', 'document-types'] as const,
}

// ---------------------------------------------------------------------------
// Generic factory para list + create + update
// ---------------------------------------------------------------------------

function useAdminResource<T>(key: string, endpoint: string) {
  const qc = useQueryClient()

  const query = useQuery({
    queryKey: ['admin', key],
    queryFn: async () => {
      const { data } = await api.get<T[]>(`/admin/${endpoint}`)
      return data
    },
    staleTime: 1000 * 60 * 5,
  })

  const create = useMutation({
    mutationFn: async (payload: Record<string, unknown>) => {
      const { data } = await api.post<T>(`/admin/${endpoint}`, payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['admin', key] })
    },
  })

  const update = useMutation({
    mutationFn: async ({
      id,
      payload,
    }: {
      id: string
      payload: Record<string, unknown>
    }) => {
      const { data } = await api.put<T>(`/admin/${endpoint}/${id}`, payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['admin', key] })
    },
  })

  return { query, create, update }
}

// ---------------------------------------------------------------------------
// Hooks específicos
// ---------------------------------------------------------------------------

export function useAdminVerticals() {
  return useAdminResource<AdminVertical>('verticals', 'verticals')
}
export function useAdminFeatures() {
  return useAdminResource<AdminFeature>('features', 'features')
}
export function useAdminPlans() {
  return useAdminResource<AdminPlan>('plans', 'plans')
}
export function useAdminAttributes() {
  return useAdminResource<AdminAttribute>('attributes', 'attributes')
}
export function useAdminTaxes() {
  return useAdminResource<AdminTax>('taxes', 'taxes')
}
export function useAdminServices() {
  return useAdminResource<AdminService>('services', 'services')
}
export function useAdminCurrencies() {
  return useAdminResource<AdminCurrency>('currencies', 'currencies')
}
export function useAdminUnits() {
  return useAdminResource<AdminUnit>('units', 'units')
}
export function useAdminCategories() {
  return useAdminResource<AdminCategory>('categories', 'categories')
}
export function useAdminCountries() {
  return useAdminResource<AdminCountry>('countries', 'countries')
}
export function useAdminDocumentTypes() {
  return useAdminResource<AdminDocumentType>(
    'document-types',
    'document-types',
  )
}