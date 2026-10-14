import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { api } from '../lib/api'
import { auth } from '../lib/auth'
import type {
  LoginRequest,
  RegisterRequest,
  RegisterResponse,
  User,
} from '../types/auth'

interface AuthContextValue {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (data: LoginRequest) => Promise<void>
  register: (data: RegisterRequest) => Promise<RegisterResponse>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => auth.getUser<User>())
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (!auth.getToken()) {
      setUser(null)
    }
  }, [])

  const login = useCallback(async (data: LoginRequest) => {
    setIsLoading(true)
    try {
      const response = await api.post('/auth/login', data)
      const { access_token, user: loggedUser } = response.data
      auth.setToken(access_token)
      auth.setUser(loggedUser)
      setUser(loggedUser)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const register = useCallback(
    async (data: RegisterRequest): Promise<RegisterResponse> => {
      setIsLoading(true)
      try {
        const response = await api.post<RegisterResponse>('/register', data)
        return response.data
      } finally {
        setIsLoading(false)
      }
    },
    [],
  )

  const logout = useCallback(() => {
    auth.clearToken()
    setUser(null)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isLoading,
      login,
      register,
      logout,
    }),
    [user, isLoading, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth debe usarse dentro de <AuthProvider>')
  }
  return ctx
}