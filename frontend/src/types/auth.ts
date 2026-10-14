// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export interface User {
  id: string
  tenant_id: string
  email: string
  first_name: string
  last_name: string
  phone: string | null
  status: string
  last_login_at: string | null
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

// ---------------------------------------------------------------------------
// Registro
// ---------------------------------------------------------------------------

export interface RegisterRequest {
  company_name: string
  tax_id: string
  tax_id_type: string
  vertical_id: string
  country_code: string
  base_currency: string
  admin_email: string
  admin_password: string
  admin_first_name: string
  admin_last_name: string
  admin_phone: string
}

export interface RegisterResponse {
  tenant_id: string
  user_id: string
  email: string
  schema_name: string
  message: string
}

// ---------------------------------------------------------------------------
// Suscripción
// ---------------------------------------------------------------------------

export interface PlanSummary {
  id: string
  code: string
  name: string
  price: string
  currency_code: string
  interval: string
  trial_days: number
  features: string[]
  limits: Record<string, number | null>
}

export interface SubscriptionInfo {
  plan_id: string | null
  plan_name: string | null
  status: 'sin_plan' | 'trial' | 'activo' | 'pausado' | 'cancelado'
  trial_ends_at: string | null
  days_remaining: number | null
}

export interface SelectPlanResponse {
  plan_id: string
  plan_name: string
  status: string
  trial_ends_at: string | null
  message: string
}