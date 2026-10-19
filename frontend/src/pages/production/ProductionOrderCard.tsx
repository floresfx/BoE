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
}

export function ProductionOrderCard({ order }: Props) {
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

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-3 space-y-2">
      <div className="flex items-center justify-between">
        <span className="font-mono text-xs text-slate-500">{order.code}</span>
        <Badge variant="gray">{order.quantity}</Badge>
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

      {order.notes && (
        <p className="text-xs text-slate-600 italic">{order.notes}</p>
      )}

      <div className="flex gap-2 justify-end pt-2 border-t border-slate-100">
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