import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'
import { useAuth } from '../../hooks/useAuth'
import { useCurrentSubscription } from '../../hooks/useSubscription'
import { Link } from 'react-router-dom'

export function Header() {
  const { user, logout } = useAuth()
  const { data: sub } = useCurrentSubscription()

  const trialBadge = () => {
    if (!sub) return null
    if (sub.status === 'trial' && sub.days_remaining !== null) {
      return (
        <Link to="/select-plan">
          <Badge variant="yellow">
            Trial · {sub.days_remaining} días
          </Badge>
        </Link>
      )
    }
    if (sub.status === 'sin_plan') {
      return (
        <Link to="/select-plan">
          <Badge variant="gray">Sin plan</Badge>
        </Link>
      )
    }
    if (sub.status === 'activo') {
      return <Badge variant="green">{sub.plan_name}</Badge>
    }
    return null
  }

  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6">
      <div className="text-sm text-slate-500">
        {/* Espacio para breadcrumbs en el futuro */}
      </div>

      <div className="flex items-center gap-4">
        {trialBadge()}
        <div className="text-sm text-slate-700 text-right">
          <p className="font-medium">
            {user?.first_name} {user?.last_name}
          </p>
          <p className="text-xs text-slate-500">{user?.email}</p>
        </div>
        <Button size="sm" variant="secondary" onClick={logout}>
          Salir
        </Button>
      </div>
    </header>
  )
}