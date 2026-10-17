import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Modal } from '../../components/ui/Modal'
import type { PurchaseRequest } from '../../types/purchase_request'
import { PURCHASE_REQUEST_STATUSES } from '../../types/purchase_request'

interface Props {
  open: boolean
  request: PurchaseRequest | null
  onClose: () => void
}

export function PurchaseRequestDetailModal({ open, request, onClose }: Props) {
  if (!request) return null

  const statusCfg = PURCHASE_REQUEST_STATUSES.find(
    (s) => s.value === request.status,
  )
  const variant = (statusCfg?.color ?? 'gray') as
    | 'gray'
    | 'yellow'
    | 'green'
    | 'red'
    | 'blue'

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`Solicitud ${request.code}`}
      footer={
        <Button variant="secondary" onClick={onClose}>
          Cerrar
        </Button>
      }
    >
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-600">Estado</span>
          <Badge variant={variant}>{statusCfg?.label ?? request.status}</Badge>
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
                    Cantidad
                  </th>
                  <th className="text-left px-3 py-2 font-medium text-slate-700">
                    Proveedor
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {request.lines.map((l) => (
                  <tr key={l.id}>
                    <td className="px-3 py-2">{l.resource_name}</td>
                    <td className="px-3 py-2 text-right font-mono">
                      {l.quantity}
                    </td>
                    <td className="px-3 py-2">{l.supplier_name ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </Modal>
  )
}