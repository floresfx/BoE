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
  onArchive: (orderId: string) => void
  onAddAnnex: () => void
}

export function ProductionOrderCard({ order, onMarkException, onArchive, onAddAnnex }: Props) {
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
  const isFinished = order.status === 'completed' || order.status === 'cancelled' ||  ['not_executed', 'partial', 'with_deviation'].includes(order.status) || !!order.exception_type

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

      {/* NUEVO: Listado de Anexos */}
      {order.annexes && order.annexes.length > 0 && (
        <div className="mt-2 text-xs bg-blue-50 border border-blue-100 rounded p-2 space-y-1">
          <p className="font-semibold text-blue-800">Anexos:</p>
          {order.annexes.map((annex) => (
            <p key={annex.id} className="text-blue-700">
              • {annex.annex_type === 'quantity_adjustment' ? 'Ajuste cant.' : 
                 annex.annex_type === 'extra_resource' ? 'Insumo extra' : 'Otro'} 
              {annex.quantity ? ` (+${annex.quantity})` : ''}
              {annex.notes ? ` - ${annex.notes}` : ''}
            </p>
          ))}
        </div>
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

        {/* BOTONES DE EN PROGRESO (Anexo y Completar) */}
        {order.status === 'in_progress' && (
          <>
            <Button
              size="sm"
              variant="secondary"
              onClick={onAddAnnex}
              disabled={isBusy}
            >
              + Anexo
            </Button>
            <Button
              size="sm"
              onClick={handleComplete}
              disabled={isBusy}
            >
              {completeMutation.isPending ? 'Completando...' : 'Completar'}
            </Button>
          </>
        )}

      </div>
    </div>
  )
}