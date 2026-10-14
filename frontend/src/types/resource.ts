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

// ---------------------------------------------------------------------------
// Relaciones N:M
// ---------------------------------------------------------------------------

export interface ResourceAttribute {
  attribute_id: string
  attribute_code: string
  attribute_name: string
  value: string | null
}

export interface ResourceTax {
  tax_id: string
  tax_code: string
  tax_name: string
  tax_rate: string
}

export interface ResourceAttributeInline {
  attribute_id: string
  value?: string | null
}

export interface ResourceTaxInline {
  tax_id: string
}

// ---------------------------------------------------------------------------
// Resource
// ---------------------------------------------------------------------------

export interface Resource {
  id: string
  name: string
  resource_type: ResourceType
  category_id: string | null
  subcategory_id: string | null
  base_unit_id: string
  cost: string | null
  is_active: boolean
  attributes: ResourceAttribute[]
  taxes: ResourceTax[]
  created_at: string
  updated_at: string
}

export interface ResourceCreate {
  name: string
  resource_type: ResourceType
  category_id?: string | null
  subcategory_id?: string | null
  base_unit_id: string
  cost?: string | null
  is_active?: boolean
  attributes?: ResourceAttributeInline[]
  taxes?: ResourceTaxInline[]
}

export interface ResourceUpdate {
  name?: string
  resource_type?: ResourceType
  category_id?: string | null
  subcategory_id?: string | null
  base_unit_id?: string
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
  category_id?: string
  subcategory_id?: string
  search?: string
  is_active?: boolean
}