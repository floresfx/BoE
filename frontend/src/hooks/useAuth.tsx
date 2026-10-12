import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { api } from '../lib/api'
import { auth } from '../lib/auth'
import type { LoginRequest, LoginResponse, User } from '../types/api'

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (credentials: LoginRequest) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(() => auth.getUser<User>())
  const [isLoading, setIsLoading] = useState(false)

  // Verifica el token al cargar la app
  useEffect(() => {
    const token = auth.getToken()
    if (!token) {
      setUser(null)
      return
    }

    // Si hay token pero no user en localStorage, pide /me
    if (!user) {
      api
        .get<User>('/auth/me')
        .then(({ data }) => {
          setUser(data)
          auth.setUser(data)
        })
        .catch(() => {
          auth.clearToken()
          setUser(null)
        })
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const login = useCallback(async (credentials: LoginRequest) => {
    setIsLoading(true)
    try {
      const { data } = await api.post<LoginResponse>('/auth/login', credentials)
      auth.setToken(data.access_token)
      auth.setUser(data.user)
      setUser(data.user)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    auth.clearToken()
    setUser(null)
  }, [])

  const value: AuthContextValue = {
    user,
    isLoading,
    isAuthenticated: Boolean(user),
    login,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth debe usarse dentro de <AuthProvider>')
  }
  return ctx
}