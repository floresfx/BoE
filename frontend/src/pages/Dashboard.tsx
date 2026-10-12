import { useAuth } from '../hooks/useAuth'

export function Dashboard() {
  const { user } = useAuth()

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Bienvenido, {user?.first_name}
        </h1>
        <p className="text-slate-500 mt-1">
          Este es tu panel de control. Aquí verás un resumen de tu actividad.
        </p>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">
          Tu información
        </h2>
        <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <div>
            <dt className="text-slate-500">Nombre completo</dt>
            <dd className="text-slate-900 font-medium">
              {user?.first_name} {user?.last_name}
            </dd>
          </div>
          <div>
            <dt className="text-slate-500">Correo</dt>
            <dd className="text-slate-900 font-medium">{user?.email}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Tenant ID</dt>
            <dd className="text-slate-900 font-mono text-xs break-all">
              {user?.tenant_id}
            </dd>
          </div>
          <div>
            <dt className="text-slate-500">Estado</dt>
            <dd>
              <span className="inline-block px-2 py-0.5 rounded-full bg-green-100 text-green-800 text-xs font-medium">
                {user?.status}
              </span>
            </dd>
          </div>
        </dl>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-2">
          Próximos pasos
        </h2>
        <p className="text-sm text-slate-600">
          Los módulos de Planificación, Ejecución e Inventario estarán
          disponibles en las próximas versiones.
        </p>
      </div>
    </div>
  )
}