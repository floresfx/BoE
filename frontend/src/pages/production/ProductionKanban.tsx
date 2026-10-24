import { useState, useMemo } from 'react'
import { Button } from '../../components/ui/Button'
import { ProductionOrderCard } from './ProductionOrderCard'
import { NewProductionOrderModal } from './NewProductionOrderModal'
import { useProductionOrders } from '../../hooks/useProduction'
import type { ProductionOrder } from '../../types/production'
import { MarkExceptionModal } from './MarkExceptionModal'
import { CreateAnnexModal } from './CreateAnnexModal'

interface Column {
  status: string 
  label: string
  color: string
}

const COLUMNS: Column[] = [
  { status: 'draft', label: 'Borrador', color: 'bg-slate-100' },
  { status: 'planned', label: 'Planificado', color: 'bg-blue-100' },
  { status: 'in_progress', label: 'En progreso', color: 'bg-yellow-100' },
  { status: 'completed', label: 'Completado', color: 'bg-green-100' },
  { status: 'cancelled', label: 'Cancelado / Excepción', color: 'bg-red-100' },
]

export function ProductionKanban() {
  const { data, isLoading, error } = useProductionOrders()
  const [modalOpen, setModalOpen] = useState(false)
  const [orderToExcept, setOrderToExcept] = useState<ProductionOrder | null>(null)
  const [orderToAnnex, setOrderToAnnex] = useState<ProductionOrder | null>(null)

  // --- LÓGICA DE ARCHIVADO (localStorage) ---
  const [archivedIds, setArchivedIds] = useState<string[]>(() => {
    const saved = localStorage.getItem('boe_archived_orders')
    return saved ? JSON.parse(saved) : []
  })

  const handleArchive = (orderId: string) => {
    const newArchived = [...archivedIds, orderId]
    setArchivedIds(newArchived)
    localStorage.setItem('boe_archived_orders', JSON.stringify(newArchived))
  }
  // ------------------------------------------

  // Filtramos todas las órdenes para separar las archivadas de las activas
  const allOrders = data?.items ?? []
  const activeOrders = allOrders.filter(o => !archivedIds.includes(o.id))
  const archivedOrders = allOrders.filter(o => archivedIds.includes(o.id))

  // LÓGICA CLAVE: Si la orden tiene un estado de excepción, la mostramos en "Cancelado/Excepción"
  const ordersByStatus = (columnStatus: string) => {
    return activeOrders.filter((o) => {
      const isExceptionState = ['not_executed', 'partial', 'with_deviation'].includes(o.status)
      
      if (columnStatus === 'cancelled') {
        // Aquí mandamos las canceladas normales Y las que tuvieron excepción
        return o.status === 'cancelled' || isExceptionState
      }
      
      return o.status === columnStatus
    })
  }

  // --- LÓGICA DE HISTORIAL Y FILTRO DE FECHAS ---
  const [filterDate, setFilterDate] = useState('')
  
  const filteredHistory = useMemo(() => {
    if (!filterDate) return archivedOrders
    return archivedOrders.filter(o => {
      // Comparamos la fecha del filtro con la fecha de fin o creación
      const dateToCompare = o.end_date ? new Date(o.end_date).toISOString().split('T')[0] : new Date(o.created_at).toISOString().split('T')[0]
      return dateToCompare === filterDate
    })
  }, [archivedOrders, filterDate])

  return (
    <div className="space-y-8">
      {/* HEADER */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Producción</h1>
          <p className="text-sm text-slate-500 mt-1">Tablero Kanban de órdenes de producción.</p>
        </div>
        <Button onClick={() => setModalOpen(true)}>+ Nueva orden</Button>
      </div>

      {/* KANBAN ACTIVO */}
      {isLoading ? (
        <div className="p-8 text-center text-slate-500">Cargando...</div>
      ) : error ? (
        <div className="p-8 text-center text-red-600">Error al cargar</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {COLUMNS.map((column) => {
            const columnOrders = ordersByStatus(column.status)
            return (
              <div key={column.status} className={`rounded-lg p-3 ${column.color} min-h-[200px]`}>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-slate-900 text-sm">{column.label}</h3>
                  {column.status === 'cancelled' && columnOrders.length > 0 && (
                      <button 
                        onClick={() => {
                          columnOrders.forEach(o => handleArchive(o.id));
                        }}
                        className="text-[10px] text-red-600 hover:underline"
                        title="Archivar todas"
                      >
                        Limpiar
                      </button>
                    )}
                  <span className="text-xs bg-white/60 px-2 py-0.5 rounded-full">{columnOrders.length}</span>
                </div>
                <div className="space-y-2">
                  {columnOrders.length === 0 ? (
                    <p className="text-xs text-slate-500 italic text-center py-4">Sin órdenes</p>
                  ) : (
                    columnOrders.map((order) => (
                      <ProductionOrderCard 
                        key={order.id} 
                        order={order} 
                        onMarkException={() => setOrderToExcept(order)}
                        onArchive={handleArchive} // <-- Pasamos la función
                        onAddAnnex={() => setOrderToAnnex(order)} 
                      />
                    ))
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* HISTORIAL DE ARCHIVADOS */}
      <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-4 gap-4">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Historial de Producción</h2>
            <p className="text-sm text-slate-500">Órdenes completadas, canceladas o con excepciones.</p>
          </div>
          
          <div className="flex items-center gap-2">
            <label className="text-sm text-slate-600">Filtrar por fecha:</label>
            <input 
              type="date" 
              className="border border-slate-300 rounded px-3 py-1.5 text-sm"
              value={filterDate}
              onChange={(e) => setFilterDate(e.target.value)}
            />
            {filterDate && (
              <Button variant="secondary" size="sm" onClick={() => setFilterDate('')}>
                Limpiar
              </Button>
            )}
          </div>
        </div>

        {filteredHistory.length === 0 ? (
          <p className="text-sm text-slate-500 text-center py-6">No hay órdenes archivadas que coincidan con la búsqueda.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-slate-50 text-slate-600 border-b border-slate-200">
                <tr>
                  <th className="px-4 py-3 font-medium">Código</th>
                  <th className="px-4 py-3 font-medium">Bundle</th>
                  <th className="px-4 py-3 font-medium">Cantidad</th>
                  <th className="px-4 py-3 font-medium">Estado Final</th>
                  <th className="px-4 py-3 font-medium">Fecha Cierre</th>
                  <th className="px-4 py-3 font-medium">Notas</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredHistory.map(order => (
                  <tr key={order.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 font-mono text-xs">{order.code}</td>
                    <td className="px-4 py-3 font-medium text-slate-900">{order.bundle_name}</td>
                    <td className="px-4 py-3">{order.quantity}</td>
                    <td className="px-4 py-3">
                      <span className="capitalize">
                        {order.status === 'with_deviation' ? 'Desviación' : order.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {order.end_date ? new Date(order.end_date).toLocaleDateString('es-ES') : '-'}
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-500 max-w-[200px] truncate" title={order.exception_notes || order.notes || ''}>
                      {order.exception_notes || order.notes || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <NewProductionOrderModal open={modalOpen} onClose={() => setModalOpen(false)} />
      <MarkExceptionModal open={!!orderToExcept} onClose={() => setOrderToExcept(null)} order={orderToExcept} />
        {/* AQUÍ VA EL MODAL DE ANEXOS */}
      
      <CreateAnnexModal
        open={!!orderToAnnex}
        onClose={() => setOrderToAnnex(null)}
        order={orderToAnnex}
      />
    </div>
  )
}