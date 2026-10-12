// Tipos compartidos con el backend

export type UserStatus = 'activo' | 'inactivo' | 'suspendido'

export interface User {
  id: string
  tenant_id: string
  email: string
  first_name: string
  last_name: string
  phone: string | null
  phone_verified: boolean
  status: UserStatus
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