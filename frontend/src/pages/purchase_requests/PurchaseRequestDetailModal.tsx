import { useState } from 'react'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Modal } from '../../components/ui/Modal'
import { QuotesSection } from '../../components/purchase_requests/QuotesSection'
import { ReceiveModal } from '../../components/purchase_requests/ReceiveModal'
import { useSendToSuppliers } from '../../hooks/useSupplierQuotes'
import {
  usePurchaseRequest,
  useUpdateStatus,
} from '../../hooks/usePurchaseRequests'
import { PURCHASE_REQUEST_STATUSES } from '../../types/purchase_request'
import { Can } from '../../components/auth/Can'

interface Props {
  open: boolean
  requestId: string | null
  onClose: () => void
}

export function PurchaseRequestDetailModal({
  open,
  requestId,
  onClose,
}: Props) {
  const { data: request, isLoading } = usePurchaseRequest(requestId)
  const sendMutation = useSendToSuppliers()
  const updateStatusMutation = useUpdateStatus()
  const [receiveModalOpen, setReceiveModalOpen] = useState(false)

  if (!open || !requestId) return null

  if (isLoading) {
    return (
      <Modal
        open={open}
        onClose={onClose}
        title="Cargando..."
        footer={
          <Button variant="secondary" onClick={onClose}>
            Cerrar
          </Button>
        }
      >
        <p className="text-slate-500">Cargando solicitud...</p>
      </Modal>
    )
  }

  if (!request) {
    return (
      <Modal
        open={open}
        onClose={onClose}
        title="Error"
        footer={
          <Button variant="secondary" onClick={onClose}>
            Cerrar
          </Button>
        }
      >
        <p className="text-red-600">Solicitud no encontrada.</p>
      </Modal>
    )
  }

  const statusCfg = PURCHASE_REQUEST_STATUSES.find(
    (s) => s.value === request.status,
  )
  const variant = (statusCfg?.color ?? 'gray') as
    | 'gray'
    | 'yellow'
    | 'green'
    | 'red'
    | 'blue'

  const handleSend = async () => {
    if (!confirm('¿Enviar esta solicitud a proveedores?')) return
    try {
      await sendMutation.mutateAsync(request.id)
      alert('Solicitud enviada a proveedores.')
    } catch (err) {
      alert('Error al enviar: ' + (err as Error).message)
    }
  }

  const handleApprove = async () => {
    if (!confirm('¿Aprobar esta solicitud?')) return
    try {
      await updateStatusMutation.mutateAsync({
        id: request.id,
        status: 'approved',
      })
      alert('Solicitud aprobada.')
    } catch (err) {
      alert('Error al aprobar: ' + (err as Error).message)
    }
  }

  const handleReject = async () => {
    if (!confirm('¿Rechazar esta solicitud?')) return
    try {
      await updateStatusMutation.mutateAsync({
        id: request.id,
        status: 'cancelled',
      })
      alert('Solicitud rechazada.')
    } catch (err) {
      alert('Error al rechazar: ' + (err as Error).message)
    }
  }

  const handleComplete = async () => {
    if (!confirm('¿Marcar como completada?')) return
    try {
      await updateStatusMutation.mutateAsync({
        id: request.id,
        status: 'completed',
      })
      alert('Solicitud completada.')
    } catch (err) {
      alert('Error al completar: ' + (err as Error).message)
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`Solicitud ${request.code}`}
      size="xl"
      footer={
        <Button variant="secondary" onClick={onClose}>
          Cerrar
        </Button>
      }
    >
      <div className="space-y-5">
        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-600">Estado</span>
          <Badge variant={variant}>
            {statusCfg?.label ?? request.status}
          </Badge>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-600">Fecha requerida</span>
          <span>
            {request.needed_by
              ? new Date(request.needed_by).toLocaleDateString('es-ES')
              : '—'}
          </span>
        </div>

        <div>
          <span className="text-sm text-slate-600 block">Notas</span>
          <p className="text-slate-900 mt-1">{request.notes ?? '—'}</p>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-slate-700 mb-2">
            Líneas ({request.lines.length})
          </h3>
          {request.lines.length === 0 ? (
            <p className="text-sm text-slate-500 italic">Sin líneas</p>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="text-left px-3 py-2 font-medium text-slate-700">
                    Recurso
                  </th>
                  <th className="text-right px-3 py-2 font-medium text-slate-700">
                    Solicitado
                  </th>
                  <th className="text-right px-3 py-2 font-medium text-slate-700">
                    Recibido
                  </th>
                  <th className="text-right px-3 py-2 font-medium text-slate-700">
                    Pendiente
                  </th>
                  <th className="text-left px-3 py-2 font-medium text-slate-700">
                    Proveedor
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {request.lines.map((l) => {
                  const qty = parseFloat(l.quantity)
                  const received = parseFloat(l.quantity_received ?? '0')
                  const pending = qty - received
                  return (
                    <tr key={l.id}>
                      <td className="px-3 py-2 font-medium">
                        {l.resource_name}
                      </td>
                      <td className="px-3 py-2 text-right font-mono">
                        {l.quantity}
                      </td>
                      <td className="px-3 py-2 text-right text-green-600">
                        {l.quantity_received ?? '0'}
                      </td>
                      <td className="px-3 py-2 text-right text-yellow-600">
                        {pending.toFixed(4)}
                      </td>
                      <td className="px-3 py-2">
                        {l.supplier_name ?? '—'}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          )}
        </div>

        {request.status === 'draft' && (
          <div className="flex gap-2 justify-end border-t border-slate-200 pt-4">
            <Can module="purchase_request" action="aprobar">
              <Button
                onClick={handleSend}
                disabled={sendMutation.isPending}
              >
                {sendMutation.isPending
                  ? 'Enviando...'
                  : 'Enviar a proveedores'}
              </Button>
            </Can>
          </div>
        )}

        {request.status === 'quoted' && (
          <div className="flex gap-2 justify-end border-t border-slate-200 pt-4">
            <Can module="purchase_request" action="aprobar">
              <Button onClick={handleApprove}>Aprobar</Button>
              <Button variant="danger" onClick={handleReject}>
                Rechazar
              </Button>
            </Can>
          </div>
        )}

        {(request.status === 'approved' ||
          request.status === 'partially_received') && (
          <div className="flex gap-2 justify-end border-t border-slate-200 pt-4">
            <Can module="purchase_request" action="aprobar">
              <Button onClick={() => setReceiveModalOpen(true)}>
                Recibir mercancía
              </Button>
            </Can>
            {request.status === 'approved' && (
              <Can module="purchase_request" action="editar">
                <Button variant="secondary" onClick={handleComplete}>
                  Completar
                </Button>
              </Can>
            )}
          </div>
        )}

        {(request.status === 'pending' ||
          request.status === 'quoted' ||
          request.status === 'approved') && (
          <div className="border-t border-slate-200 pt-4">
            <QuotesSection
              requestId={request.id}
              lines={request.lines}
              canCreateQuote={
                request.status === 'pending' ||
                request.status === 'quoted'
              }
              canSelectQuote={request.status === 'quoted'}
            />
          </div>
        )}
      </div>

      <ReceiveModal
        open={receiveModalOpen}
        request={request}
        onClose={() => setReceiveModalOpen(false)}
      />
    </Modal>
  )
}
