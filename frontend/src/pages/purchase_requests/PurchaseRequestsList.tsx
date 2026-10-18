import { useState } from 'react'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Select } from '../../components/ui/Select'
import {
  useDeletePurchaseRequest,
  usePurchaseRequests,
  useUpdateStatus,
} from '../../hooks/usePurchaseRequests'
import type {
  PurchaseRequest,
  PurchaseRequestStatus,
} from '../../types/purchase_request'
import { PURCHASE_REQUEST_STATUSES } from '../../types/purchase_request'
import { ConfirmDialog } from '../resources/ConfirmDialog'
import { PurchaseRequestDetailModal } from './PurchaseRequestDetailModal'
import { PurchaseRequestForm } from './PurchaseRequestForm'
import { PurchaseRequestFromBundleModal } from './PurchaseRequestFromBundleModal'
import { Can } from '../../components/auth/Can'

const statusBadge = (s: PurchaseRequestStatus) => {
  const cfg = PURCHASE_REQUEST_STATUSES.find((x) => x.value === s)
  const variant = (cfg?.color ?? 'gray') as
    | 'gray'
    | 'yellow'
    | 'green'
    | 'red'
    | 'blue'
  return <Badge variant={variant}>{cfg?.label ?? s}</Badge>
}

export function PurchaseRequestsList() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<PurchaseRequestStatus | ''>('')
  const [formOpen, setFormOpen] = useState(false)
  const [fromBundleOpen, setFromBundleOpen] = useState(false)
  const [viewingId, setViewingId] = useState<string | null>(null)
  const [deleting, setDeleting] = useState<PurchaseRequest | null>(null)

  const { data, isLoading, error } = usePurchaseRequests({
    search: search || undefined,
    status: statusFilter || undefined,
  })
  const deleteMutation = useDeletePurchaseRequest()
  const statusMutation = useUpdateStatus()

  const items = data?.items ?? []
  const total = data?.total ?? 0

  const handleConfirmDelete = async () => {
    if (!deleting) return
    try {
      await deleteMutation.mutateAsync(deleting.id)
      setDeleting(null)
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      alert(apiErr.response?.data?.detail ?? 'Error al borrar')
    }
  }

  const handleStatusChange = async (
    req: PurchaseRequest,
    newStatus: PurchaseRequestStatus,
  ) => {
    try {
      await statusMutation.mutateAsync({ id: req.id, status: newStatus })
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      alert(apiErr.response?.data?.detail ?? 'Error al cambiar estado')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Solicitudes de compra
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Solicitudes de recursos a proveedores.
          </p>
        </div>
        <div className="space-x-2">
         <Can module="purchase_request" action="crear">
          <Button variant="secondary" onClick={() => setFromBundleOpen(true)}>
            + Desde paquete
          </Button>
        </Can>
          <Can module="purchase_request" action="crear">
            <Button onClick={() => setFormOpen(true)}>+ Nueva solicitud</Button>
          </Can>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Input
          placeholder="Buscar por código..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <Select
          value={statusFilter}
          onChange={(e) =>
            setStatusFilter(e.target.value as PurchaseRequestStatus | '')
          }
        >
          <option value="">Todos los estados</option>
          {PURCHASE_REQUEST_STATUSES.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </Select>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-slate-500">Cargando...</div>
        ) : error ? (
          <div className="p-8 text-center text-red-600">Error al cargar</div>
        ) : items.length === 0 ? (
          <div className="p-8 text-center text-slate-500">
            No hay solicitudes. Crea la primera con los botones de arriba.
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-slate-700">
                  Código
                </th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">
                  Estado
                </th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">
                  Líneas
                </th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">
                  Necesario
                </th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">
                  Creada
                </th>
                <th className="text-right px-4 py-3 font-medium text-slate-700">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((r) => (
                <tr key={r.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-mono text-xs text-slate-600">
                    {r.code}
                  </td>
                  <td className="px-4 py-3">{statusBadge(r.status)}</td>
                  <td className="px-4 py-3 text-slate-600">
                    {r.lines.length} línea(s)
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {r.needed_by
                      ? new Date(r.needed_by).toLocaleDateString('es-ES')
                      : '—'}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {new Date(r.created_at).toLocaleDateString('es-ES')}
                  </td>
                  <td className="px-4 py-3 text-right space-x-2 whitespace-nowrap">
                  <Can module="purchase_request" action="ver">
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => setViewingId(r.id)}
                    >
                      Ver
                    </Button>
                  </Can>
                  {r.status === 'draft' && (
                    <Can module="purchase_request" action="editar">
                      <Button
                        size="sm"
                        onClick={() => handleStatusChange(r, 'pending')}
                      >
                        Enviar
                      </Button>
                    </Can>
                  )}
                  {r.status === 'pending' && (
                    <>
                      <Can module="purchase_request" action="aprobar">
                        <Button
                          size="sm"
                          onClick={() => handleStatusChange(r, 'approved')}
                        >
                          Aprobar
                        </Button>
                        <Button
                          size="sm"
                          variant="danger"
                          onClick={() => handleStatusChange(r, 'cancelled')}
                        >
                          Rechazar
                        </Button>
                      </Can>
                    </>
                  )}
                  {r.status === 'approved' && (
                    <Can module="purchase_request" action="aprobar">
                      <Button
                        size="sm"
                        onClick={() => handleStatusChange(r, 'completed')}
                      >
                        Completar
                      </Button>
                    </Can>
                  )}
                  {r.status === 'draft' && (
                    <Can module="purchase_request" action="eliminar">
                      <Button
                        size="sm"
                        variant="danger"
                        onClick={() => setDeleting(r)}
                      >
                        Borrar
                      </Button>
                    </Can>
                  )}
                </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <p className="text-xs text-slate-500 text-right">
        Mostrando {items.length} de {total}
      </p>

      <PurchaseRequestForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
      />

      <PurchaseRequestFromBundleModal
        open={fromBundleOpen}
        onClose={() => setFromBundleOpen(false)}
      />

      <PurchaseRequestDetailModal
        open={Boolean(viewingId)}
        requestId={viewingId}
        onClose={() => setViewingId(null)}
      />

      <ConfirmDialog
        open={Boolean(deleting)}
        title="Borrar solicitud"
        message={`¿Borrar "${deleting?.code}"? Esta acción no se puede deshacer.`}
        confirmLabel="Borrar"
        isLoading={deleteMutation.isPending}
        onConfirm={handleConfirmDelete}
        onCancel={() => setDeleting(null)}
      />
    </div>
  )
}