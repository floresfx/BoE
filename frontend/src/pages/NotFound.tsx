import { Link } from 'react-router-dom'

export function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-100 px-4">
      <h1 className="text-6xl font-bold text-slate-900">404</h1>
      <p className="text-slate-600 mt-4">Página no encontrada</p>
      <Link
        to="/dashboard"
        className="mt-6 px-4 py-2 bg-slate-900 text-white rounded-md text-sm hover:bg-slate-800 transition-colors"
      >
        Volver al inicio
      </Link>
    </div>
  )
}