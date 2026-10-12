import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'
import { api } from '../lib/api'
import type {
  Resource,
  ResourceCreate,
  ResourceListParams,
  ResourceListResponse,
  ResourceUpdate,
} from '../types/resource'

const QUERY_KEY = 'resources'

export function useResources(params: ResourceListParams = {}) {
  return useQuery({
    queryKey: [QUERY_KEY, params],
    queryFn: async () => {
      const { data } = await api.get<ResourceListResponse>('/resources', {
        params,
      })
      return data
    },
  })
}

export function useCreateResource() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: ResourceCreate) => {
      const { data } = await api.post<Resource>('/resources', payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QUERY_KEY] })
    },
  })
}

export function useUpdateResource() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({
      id,
      payload,
    }: {
      id: string
      payload: ResourceUpdate
    }) => {
      const { data } = await api.put<Resource>(`/resources/${id}`, payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QUERY_KEY] })
    },
  })
}

export function useDeleteResource() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/resources/${id}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QUERY_KEY] })
    },
  })
}