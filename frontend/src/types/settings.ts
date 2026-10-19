export type CostingMethod = 'fifo' | 'lifo'

export interface TenantSettings {
  id: string
  name: string
  inventory_costing_method: CostingMethod
  // ... otros campos si los necesitas
}

export interface TenantSettingsUpdate {
  inventory_costing_method?: CostingMethod
}