import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { useAuth } from '../hooks/useAuth'
import { useCurrentSubscription } from '../hooks/useSubscription'
import { useResources } from '../hooks/useResources'
import { Link } from 'react-router-dom'

export function Dashboard() {
  const { user } = useAuth()
  const { data: sub, isLoading: loadingSub } = useCurrentSubscription()
  const { data: resourcesData } = useResources({ limit: 1 })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Hola, {user?.first_name}
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Bienvenido a tu panel de BoE MPR.
        </p>
      </div>

      {/* Estado de suscripción */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-900">
            Tu suscripción
          </h2>
          {loadingSub ? (
            <span className="text-sm text-slate-500">Cargando...</span>
          ) : sub?.status === 'trial' ? (
            <Badge variant="yellow">Trial</Badge>
          ) : sub?.status === 'activo' ? (
            <Badge variant="green">Activo</Badge>
          ) : sub?.status === 'sin_plan' ? (
            <Badge variant="gray">Sin plan</Badge>
          ) : (
            <Badge variant="gray">{sub?.status ?? '—'}</Badge>
          )}
        </div>

        {sub?.status === 'sin_plan' && (
          <div className="flex items-center justify-between p-4 bg-yellow-50 border border-yellow-200 rounded">
            <div>
              <p className="font-medium text-yellow-900">
                No tienes un plan activo
              </p>
              <p className="text-sm text-yellow-700 mt-1">
                Selecciona un plan para comenzar a usar el sistema.
              </p>
            </div>
            <Link to="/select-plan">
              <Button>Elegir plan</Button>
            </Link>
          </div>
        )}

        {sub?.status === 'trial' && (
          <div className="p-4 bg-blue-50 border border-blue-200 rounded">
            <p className="font-medium text-blue-900">
              Estás en período de prueba ({sub.plan_name})
            </p>
            <p className="text-sm text-blue-700 mt-1">
              Te quedan <strong>{sub.days_remaining} días</strong> de prueba.
              {sub.trial_ends_at && (
                <>
                  {' '}
                  Termina el{' '}
                  {new Date(sub.trial_ends_at).toLocaleDateString('es-ES')}.
                </>
              )}
            </p>
          </div>
        )}

        {sub?.status === 'activo' && (
          <div className="p-4 bg-green-50 border border-green-200 rounded">
            <p className="font-medium text-green-900">
              Plan {sub.plan_name} activo
            </p>
            <p className="text-sm text-green-700 mt-1">
              Tu suscripción está al día.
            </p>
          </div>
        )}
      </div>

      {/* Resumen rápido */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-slate-500">Recursos</p>
          <p className="text-2xl font-bold text-slate-900 mt-1">
            {resourcesData?.total ?? '—'}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-slate-500">Paquetes</p>
          <p className="text-2xl font-bold text-slate-900 mt-1">—</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-slate-500">Usuarios</p>
          <p className="text-2xl font-bold text-slate-900 mt-1">1</p>
        </div>
      </div>
    </div>
  )
}