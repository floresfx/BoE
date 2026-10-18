import { Link, useParams } from 'react-router-dom'
import { StatusBadge } from '../../components/purchase_requests/StatusBadge'
import { usePurchaseRequest } from '../../hooks/usePurchaseRequests'

export function PurchaseRequestDetail() {
  const { requestId } = useParams<{ requestId: string }>()
  const { data, isLoading, error } = usePurchaseRequest(requestId ?? null)

  if (!requestId) {
    return (
      <div className="p-8 text-center text-red-600">
        Solicitud no especificada.
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="p-8 text-center text-slate-500">Cargando...</div>
    )
  }

  if (error || !data) {
    return (
      <div className="p-8 text-center text-red-600">
        Error al cargar la solicitud.
      </div>
    )
  }

  const total_requested = data.lines.reduce(
    (sum, l) => sum + parseFloat(l.quantity),
    0,
  )
  const total_received = data.lines.reduce(
    (sum, l) => sum + parseFloat(l.quantity_received ?? '0'),
    0,
  )

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <Link
            to="/purchase-requests"
            className="text-sm text-blue-600 hover:underline"
          >
            ← Volver a solicitudes
          </Link>
          <h1 className="text-2xl font-bold text-slate-900 mt-2">
            {data.code}
          </h1>
          <div className="flex items-center gap-3 mt-2">
            <StatusBadge status={data.status} />
            <span className="text-sm text-slate-500">
              Creada {new Date(data.created_at).toLocaleDateString('es-ES')}
            </span>
          </div>
        </div>
      </div>

      {data.notes && (
        <div className="bg-slate-50 p-4 rounded-lg">
          <p className="text-sm text-slate-600">
            <strong>Notas:</strong> {data.notes}
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-slate-500">Líneas</p>
          <p className="text-2xl font-bold">{data.lines.length}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-slate-500">Total solicitado</p>
          <p className="text-2xl font-bold">{total_requested.toFixed(2)}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-slate-500">Total recibido</p>
          <p className="text-2xl font-bold text-green-600">
            {total_received.toFixed(2)}
          </p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-slate-700">
                Recurso
              </th>
              <th className="text-right px-4 py-3 font-medium text-slate-700">
                Solicitado
              </th>
              <th className="text-right px-4 py-3 font-medium text-slate-700">
                Recibido
              </th>
              <th className="text-right px-4 py-3 font-medium text-slate-700">
                Pendiente
              </th>
              <th className="text-left px-4 py-3 font-medium text-slate-700">
                Proveedor
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {data.lines.map((line) => {
              const qty = parseFloat(line.quantity)
              const received = parseFloat(line.quantity_received ?? '0')
              const pending = qty - received
              return (
                <tr key={line.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium">
                    {line.resource_name}
                  </td>
                  <td className="px-4 py-3 text-right">{line.quantity}</td>
                  <td className="px-4 py-3 text-right text-green-600">
                    {line.quantity_received ?? '0'}
                  </td>
                  <td className="px-4 py-3 text-right text-yellow-600">
                    {pending.toFixed(4)}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {line.supplier_name ?? '—'}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}