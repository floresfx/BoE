// Helpers para manejar el token JWT

const TOKEN_KEY = 'boe_mpr_token'
const USER_KEY = 'boe_mpr_user'

export const auth = {
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY)
  },

  setToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token)
  },

  clearToken(): void {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  },

  getUser<T = unknown>(): T | null {
    const raw = localStorage.getItem(USER_KEY)
    if (!raw) return null
    try {
      return JSON.parse(raw) as T
    } catch {
      return null
    }
  },

  setUser(user: unknown): void {
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  },

  isAuthenticated(): boolean {
    return Boolean(this.getToken())
  },
}