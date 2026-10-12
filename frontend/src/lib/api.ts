import axios from 'axios'
import { auth } from './auth'

// Cliente Axios configurado
// En dev, el proxy de Vite redirige /api → http://localhost:8000
export const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor: añade el Bearer token a cada request
api.interceptors.request.use((config) => {
  const token = auth.getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor: si el backend devuelve 401, limpia el token
// y redirige a /login (excepto si ya estamos en /login)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      auth.clearToken()
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)