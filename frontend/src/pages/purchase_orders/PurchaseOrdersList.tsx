import { useState } from 'react'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import {
  useConfirmOrder,
  usePurchaseOrders,
} from '../../hooks/usePurchaseOrders'
import { ReceiveOrderModal } from './ReceiveOrderModal'

export function PurchaseOrdersList() {
  const { data, isLoading } = usePurchaseOrders()
  const confirmMutation = useConfirmOrder()
  const [receiving, setReceiving] = useState<string | null>(null)

  if (isLoading) {
    return <div className="p-8 text-center text-slate-500">Cargando órdenes...</div>
  }

  const items = data?.items ?? []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Órdenes de Compra</h1>
        <p className="text-sm text-slate-500 mt-1">
          Órdenes formales a proveedores generadas desde cotizaciones.
        </p>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        {items.length === 0 ? (
          <div className="p-8 text-center text-slate-500">
            No hay órdenes de compra. Genera una desde una cotización aceptada.
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Código</th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Proveedor</th>
                <th className="text-right px-4 py-3 font-medium text-slate-700">Total</th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Estado</th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Fecha</th>
                <th className="text-right px-4 py-3 font-medium text-slate-700">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((order) => (
                <tr key={order.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-mono text-xs">{order.code}</td>
                  <td className="px-4 py-3">{order.supplier_name}</td>
                  <td className="px-4 py-3 text-right font-medium">
                    ${Number(order.total).toFixed(2)} {order.currency_code}
                  </td>
                  <td className="px-4 py-3">
                    {order.status === 'draft' && <Badge variant="gray">Borrador</Badge>}
                    {order.status === 'confirmed' && <Badge variant="blue">Confirmada</Badge>}
                    {order.status === 'received' && <Badge variant="green">Recibida</Badge>}
                    {order.status === 'cancelled' && <Badge variant="red">Cancelada</Badge>}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {new Date(order.created_at).toLocaleDateString('es-ES')}
                  </td>
                  <td className="px-4 py-3 text-right space-x-2">
                    {order.status === 'draft' && (
                      <Button
                        size="sm"
                        onClick={() => confirmMutation.mutate(order.id)}
                        disabled={confirmMutation.isPending}
                      >
                        Confirmar
                      </Button>
                    )}
                    {order.status === 'confirmed' && (
                      <Button
                        size="sm"
                        onClick={() => setReceiving(order.id)}
                      >
                        Recibir
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {receiving && (
        <ReceiveOrderModal
          open={Boolean(receiving)}
          orderId={receiving}
          onClose={() => setReceiving(null)}
        />
      )}
    </div>
  )
}