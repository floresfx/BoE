export interface AdminVertical {
  id: string
  code: string
  name: string
  description: string
  is_active: boolean
}

export interface AdminFeature {
  id: string
  code: string
  name: string
  description: string
  applies_to: 'mpr' | 'marketplace' | 'both'
  is_active: boolean
}

export interface AdminPlan {
  id: string
  code: string
  name: string
  price: string
  currency_id: string
  interval: string
  trial_days: number
  is_active: boolean
  feature_codes: string[]
  limits: Record<string, number | null>
}

export interface AdminAttribute {
  id: string
  code: string
  name: string
  type_code: string
  is_active: boolean
}

export interface AdminTax {
  id: string
  country_code: string
  code: string
  name: string
  rate: string
  applies_to: string
  is_active: boolean
}

export interface AdminService {
  id: string
  code: string
  name: string
  description: string
  category_id: string | null
  is_active: boolean
}

export interface AdminCurrency {
  id: string
  code: string
  name: string
  symbol: string
  decimals: number
  is_base: boolean
  is_active: boolean
}

export interface AdminUnit {
  id: string
  code: string
  name: string
  symbol: string
  category_id: string
  is_base: boolean
  is_active: boolean
}

export interface AdminCategory {
  id: string
  code: string
  name: string
  is_active: boolean
}

export interface AdminCountry {
  id: string
  code: string
  name: string
  timezone_id: string
  currency_id: string
  phone_prefix: string
  is_active: boolean
}

export interface AdminDocumentType {
  id: string
  code: string
  name: string
  country_id: string | null
  format: string | null
  regex: string | null
  is_active: boolean
}