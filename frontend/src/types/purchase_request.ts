export type PurchaseRequestStatus =
  | 'draft'
  | 'pending'
  | 'quoted'
  | 'approved'
  | 'ordered'
  | 'partially_received'
  | 'completed'
  | 'cancelled'

export const PURCHASE_REQUEST_STATUSES: {
  value: PurchaseRequestStatus
  label: string
  color: string
}[] = [
  { value: 'draft', label: 'Borrador', color: 'gray' },
  { value: 'pending', label: 'Enviada', color: 'blue' },
  { value: 'quoted', label: 'Cotizada', color: 'yellow' },
  { value: 'approved', label: 'Aprobada', color: 'green' },
  { value: 'ordered', label: 'Ordenada', color: 'blue' },
  {
    value: 'partially_received',
    label: 'Parcial',
    color: 'yellow',
  },
  { value: 'completed', label: 'Completada', color: 'green' },
  { value: 'cancelled', label: 'Cancelada', color: 'red' },
]

export interface PurchaseRequestLine {
  id: string
  resource_id: string
  resource_name: string
  quantity: string
  quantity_received: string
  status: PurchaseRequestStatus
  supplier_id: string | null
  supplier_name: string | null
  notes: string | null
}

export interface PurchaseRequest {
  id: string
  code: string
  status: PurchaseRequestStatus
  needed_by: string | null
  notes: string | null
  lines: PurchaseRequestLine[]
  created_at: string
  updated_at: string
}

export interface PurchaseRequestListResponse {
  items: PurchaseRequest[]
  total: number
}

export interface PurchaseRequestLineInline {
  resource_id: string
  quantity: string
  supplier_id?: string | null
  notes?: string | null
}

export interface PurchaseRequestCreate {
  code: string
  needed_by?: string | null
  notes?: string | null
  lines?: PurchaseRequestLineInline[]
}

export interface PurchaseRequestUpdate {
  needed_by?: string | null
  notes?: string | null
}

export interface PurchaseRequestFromBundleRequest {
  bundle_id: string
  multiplier: string
  code?: string | null
  needed_by?: string | null
  notes?: string | null
}
// ============================================================
// Cotizaciones (Bloque 6.2)
// ============================================================

export type SupplierQuoteStatus = 'pending' | 'accepted' | 'rejected'

export interface SupplierQuote {
  id: string
  request_id: string
  line_id: string
  supplier_id: string
  supplier_name: string
  unit_price: string
  currency_code: string
  lead_time_days: number
  valid_until: string | null
  notes: string | null
  status: string
  is_selected: boolean
  created_at: string
  updated_at: string
}

export interface SupplierQuoteListResponse {
  items: SupplierQuote[]
  total: number
}

export interface SupplierQuoteCreate {
  line_id: string
  supplier_id: string
  unit_price: string
  currency_code?: string
  lead_time_days?: number
  valid_until?: string | null
  notes?: string | null
}

export interface SupplierQuoteUpdate {
  unit_price?: string
  currency_code?: string
  lead_time_days?: number
  valid_until?: string | null
  notes?: string | null
}

// ============================================================
// Recepción de mercancía (Bloque 5)
// ============================================================

export interface ReceiveLineIn {
  line_id: string
  received_quantity: string
  lot_code: string
  unit_cost?: string | null
  expiration?: string | null
  notes?: string | null
}

export interface ReceiveRequest {
  warehouse_id: string
  lines: ReceiveLineIn[]
  notes?: string | null
}

export interface ReceiveLineResponse {
  line_id: string
  resource_id: string
  resource_name: string
  quantity_received: string
  lot_code: string
  movement_id: string
}

export interface ReceiveResponse {
  request_id: string
  request_code: string
  new_status: string
  lines: ReceiveLineResponse[]
  message: string
}

// --- Tipos para cotizaciones ---

export interface SupplierQuote {
  id: string
  request_id: string
  line_id: string
  supplier_id: string
  supplier_name: string
  unit_price: string
  currency_code: string
  lead_time_days: number
  valid_until: string | null
  notes: string | null
  status: string
  is_selected: boolean
  created_at: string
  updated_at: string
}

export interface SupplierQuoteListResponse {
  items: SupplierQuote[]
  total: number
}

export interface SupplierQuoteCreate {
  line_id: string
  supplier_id: string
  unit_price: string
  currency_code?: string
  lead_time_days?: number
  valid_until?: string | null
  notes?: string | null
}

export interface SupplierQuoteUpdate {
  unit_price?: string
  currency_code?: string
  lead_time_days?: number
  valid_until?: string | null
  notes?: string | null
}