export interface SupplierResource {
  resource_id: string
  resource_name: string
  unit_price: string | null
  currency_id: string | null
  currency_code: string | null
  lead_time_days: number | null
  min_quantity: string | null
  valid_until: string | null
  notes: string | null
}

export interface Supplier {
  id: string
  code: string
  name: string
  tax_id: string | null
  email: string | null
  phone: string | null
  address: string | null
  contact_name: string | null
  notes: string | null
  is_active: boolean
  resources: SupplierResource[]
  created_at: string
  updated_at: string
}

export interface SupplierListResponse {
  items: Supplier[]
  total: number
}

export interface SupplierResourceInline {
  resource_id: string
  unit_price?: string | null
  currency_id?: string | null
  lead_time_days?: number | null
  min_quantity?: string | null
  valid_until?: string | null
  notes?: string | null
}

export interface SupplierResourceUpdate {
  unit_price?: string | null
  currency_id?: string | null
  lead_time_days?: number | null
  min_quantity?: string | null
  valid_until?: string | null
  notes?: string | null
}

export interface SupplierCreate {
  code: string
  name: string
  tax_id?: string | null
  email?: string | null
  phone?: string | null
  address?: string | null
  contact_name?: string | null
  notes?: string | null
  is_active?: boolean
  resources?: SupplierResourceInline[]
}

export interface SupplierUpdate {
  name?: string
  tax_id?: string | null
  email?: string | null
  phone?: string | null
  address?: string | null
  contact_name?: string | null
  notes?: string | null
  is_active?: boolean
}