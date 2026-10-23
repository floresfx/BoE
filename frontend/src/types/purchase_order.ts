export interface PurchaseOrderLine {
  id: string
  resource_id: string
  resource_name: string
  quantity: string
  unit_price: string
  subtotal: string
}

export interface PurchaseOrder {
  id: string
  code: string
  request_id: string | null
  supplier_id: string
  supplier_name: string
  status: 'draft' | 'confirmed' | 'received' | 'cancelled'
  total: string
  currency_code: string
  expected_delivery: string | null
  notes: string | null
  created_at: string
  updated_at: string
  lines: PurchaseOrderLine[]
}

export interface PurchaseOrderListResponse {
  items: PurchaseOrder[]
  total: number
}