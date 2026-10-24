import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { useAuth } from '../hooks/useAuth'
import { useCurrentSubscription } from '../hooks/useSubscription'
import { useResources } from '../hooks/useResources'
import { useDashboardSummary } from '../hooks/useDashboard' // <--- NUEVO
import { Link } from 'react-router-dom'

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer,
  LineChart, Line
} from 'recharts';

export function Dashboard() {
  const { user } = useAuth()
  const { data: sub, isLoading: loadingSub } = useCurrentSubscription()
  const { data: resourcesData } = useResources({ limit: 1 })
  const { data: summary, isLoading: loadingSummary } = useDashboardSummary() // <--- NUEVO

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
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
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
              <Link to="/select-plan?mode=change">
                <Button size="sm" variant="secondary">
                  Cambiar plan
                </Button>
              </Link>
            </div>
          </div>
        )}

        {sub?.status === 'activo' && (
          <div className="p-4 bg-green-50 border border-green-200 rounded">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <p className="font-medium text-green-900">
                  Plan {sub.plan_name} activo
                </p>
                <p className="text-sm text-green-700 mt-1">
                  Tu suscripción está al día.
                </p>
              </div>
              <Link to="/select-plan?mode=change">
                <Button size="sm" variant="secondary">
                  Cambiar plan
                </Button>
              </Link>
            </div>
          </div>
        )}
      </div>

      {/* --- NUEVO: KPIs del Dashboard --- */}
      <div>
        <h2 className="text-lg font-semibold text-slate-900 mb-4">
          Resumen de Operaciones
        </h2>
        {loadingSummary ? (
          <div className="text-sm text-slate-500">Cargando KPIs...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Tarjeta 1: Recursos Activos */}
            <div className="bg-white rounded-lg shadow p-6 border border-slate-200">
              <p className="text-sm font-medium text-slate-500">Recursos Activos</p>
              <p className="text-3xl font-bold text-slate-900 mt-2">
                {summary?.total_resources ?? 0}
              </p>
              <p className="text-xs text-slate-400 mt-1">Materiales y servicios registrados</p>
            </div>

            {/* Tarjeta 2: Valor del Inventario */}
            <div className="bg-white rounded-lg shadow p-6 border border-slate-200">
              <p className="text-sm font-medium text-slate-500">Valor del Inventario</p>
              <p className="text-3xl font-bold text-green-600 mt-2">
                ${Number(summary?.total_inventory_value ?? 0).toLocaleString('es-ES', { minimumFractionDigits: 2 })}
              </p>
              <p className="text-xs text-slate-400 mt-1">Suma de (cantidad × costo)</p>
            </div>

            {/* Tarjeta 3: Items en Stock */}
            <div className="bg-white rounded-lg shadow p-6 border border-slate-200">
              <p className="text-sm font-medium text-slate-500">Items en Stock</p>
              <p className="text-3xl font-bold text-indigo-600 mt-2">
                {Number(summary?.total_stock_items ?? 0).toLocaleString('es-ES')}
              </p>
              <p className="text-xs text-slate-400 mt-1">Suma total de cantidades</p>
            </div>

            {/* Tarjeta 4: Órdenes de Producción */}
            <div className="bg-white rounded-lg shadow p-6 border border-slate-200">
              <p className="text-sm font-medium text-slate-500">Órdenes de Producción</p>
              <p className="text-3xl font-bold text-orange-600 mt-2">
                {summary?.pending_production_orders ?? 0}
              </p>
              <p className="text-xs text-slate-400 mt-1">Pendientes (draft o en progreso)</p>
            </div>

            {/* Tarjeta 5: Solicitudes de Compra */}
            <div className="bg-white rounded-lg shadow p-6 border border-slate-200">
              <p className="text-sm font-medium text-slate-500">Solicitudes de Compra</p>
              <p className="text-3xl font-bold text-purple-600 mt-2">
                {summary?.pending_purchase_requests ?? 0}
              </p>
              <p className="text-xs text-slate-400 mt-1">Pendientes (draft o enviadas)</p>
            </div>

            {/* Tarjeta 6: Alertas de Caducidad */}
            <div className="bg-white rounded-lg shadow p-6 border border-slate-200">
              <p className="text-sm font-medium text-slate-500">Alertas de Caducidad</p>
              <p className="text-3xl font-bold text-red-600 mt-2">
                {summary?.expiring_soon_alerts ?? 0}
              </p>
              <p className="text-xs text-slate-400 mt-1">Lotes que vencen en 30 días</p>
            </div>

            {/* --- NUEVOS GRÁFICOS (Recharts) --- */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
              
              {/* Gráfico 1: Margen por Bundle */}
              <div className="bg-white rounded-lg shadow p-6 border border-slate-200">
                <h3 className="text-md font-semibold text-slate-900 mb-4">Margen Estimado por Paquete (Top 5)</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={summary?.bundle_margins || []} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} />
                      <RechartsTooltip formatter={(value) => `$${Number(value).toFixed(2)}`} />
                      <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Margen ($)" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Gráfico 2: Top Proveedores */}
              <div className="bg-white rounded-lg shadow p-6 border border-slate-200">
                <h3 className="text-md font-semibold text-slate-900 mb-4">Top Proveedores (por Ofertas)</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={summary?.top_suppliers || []} layout="vertical" margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                      <XAxis type="number" tick={{ fontSize: 12 }} />
                      <YAxis dataKey="name" type="category" tick={{ fontSize: 12 }} width={100} />
                      <RechartsTooltip />
                      <Bar dataKey="value" fill="#8b5cf6" radius={[0, 4, 4, 0]} name="Cant. Ofertas" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Gráfico 3: Rotación de Inventario */}
              <div className="bg-white rounded-lg shadow p-6 border border-slate-200 lg:col-span-2">
                <h3 className="text-md font-semibold text-slate-900 mb-4">Rotación de Inventario (Últimos 6 meses)</h3>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={summary?.inventory_rotation || []} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} />
                      <RechartsTooltip />
                      <Legend />
                      <Line type="monotone" dataKey="value" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 8 }} name="Movimientos" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

            </div>


          </div>
        )}
      </div>

      {/* Resumen rápido (el que ya tenías) */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-slate-500">Recursos (total)</p>
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