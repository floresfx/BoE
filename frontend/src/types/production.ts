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

export interface PlanItemAnnex {
  id: string
  production_order_id: string
  annex_type: string
  resource_id: string | null
  resource_name: string | null
  quantity: string | null
  notes: string | null
}

export interface ProductionOrder {
  id: string
  code: string
  plan_id: string | null
  bundle_id: string
  bundle_name: string
  quantity: string
  // Añadimos los estados de excepción aquí:
  status: 'draft' | 'planned' | 'in_progress' | 'completed' | 'cancelled' | 'not_executed' | 'partial' | 'with_deviation'
  start_date: string | null
  end_date: string | null
  notes: string | null
  created_at: string
  updated_at: string
  exception_type?: 'not_executed' | 'partial' | 'with_deviation' | null
  exception_notes?: string | null
  annexes?: PlanItemAnnex[] 
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