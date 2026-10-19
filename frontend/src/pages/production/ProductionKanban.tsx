import { useState } from 'react'
import { Button } from '../../components/ui/Button'
import { ProductionOrderCard } from './ProductionOrderCard'
import { NewProductionOrderModal } from './NewProductionOrderModal'
import { useProductionOrders } from '../../hooks/useProduction'
import type { ProductionOrderStatus } from '../../types/production'

interface Column {
  status: ProductionOrderStatus
  label: string
  color: string
}

const COLUMNS: Column[] = [
  { status: 'draft', label: 'Borrador', color: 'bg-slate-100' },
  { status: 'planned', label: 'Planificado', color: 'bg-blue-100' },
  { status: 'in_progress', label: 'En progreso', color: 'bg-yellow-100' },
  { status: 'completed', label: 'Completado', color: 'bg-green-100' },
  { status: 'cancelled', label: 'Cancelado', color: 'bg-red-100' },
]

export function ProductionKanban() {
  const { data, isLoading, error } = useProductionOrders()
  const [modalOpen, setModalOpen] = useState(false)

  const orders = data?.items ?? []

  const ordersByStatus = (status: ProductionOrderStatus) =>
    orders.filter((o) => o.status === status)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Producción</h1>
          <p className="text-sm text-slate-500 mt-1">
            Tablero Kanban de órdenes de producción.
          </p>
        </div>
        <Button onClick={() => setModalOpen(true)}>
          + Nueva orden
        </Button>
      </div>

      {isLoading ? (
        <div className="p-8 text-center text-slate-500">Cargando...</div>
      ) : error ? (
        <div className="p-8 text-center text-red-600">Error al cargar</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {COLUMNS.map((column) => {
            const columnOrders = ordersByStatus(column.status)
            return (
              <div
                key={column.status}
                className={`rounded-lg p-3 ${column.color} min-h-[200px]`}
              >
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-slate-900 text-sm">
                    {column.label}
                  </h3>
                  <span className="text-xs bg-white/60 px-2 py-0.5 rounded-full">
                    {columnOrders.length}
                  </span>
                </div>

                <div className="space-y-2">
                  {columnOrders.length === 0 ? (
                    <p className="text-xs text-slate-500 italic text-center py-4">
                      Sin órdenes
                    </p>
                  ) : (
                    columnOrders.map((order) => (
                      <ProductionOrderCard key={order.id} order={order} />
                    ))
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      <NewProductionOrderModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
      />
    </div>
  )
}