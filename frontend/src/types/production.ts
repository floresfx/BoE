export type ProductionOrderStatus =
  | 'draft'
  | 'planned'
  | 'in_progress'
  | 'completed'
  | 'cancelled'

export type ProductionPlanStatus =
  | 'draft'
  | 'planned'
  | 'in_progress'
  | 'completed'
  | 'cancelled'

export interface ProductionPlan {
  id: string
  code: string
  name: string
  description: string | null
  status: ProductionPlanStatus
  target_date: string | null
  created_at: string
  updated_at: string
}

export interface ProductionPlanListResponse {
  items: ProductionPlan[]
  total: number
}

export interface ProductionOrder {
 id: string
  code: string
  plan_id: string | null
  bundle_id: string
  bundle_name: string
  quantity: string
  status: ProductionOrderStatus | 'not_executed' | 'partial' | 'with_deviation' // Ampliamos el tipo
  start_date: string | null
  end_date: string | null
  notes: string | null
  created_at: string
  updated_at: string
  exception_type?: 'not_executed' | 'partial' | 'with_deviation' | null
  exception_notes?: string | null
}

export interface ProductionOrderListResponse {
  items: ProductionOrder[]
  total: number
}

export interface ProductionOrderCreate {
  code?: string
  plan_id?: string | null
  bundle_id: string
  quantity: string
  notes?: string | null
}