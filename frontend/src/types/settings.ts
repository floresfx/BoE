export type CostingMethod = 'fifo' | 'lifo'

export interface TenantSettings {
  base_currency_id: string | null
  inventory_costing_method: CostingMethod
  date_format_id: string | null
  number_format_id: string | null
  active_unit_ids: string[]
  active_category_ids: string[]
  active_attribute_ids: string[]
  active_tax_ids: string[]
}

export interface TenantSettingsUpdate {
  base_currency_id?: string | null
  inventory_costing_method?: CostingMethod
  date_format_id?: string | null
  number_format_id?: string | null
  active_unit_ids?: string[]
  active_category_ids?: string[]
  active_attribute_ids?: string[]
  active_tax_ids?: string[]
}

export interface CatalogItem {
  id: string
  code: string
  name: string
  symbol?: string
}