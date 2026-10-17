export type PurchaseRequestStatus =
  | 'draft'
  | 'pending'
  | 'approved'
  | 'rejected'
  | 'completed'
  | 'cancelled'

export const PURCHASE_REQUEST_STATUSES: { value: PurchaseRequestStatus; label: string; color: string }[] = [
  { value: 'draft', label: 'Borrador', color: 'gray' },
  { value: 'pending', label: 'Pendiente', color: 'yellow' },
  { value: 'approved', label: 'Aprobada', color: 'green' },
  { value: 'rejected', label: 'Rechazada', color: 'red' },
  { value: 'completed', label: 'Completada', color: 'blue' },
  { value: 'cancelled', label: 'Cancelada', color: 'gray' },
]

export interface PurchaseRequestLine {
  id: string
  resource_id: string
  resource_name: string
  quantity: string
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