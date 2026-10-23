import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { StatusBadge } from '../../components/purchase_requests/StatusBadge'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Modal } from '../../components/ui/Modal'
import { Select } from '../../components/ui/Select'
import { Input } from '../../components/ui/Input'
import { usePurchaseRequest, useUpdateStatus } from '../../hooks/usePurchaseRequests'
import {
  useSupplierQuotes,
  useSendToSuppliers,
  useCreateSupplierQuote,
  useSelectSupplierQuote,
} from '../../hooks/useSupplierQuotes'
import { useSuppliers } from '../../hooks/useSuppliers'
import { useGenerateOrderFromQuote } from '../../hooks/usePurchaseOrders'

export function PurchaseRequestDetail() {
  const { requestId } = useParams<{ requestId: string }>()
  const { data, isLoading, error } = usePurchaseRequest(requestId ?? null)
  const { data: quotesData } = useSupplierQuotes(requestId ?? null)
  const { data: suppliersData } = useSuppliers({ limit: 500 })
  const updateStatus = useUpdateStatus()
  const sendToSuppliers = useSendToSuppliers()
  const createQuote = useCreateSupplierQuote()
  const selectQuote = useSelectSupplierQuote()
  const generateOrder = useGenerateOrderFromQuote()

  const [quoteModalOpen, setQuoteModalOpen] = useState(false)
  const [selectedLineId, setSelectedLineId] = useState('')
  const [selectedSupplierId, setSelectedSupplierId] = useState('')
  const [unitPrice, setUnitPrice] = useState('')
  const [leadTime, setLeadTime] = useState('')
  const [quoteError, setQuoteError] = useState<string | null>(null)

  if (!requestId) {
    return <div className="p-8 text-center text-red-600">Solicitud no especificada.</div>
  }
  if (isLoading) {
    return <div className="p-8 text-center text-slate-500">Cargando...</div>
  }
  if (error || !data) {
    return <div className="p-8 text-center text-red-600">Error al cargar la solicitud.</div>
  }

  const quotes = quotesData?.items ?? []



  const total_requested = data.lines.reduce((sum, l) => sum + parseFloat(l.quantity), 0)
  const total_received = data.lines.reduce((sum, l) => sum + parseFloat(l.quantity_received ?? '0'), 0)

  const handleStatusChange = async (newStatus: string) => {
    try {
      await updateStatus.mutateAsync({ id: requestId, status: newStatus as any })
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error al cambiar estado')
    }
  }

  const handleSendToSuppliers = async () => {
    try {
      await sendToSuppliers.mutateAsync(requestId)
      alert('Solicitud enviada a proveedores.')
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error al enviar')
    }
  }

  const handleCreateQuote = async (e: React.FormEvent) => {
    e.preventDefault()
    setQuoteError(null)
    if (!selectedLineId || !selectedSupplierId || !unitPrice) {
      setQuoteError('Completa todos los campos.')
      return
    }
    try {
      await createQuote.mutateAsync({
        requestId,
        payload: {
          line_id: selectedLineId,
          supplier_id: selectedSupplierId,
          unit_price: unitPrice,
          currency_code: 'USD',
          lead_time_days: leadTime ? Number(leadTime) : 0,
        },
      })
      setQuoteModalOpen(false)
      setSelectedLineId('')
      setSelectedSupplierId('')
      setUnitPrice('')
      setLeadTime('')
    } catch (err: any) {
      setQuoteError(err.response?.data?.detail || 'Error al crear cotización')
    }
  }

  const handleSelectQuote = async (quoteId: string) => {
    try {
      await selectQuote.mutateAsync({ requestId, quoteId })
      alert('Cotización seleccionada como aceptada.')
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error al seleccionar')
    }
  }

  const handleGenerateOrder = async (quoteId: string) => {
    try {
      await generateOrder.mutateAsync({ requestId, quoteId })
      alert('Orden de compra generada correctamente.')
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error al generar la orden.')
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <Link to="/purchase-requests" className="text-sm text-blue-600 hover:underline">
            ← Volver a solicitudes
          </Link>
          <h1 className="text-2xl font-bold text-slate-900 mt-2">{data.code}</h1>
          <div className="flex items-center gap-3 mt-2">
            <StatusBadge status={data.status} />
            <span className="text-sm text-slate-500">
              Creada {new Date(data.created_at).toLocaleDateString('es-ES')}
            </span>
          </div>
        </div>

        {/* Botones de estado */}
        <div className="flex gap-2">
          {data.status === 'draft' && (
            <Button onClick={handleSendToSuppliers} disabled={sendToSuppliers.isPending}>
              {sendToSuppliers.isPending ? 'Enviando...' : 'Enviar a proveedores'}
            </Button>
          )}
          {data.status === 'pending' && (
            <Button onClick={() => handleStatusChange('approved')} disabled={updateStatus.isPending}>
              Aprobar
            </Button>
          )}
          {data.status === 'approved' && (
            <Button onClick={() => handleStatusChange('completed')} disabled={updateStatus.isPending}>
              Completar
            </Button>
          )}
          {['draft', 'pending', 'approved'].includes(data.status) && (
            <Button variant="danger" onClick={() => handleStatusChange('cancelled')} disabled={updateStatus.isPending}>
              Cancelar
            </Button>
          )}
        </div>
      </div>

      {data.notes && (
        <div className="bg-slate-50 p-4 rounded-lg">
          <p className="text-sm text-slate-600"><strong>Notas:</strong> {data.notes}</p>
        </div>
      )}

      {/* KPIs */}
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
          <p className="text-2xl font-bold text-green-600">{total_received.toFixed(2)}</p>
        </div>
      </div>

      {/* Líneas */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <h2 className="text-lg font-semibold text-slate-900 px-4 py-3 border-b border-slate-200">
          Líneas de la solicitud
        </h2>
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-slate-700">Recurso</th>
              <th className="text-right px-4 py-3 font-medium text-slate-700">Solicitado</th>
              <th className="text-right px-4 py-3 font-medium text-slate-700">Recibido</th>
              <th className="text-right px-4 py-3 font-medium text-slate-700">Pendiente</th>
              <th className="text-left px-4 py-3 font-medium text-slate-700">Proveedor</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {data.lines.map((line) => {
              const qty = parseFloat(line.quantity)
              const received = parseFloat(line.quantity_received ?? '0')
              return (
                <tr key={line.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium">{line.resource_name}</td>
                  <td className="px-4 py-3 text-right">{line.quantity}</td>
                  <td className="px-4 py-3 text-right text-green-600">{line.quantity_received ?? '0'}</td>
                  <td className="px-4 py-3 text-right text-yellow-600">{(qty - received).toFixed(4)}</td>
                  <td className="px-4 py-3 text-slate-600">{line.supplier_name ?? '—'}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Cotizaciones */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200">
          <h2 className="text-lg font-semibold text-slate-900">
            Cotizaciones ({quotes.length})
          </h2>
          {['draft', 'pending', 'approved'].includes(data.status) && (
            <Button size="sm" onClick={() => setQuoteModalOpen(true)}>
              + Añadir cotización
            </Button>
          )}
        </div>

        {quotes.length === 0 ? (
          <div className="p-8 text-center text-slate-500">
            No hay cotizaciones. Añade una para poder generar la orden de compra.
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Proveedor</th>
                <th className="text-right px-4 py-3 font-medium text-slate-700">Precio</th>
                <th className="text-right px-4 py-3 font-medium text-slate-700">Lead Time</th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Estado</th>
                <th className="text-right px-4 py-3 font-medium text-slate-700">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {quotes.map((q) => (
                <tr key={q.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium">{q.supplier_name}</td>
                  <td className="px-4 py-3 text-right">${Number(q.unit_price).toFixed(2)} {q.currency_code}</td>
                  <td className="px-4 py-3 text-right">{q.lead_time_days} días</td>
                  <td className="px-4 py-3">
                    {q.status === 'pending' && <Badge variant="yellow">Pendiente</Badge>}
                    {q.status === 'accepted' && <Badge variant="green">Aceptada</Badge>}
                    {q.status === 'rejected' && <Badge variant="red">Rechazada</Badge>}
                  </td>
                  <td className="px-4 py-3 text-right space-x-2">
                    {q.status === 'pending' && (
                      <Button size="sm" onClick={() => handleSelectQuote(q.id)}>
                        Seleccionar
                      </Button>
                    )}
                    {q.status === 'accepted' && (
                      <Button size="sm" onClick={() => handleGenerateOrder(q.id)} disabled={generateOrder.isPending}>
                        Generar Orden
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Modal para crear cotización */}
      <Modal
        open={quoteModalOpen}
        onClose={() => setQuoteModalOpen(false)}
        title="Nueva cotización"
        footer={
          <>
            <Button variant="secondary" onClick={() => setQuoteModalOpen(false)}>Cancelar</Button>
            <Button type="submit" form="quote-form" disabled={createQuote.isPending}>Crear</Button>
          </>
        }
      >
        <form id="quote-form" onSubmit={handleCreateQuote} className="space-y-4">
          {quoteError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">{quoteError}</div>
          )}
          <Select label="Línea de la solicitud" value={selectedLineId} onChange={(e) => setSelectedLineId(e.target.value)}>
            <option value="">Selecciona una línea...</option>
            {data.lines.map((l) => (
              <option key={l.id} value={l.id}>{l.resource_name} ({l.quantity})</option>
            ))}
          </Select>
          <Select label="Proveedor" value={selectedSupplierId} onChange={(e) => setSelectedSupplierId(e.target.value)}>
            <option value="">Selecciona un proveedor...</option>
            {suppliersData?.items.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </Select>
          <Input label="Precio unitario" type="number" step="0.01" value={unitPrice} onChange={(e) => setUnitPrice(e.target.value)} />
          <Input label="Lead time (días)" type="number" value={leadTime} onChange={(e) => setLeadTime(e.target.value)} />
        </form>
      </Modal>
    </div>
  )
}