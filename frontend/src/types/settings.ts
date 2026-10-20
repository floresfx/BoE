export type CostingMethod = 'fifo' | 'lifo'

export interface TenantSettings {
  base_currency_id: string | null
  inventory_costing_method: CostingMethod
  active_unit_ids: string[]
  active_category_ids: string[]
  active_attribute_ids: string[]
}

export interface TenantSettingsUpdate {
  base_currency_id?: string | null
  inventory_costing_method?: CostingMethod
  active_unit_ids?: string[]
  active_category_ids?: string[]
  active_attribute_ids?: string[]
}

// Tipos para los catálogos globales
export interface CatalogItem {
  id: string
  code: string
  name: string
  symbol?: string
  type_id?: string // Para atributos
  category_id?: string // Para subcategorías
}