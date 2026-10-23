import { Button } from '../../components/ui/Button'
import { Badge } from '../../components/ui/Badge'
import {
  useStartProductionOrder,
  useCompleteProductionOrder,
  useUpdateProductionOrderStatus,
} from '../../hooks/useProduction'
import type { ProductionOrder } from '../../types/production'

interface Props {
  order: ProductionOrder
  onMarkException: () => void
  onArchive: (orderId: string) => void // <-- ¡AQUÍ ESTABA EL ERROR QUE FALTABA!
}

export function ProductionOrderCard({ order, onMarkException, onArchive }: Props) {
  const startMutation = useStartProductionOrder()
  const completeMutation = useCompleteProductionOrder()
  const updateStatusMutation = useUpdateProductionOrderStatus()

  const isBusy =
    startMutation.isPending ||
    completeMutation.isPending ||
    updateStatusMutation.isPending

  const handlePlan = async () => {
    if (isBusy) return
    try {
      await updateStatusMutation.mutateAsync({
        orderId: order.id,
        status: 'planned',
      })
    } catch (err) {
      alert('Error al planificar: ' + (err as Error).message)
    }
  }

  const handleStart = async () => {
    if (isBusy) return
    if (!confirm(`¿Iniciar producción de ${order.code}?`)) return
    try {
      await startMutation.mutateAsync(order.id)
    } catch (err) {
      alert('Error al iniciar: ' + (err as Error).message)
    }
  }

  const handleComplete = async () => {
    if (isBusy) return
    if (!confirm(`¿Completar producción de ${order.code}?`)) return
    try {
      await completeMutation.mutateAsync(order.id)
    } catch (err) {
      alert('Error al completar: ' + (err as Error).message)
    }
  }

  const renderExceptionBadge = () => {
    if (!order.exception_type) return null
    switch (order.exception_type) {
      case 'not_executed': return <Badge variant="red">No ejecutada</Badge>
      case 'partial': return <Badge variant="yellow">Parcial</Badge>
      case 'with_deviation': return <Badge variant="red">Desviación</Badge> 
      default: return null
    }
  }  

  // Si la orden ya terminó su ciclo (completada, cancelada o con excepción)
  const isFinished = order.status === 'completed' || order.status === 'cancelled' || !!order.exception_type

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-3 space-y-2">
      <div className="flex items-center justify-between">
        <span className="font-mono text-xs text-slate-500">{order.code}</span>
        <div className="flex gap-1 items-center">
          {renderExceptionBadge()}
          <Badge variant="gray">{order.quantity}</Badge>
        </div>
      </div>

      <p className="font-medium text-slate-900">{order.bundle_name}</p>

      {order.start_date && (
        <p className="text-xs text-slate-500">
          Inicio: {new Date(order.start_date).toLocaleDateString('es-ES')}
        </p>
      )}

      {order.end_date && (
        <p className="text-xs text-slate-500">
          Fin: {new Date(order.end_date).toLocaleDateString('es-ES')}
        </p>
      )}

      {order.exception_notes && (
        <p className="text-xs text-red-600 bg-red-50 p-1 rounded">Motivo: {order.exception_notes}</p>
      )}

      {order.notes && (
        <p className="text-xs text-slate-600 italic">{order.notes}</p>
      )}

      <div className="flex flex-wrap gap-2 justify-end pt-2 border-t border-slate-100">
        
        {/* NUEVO BOTÓN DE ARCHIVAR */}
        {isFinished && (
          <Button
            size="sm"
            variant="secondary"
            onClick={() => onArchive(order.id)}
            className="bg-slate-100 hover:bg-slate-200 text-slate-700"
          >
            Archivar
          </Button>
        )}

        {(order.status === 'planned' || order.status === 'in_progress') && !order.exception_type && (
          <Button
            size="sm"
            variant="secondary"
            onClick={onMarkException}
            disabled={isBusy}
          >
            Excepción
          </Button>
        )}

        {order.status === 'draft' && (
          <Button
            size="sm"
            variant="secondary"
            onClick={handlePlan}
            disabled={isBusy}
          >
            Planificar
          </Button>
        )}
        {(order.status === 'draft' || order.status === 'planned') && (
          <Button
            size="sm"
            onClick={handleStart}
            disabled={isBusy}
          >
            {startMutation.isPending ? 'Iniciando...' : 'Iniciar'}
          </Button>
        )}
        {order.status === 'in_progress' && (
          <Button
            size="sm"
            onClick={handleComplete}
            disabled={isBusy}
          >
            {completeMutation.isPending ? 'Completando...' : 'Completar'}
          </Button>
        )}
      </div>
    </div>
  )
}