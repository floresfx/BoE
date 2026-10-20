export interface Warehouse {
  id: string
  name: string
  code: string
  address: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface WarehouseListResponse {
  items: Warehouse[]
  total: number
}

export interface WarehouseCreate {
  name: string
  code: string
  address?: string | null
  is_active?: boolean
}

export interface WarehouseUpdate {
  name?: string
  address?: string | null
  is_active?: boolean
}

export type MovementType = 'in' | 'out' | 'adjust' | 'loss'

export interface Movement {
  id: string
  warehouse_id: string
  resource_id: string
  lot_id: string | null
  movement_type: MovementType
  quantity: string
  unit_cost: string | null
  reference: string | null
  notes: string | null
  created_by: string | null
  created_at: string
  updated_at: string
}

export interface MovementListResponse {
  items: Movement[]
  total: number
}

export interface MovementCreate {
  warehouse_id: string
  resource_id: string
  lot_code: string
  movement_type: MovementType
  quantity: string
  unit_cost?: string | null
  expiration?: string | null
  reference?: string | null
  notes?: string | null
}

export interface StockConsolidated {
  warehouse_id: string
  warehouse_name?: string 
  resource_id: string
  resource_name?: string 
  unit_symbol?: string
  total_quantity: string
  lot_count: number
  nearest_expiration: string | null
}

export interface StockConsolidatedListResponse {
  items: StockConsolidated[]
  total: number
}

export interface ExpirationAlert {
  lot_id: string
  warehouse_id: string
  warehouse_name: string
  resource_id: string
  resource_name: string
  lot_code: string
  quantity: string
  expiration: string
  days_until_expiration: number
}