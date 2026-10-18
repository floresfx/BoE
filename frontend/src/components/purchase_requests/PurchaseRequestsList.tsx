import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Can } from '../../components/auth/Can'
import { StatusBadge } from '../../components/purchase_requests/StatusBadge'
import type { PurchaseRequestStatus } from '../../types/purchase_request'
import {
  usePurchaseRequests,
  useDeletePurchaseRequest,
} from '../../hooks/usePurchaseRequests'
import { PurchaseRequestDetailModal } from '../../components/purchase_requests/PurchaseRequestDetailModal'
import type { PurchaseRequest } from '../../types/purchase_request'

export function PurchaseRequestsList() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [selectedRequest, setSelectedRequest] =  useState<PurchaseRequest | null>(null)
  const [statusFilter, setStatusFilter] = useState<
    PurchaseRequestStatus | ''
    >('')

  const { data, isLoading, error } = usePurchaseRequests({
  search: search || undefined,
  status: statusFilter || undefined,
  })
  const deleteMutation = useDeletePurchaseRequest()

  const items = data?.items ?? []
  const total = data?.total ?? 0

  const handleDelete = async (id: string) => {
    if (!confirm('¿Eliminar esta solicitud? Solo se puede si está en borrador.')) {
      return
    }
    try {
      await deleteMutation.mutateAsync(id)
    } catch (err) {
      alert('Error: ' + (err as Error).message)
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
            Solicitudes creadas a partir de bundles o manualmente.
          </p>
        </div>
        <Can module="purchase_request" action="crear">
          <Button onClick={() => navigate('/purchase-requests/new')}>
            + Nueva solicitud
          </Button>
        </Can>
      </div>

      <div className="bg-white rounded-lg shadow p-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Input
          placeholder="Buscar por código..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
        value={statusFilter}
        onChange={(e) =>
            setStatusFilter(e.target.value as PurchaseRequestStatus | '')
        }
        className="rounded-md border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">Todos los estados</option>
          <option value="draft">Borrador</option>
          <option value="pending">Enviada</option>
          <option value="quoted">Cotizada</option>
          <option value="approved">Aprobada</option>
          <option value="ordered">Ordenada</option>
          <option value="partially_received">Parcial</option>
          <option value="completed">Completada</option>
          <option value="cancelled">Cancelada</option>
        </select>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-slate-500">Cargando...</div>
        ) : error ? (
          <div className="p-8 text-center text-red-600">Error al cargar</div>
        ) : items.length === 0 ? (
          <div className="p-8 text-center text-slate-500">
            No hay solicitudes. Crea la primera con el botón de arriba.
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
                  Creada
                </th>
                <th className="text-right px-4 py-3 font-medium text-slate-700">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((req) => (
                <tr key={req.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-mono text-xs text-slate-600">
                    {req.code}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={req.status} />
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {req.lines.length} línea(s)
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {new Date(req.created_at).toLocaleDateString('es-ES')}
                  </td>
                  <td className="px-4 py-3 text-right space-x-2 whitespace-nowrap">
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => setSelectedRequest(req)}
                    >
                      Ver
                    </Button>
                    {req.status === 'draft' && (
                      <Can module="purchase_request" action="eliminar">
                        <Button
                          size="sm"
                          variant="danger"
                          onClick={() => handleDelete(req.id)}
                        >
                          Eliminar
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
      <PurchaseRequestDetailModal
        open={Boolean(selectedRequest)}
        request={selectedRequest}
        onClose={() => setSelectedRequest(null)}
      />
    </div>
  )
}