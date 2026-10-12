export type ResourceType =
  | 'materia_prima'
  | 'producto_terminado'
  | 'subproducto'
  | 'insumo'
  | 'servicio_propio'
  | 'servicio_externo'
  | 'recurso_humano'
  | 'recurso_fisico'

export const RESOURCE_TYPES: { value: ResourceType; label: string }[] = [
  { value: 'materia_prima', label: 'Materia prima' },
  { value: 'producto_terminado', label: 'Producto terminado' },
  { value: 'subproducto', label: 'Subproducto' },
  { value: 'insumo', label: 'Insumo' },
  { value: 'servicio_propio', label: 'Servicio propio' },
  { value: 'servicio_externo', label: 'Servicio externo' },
  { value: 'recurso_humano', label: 'Recurso humano' },
  { value: 'recurso_fisico', label: 'Recurso físico' },
]

export interface Resource {
  id: string
  name: string
  resource_type: ResourceType
  category: string | null
  base_unit: string
  cost: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ResourceCreate {
  name: string
  resource_type: ResourceType
  category?: string | null
  base_unit: string
  cost?: string | null
  is_active?: boolean
}

export interface ResourceUpdate {
  name?: string
  resource_type?: ResourceType
  category?: string | null
  base_unit?: string
  cost?: string | null
  is_active?: boolean
}

export interface ResourceListResponse {
  items: Resource[]
  total: number
}

export interface ResourceListParams {
  skip?: number
  limit?: number
  resource_type?: ResourceType
  category?: string
  search?: string
  is_active?: boolean
}