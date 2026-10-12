import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

export function Header() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6">
      <div />

      <div className="flex items-center gap-4">
        {user && (
          <div className="text-right">
            <p className="text-sm font-medium text-slate-900">
              {user.first_name} {user.last_name}
            </p>
            <p className="text-xs text-slate-500">{user.email}</p>
          </div>
        )}

        <button
          onClick={handleLogout}
          className="px-3 py-1.5 text-sm rounded-md border border-slate-300 text-slate-700 hover:bg-slate-50 transition-colors"
        >
          Cerrar sesión
        </button>
      </div>
    </header>
  )
}