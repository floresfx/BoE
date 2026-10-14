import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import type {
  Attribute,
  Category,
  Subcategory,
  Tax,
  Unit,
} from '../types/catalogs'

// ---------------------------------------------------------------------------
// Query keys
// ---------------------------------------------------------------------------

export const catalogKeys = {
  units: ['catalogs', 'units'] as const,
  categories: ['catalogs', 'categories'] as const,
  subcategories: (categoryId?: string) =>
    ['catalogs', 'subcategories', categoryId] as const,
  attributes: ['catalogs', 'attributes'] as const,
  taxes: ['catalogs', 'taxes'] as const,
}

// ---------------------------------------------------------------------------
// Hooks
// ---------------------------------------------------------------------------

export function useUnits() {
  return useQuery({
    queryKey: catalogKeys.units,
    queryFn: async () => {
      const { data } = await api.get<Unit[]>('/catalogs/units')
      return data
    },
    staleTime: 1000 * 60 * 60, // 1 hora
  })
}

export function useCategories() {
  return useQuery({
    queryKey: catalogKeys.categories,
    queryFn: async () => {
      const { data } = await api.get<Category[]>('/catalogs/categories')
      return data
    },
    staleTime: 1000 * 60 * 60,
  })
}

export function useSubcategories(categoryId?: string) {
  return useQuery({
    queryKey: catalogKeys.subcategories(categoryId),
    queryFn: async () => {
      const { data } = await api.get<Subcategory[]>('/catalogs/subcategories', {
        params: categoryId ? { category_id: categoryId } : undefined,
      })
      return data
    },
    enabled: Boolean(categoryId),
    staleTime: 1000 * 60 * 60,
  })
}

export function useAttributes() {
  return useQuery({
    queryKey: catalogKeys.attributes,
    queryFn: async () => {
      const { data } = await api.get<Attribute[]>('/catalogs/attributes')
      return data
    },
    staleTime: 1000 * 60 * 60,
  })
}

export function useTaxes() {
  return useQuery({
    queryKey: catalogKeys.taxes,
    queryFn: async () => {
      const { data } = await api.get<Tax[]>('/catalogs/taxes')
      return data
    },
    staleTime: 1000 * 60 * 60,
  })
}