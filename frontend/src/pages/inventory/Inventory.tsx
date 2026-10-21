import { useState } from 'react'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import {
  useExpirationAlerts,
  useStockConsolidated,
  useWarehouses,
} from '../../hooks/useInventory'
import {
  useStockReservations,
  useCancelStockReservation,
} from '../../hooks/useStockReservations'
import { MovementModal } from './MovementModal'
import { WarehouseForm } from './WarehouseForm'
import { ReservationModal } from './ReservationModal'
import { useDownloadReport } from '../../hooks/useReports'


type Tab = 'stock' | 'warehouses' | 'alerts' | 'reservations'

export function Inventory() {
  const [activeTab, setActiveTab] = useState<Tab>('stock')
  const [movementOpen, setMovementOpen] = useState(false)
  const [warehouseFormOpen, setWarehouseFormOpen] = useState(false)
  const [reservationOpen, setReservationOpen] = useState(false)
  const { downloadExcel, downloadPdf } = useDownloadReport()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Inventario</h1>
          <p className="text-sm text-slate-500 mt-1">
            Stock, almacenes, movimientos y reservas.
          </p>
        </div>
        <div className="space-x-2">
          <Button onClick={() => setWarehouseFormOpen(true)} variant="secondary">
            + Almacén
          </Button>
          <Button onClick={() => setMovementOpen(true)}>
            + Movimiento
          </Button>
          <Button onClick={() => setReservationOpen(true)} variant="secondary">
            + Reserva
          </Button>
          <Button onClick={downloadExcel} variant="secondary">
            Exportar Excel
          </Button>
          <Button onClick={downloadPdf} variant="secondary">
            Exportar PDF
          </Button>
        </div>
      </div>

      <div className="border-b border-slate-200">
        <nav className="flex gap-2 -mb-px">
          {[
            { id: 'stock' as Tab, label: 'Stock consolidado' },
            { id: 'warehouses' as Tab, label: 'Almacenes' },
            { id: 'alerts' as Tab, label: 'Alertas de caducidad' },
            { id: 'reservations' as Tab, label: 'Reservas' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 text-sm font-medium border-b-2 ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        {activeTab === 'stock' && <StockTab />}
        {activeTab === 'warehouses' && <WarehousesTab />}
        {activeTab === 'alerts' && <AlertsTab />}
        {activeTab === 'reservations' && <ReservationsTab />}
      </div>

      <MovementModal
        open={movementOpen}
        onClose={() => setMovementOpen(false)}
      />
      <WarehouseForm
        open={warehouseFormOpen}
        onClose={() => setWarehouseFormOpen(false)}
      />
      <ReservationModal
        open={reservationOpen}
        onClose={() => setReservationOpen(false)}
      />
    </div>
  )
}

// ---------------------------------------------------------------------------
// Stock consolidado
// ---------------------------------------------------------------------------

function StockTab() {
  const { data, isLoading } = useStockConsolidated()
  const { data: warehouses } = useWarehouses()

  if (isLoading) return <div className="p-8 text-center text-slate-500">Cargando...</div>
  if (!data?.items.length)
    return (
      <div className="p-8 text-center text-slate-500">
        No hay stock. Registra un movimiento de entrada para empezar.
      </div>
    )

  const wMap = Object.fromEntries((warehouses?.items ?? []).map((w) => [w.id, w]))

  return (
    <table className="w-full text-sm">
      <thead className="bg-slate-50 border-b border-slate-200">
        <tr>
          <th className="text-left px-4 py-3 font-medium text-slate-700">Almacén</th>
          <th className="text-left px-4 py-3 font-medium text-slate-700">Recurso</th>
          <th className="text-right px-4 py-3 font-medium text-slate-700">Cantidad Disponible</th>
          <th className="text-right px-4 py-3 font-medium text-slate-700">Lotes</th>
          <th className="text-left px-4 py-3 font-medium text-slate-700">Próx. caducidad</th>
        </tr>
      </thead>
      <tbody className="divide-y divide-slate-100">
        {data.items.map((s, i) => (
          <tr key={i} className="hover:bg-slate-50">
            <td className="px-4 py-3">
              {s.warehouse_name || wMap[s.warehouse_id]?.name || s.warehouse_id.slice(0, 8)}
            </td>
            <td className="px-4 py-3 font-medium text-slate-900">
              {s.resource_name || s.resource_id.slice(0, 8)}…
            </td>
            <td className="px-4 py-3 text-right font-medium">{s.total_quantity} {s.unit_symbol}</td>
            <td className="px-4 py-3 text-right">{s.lot_count}</td>
            <td className="px-4 py-3 text-slate-600">
              {s.nearest_expiration
                ? new Date(s.nearest_expiration).toLocaleDateString('es-ES')
                : '—'}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

// ---------------------------------------------------------------------------
// Warehouses
// ---------------------------------------------------------------------------

function WarehousesTab() {
  const { data, isLoading } = useWarehouses()
  if (isLoading) return <div className="p-8 text-center text-slate-500">Cargando...</div>
  if (!data?.items.length)
    return (
      <div className="p-8 text-center text-slate-500">
        No hay almacenes. Crea el primero con el botón "+ Almacén".
      </div>
    )
  return (
    <table className="w-full text-sm">
      <thead className="bg-slate-50 border-b border-slate-200">
        <tr>
          <th className="text-left px-4 py-3 font-medium text-slate-700">Código</th>
          <th className="text-left px-4 py-3 font-medium text-slate-700">Nombre</th>
          <th className="text-left px-4 py-3 font-medium text-slate-700">Dirección</th>
          <th className="text-left px-4 py-3 font-medium text-slate-700">Estado</th>
        </tr>
      </thead>
      <tbody className="divide-y divide-slate-100">
        {data.items.map((w) => (
          <tr key={w.id} className="hover:bg-slate-50">
            <td className="px-4 py-3 font-mono text-xs">{w.code}</td>
            <td className="px-4 py-3 font-medium">{w.name}</td>
            <td className="px-4 py-3 text-slate-600">{w.address ?? '—'}</td>
            <td className="px-4 py-3">
              {w.is_active ? (
                <Badge variant="green">Activo</Badge>
              ) : (
                <Badge variant="gray">Inactivo</Badge>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

// ---------------------------------------------------------------------------
// Alertas de caducidad
// ---------------------------------------------------------------------------

function AlertsTab() {
  const { data, isLoading } = useExpirationAlerts(60)
  if (isLoading) return <div className="p-8 text-center text-slate-500">Cargando...</div>
  if (!data?.length)
    return (
      <div className="p-8 text-center text-slate-500">
        Sin alertas. No hay lotes por caducar en los próximos 60 días.
      </div>
    )
  return (
    <table className="w-full text-sm">
      <thead className="bg-slate-50 border-b border-slate-200">
        <tr>
          <th className="text-left px-4 py-3 font-medium text-slate-700">Recurso</th>
          <th className="text-left px-4 py-3 font-medium text-slate-700">Almacén</th>
          <th className="text-left px-4 py-3 font-medium text-slate-700">Lote</th>
          <th className="text-right px-4 py-3 font-medium text-slate-700">Cantidad</th>
          <th className="text-left px-4 py-3 font-medium text-slate-700">Caduca</th>
          <th className="text-right px-4 py-3 font-medium text-slate-700">Días</th>
        </tr>
      </thead>
      <tbody className="divide-y divide-slate-100">
        {data.map((a) => (
          <tr key={a.lot_id} className="hover:bg-slate-50">
            <td className="px-4 py-3 font-medium">{a.resource_name}</td>
            <td className="px-4 py-3">{a.warehouse_name}</td>
            <td className="px-4 py-3 font-mono text-xs">{a.lot_code}</td>
            <td className="px-4 py-3 text-right">{a.quantity}</td>
            <td className="px-4 py-3">{new Date(a.expiration).toLocaleDateString('es-ES')}</td>
            <td className="px-4 py-3 text-right">
              {a.days_until_expiration < 0 ? (
                <Badge variant="red">Vencido</Badge>
              ) : a.days_until_expiration <= 7 ? (
                <Badge variant="red">{a.days_until_expiration}d</Badge>
              ) : a.days_until_expiration <= 30 ? (
                <Badge variant="yellow">{a.days_until_expiration}d</Badge>
              ) : (
                <Badge variant="gray">{a.days_until_expiration}d</Badge>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

// ---------------------------------------------------------------------------
// Reservas de Stock
// ---------------------------------------------------------------------------

function ReservationsTab() {
  const { data, isLoading } = useStockReservations()
  const cancelMutation = useCancelStockReservation()

  if (isLoading) return <div className="p-8 text-center text-slate-500">Cargando...</div>
  if (!data?.items.length) {
    return (
      <div className="p-8 text-center text-slate-500">
        No hay reservas. Crea una reserva para apartar stock para un pedido futuro.
      </div>
    )
  }

  return (
    <table className="w-full text-sm">
      <thead className="bg-slate-50 border-b border-slate-200">
        <tr>
          <th className="text-left px-4 py-3 font-medium text-slate-700">Referencia</th>
          <th className="text-left px-4 py-3 font-medium text-slate-700">Recurso ID</th>
          <th className="text-right px-4 py-3 font-medium text-slate-700">Cantidad</th>
          <th className="text-left px-4 py-3 font-medium text-slate-700">Estado</th>
          <th className="text-left px-4 py-3 font-medium text-slate-700">Necesario para</th>
          <th className="text-right px-4 py-3 font-medium text-slate-700">Acciones</th>
        </tr>
      </thead>
      <tbody className="divide-y divide-slate-100">
        {data.items.map((r) => (
          <tr key={r.id} className="hover:bg-slate-50">
            <td className="px-4 py-3">{r.reference || '—'}</td>
            <td className="px-4 py-3 font-mono text-xs">{r.resource_id.slice(0, 8)}…</td>
            <td className="px-4 py-3 text-right">{r.quantity}</td>
            <td className="px-4 py-3">
              {r.status === 'pending' ? (
                <Badge variant="yellow">Pendiente</Badge>
              ) : r.status === 'confirmed' ? (
                <Badge variant="blue">Confirmada</Badge>
              ) : r.status === 'fulfilled' ? (
                <Badge variant="green">Cumplida</Badge>
              ) : (
                <Badge variant="gray">Cancelada</Badge>
              )}
            </td>
            <td className="px-4 py-3">
              {r.needed_by ? new Date(r.needed_by).toLocaleDateString('es-ES') : '—'}
            </td>
            <td className="px-4 py-3 text-right">
              {r.status === 'pending' && (
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => cancelMutation.mutate(r.id)}
                  disabled={cancelMutation.isPending}
                >
                  Cancelar
                </Button>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

