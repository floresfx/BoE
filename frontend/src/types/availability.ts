// src/types/availability.ts

export type AvailabilityStatus = 'covered' | 'partial' | 'out_of_stock';


export interface WarehouseAvailability {
  warehouse_id: string;
  warehouse_name: string;
  available: number;
}

export interface SupplierSuggestion {
  supplier_id: string;
  supplier_name: string;
  unit_price: number;
  lead_time_days: number;
  currency_code: string;
}

export interface AvailabilityResponse {
  resource_id: string;
  resource_name: string;
  required_quantity: number;
  available_quantity: number;
  missing_quantity: number;
  status: AvailabilityStatus;
  warehouses: WarehouseAvailability[];
  suppliers: SupplierSuggestion[];
}

export interface BundleAvailabilityResponse {
  bundle_id: string;
  bundle_name: string;
  multiplier: number;
  overall_status: AvailabilityStatus;
  lines: AvailabilityResponse[];
}