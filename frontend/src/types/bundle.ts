export interface BundleComponent {
  resource_id: string
  resource_name: string
  resource_unit_symbol: string | null
  quantity: string
  notes: string | null
}

export interface Bundle {
  id: string
  code: string
  name: string
  description: string | null
  category_id: string | null
  is_active: boolean
  components: BundleComponent[]
  created_at: string
  updated_at: string
}

export interface BundleListResponse {
  items: Bundle[]
  total: number
}

export interface BundleComponentInline {
  resource_id: string
  quantity: string
  notes?: string | null
}

export interface BundleCreate {
  code: string
  name: string
  description?: string | null
  category_id?: string | null
  is_active?: boolean
  components?: BundleComponentInline[]
}

export interface BundleUpdate {
  name?: string
  description?: string | null
  category_id?: string | null
  is_active?: boolean
}

export interface ExplodedComponent {
  resource_id: string
  resource_name: string
  resource_unit_symbol: string | null
  required_quantity: string
  notes: string | null
}

export interface BundleExplodeResponse {
  bundle_id: string
  bundle_code: string
  bundle_name: string
  multiplier: string
  total_components: number
  components: ExplodedComponent[]
}