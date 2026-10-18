import { useEffect, useState } from 'react'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { Modal } from '../ui/Modal'
import { useReceivePurchaseRequest } from '../../hooks/usePurchaseReceive'
import { useWarehouses } from '../../hooks/useInventory'
import type {
  PurchaseRequest,
  PurchaseRequestLine,
} from '../../types/purchase_request'

interface Props {
  open: boolean
  request: PurchaseRequest | null
  onClose: () => void
}

interface LineState {
  line: PurchaseRequestLine
  received_quantity: string
  lot_code: string
  unit_cost: string
  expiration: string
}

export function ReceiveModal({ open, request, onClose }: Props) {
  const { data: warehouses } = useWarehouses({ is_active: true })
  const receiveMutation = useReceivePurchaseRequest()

  const [warehouseId, setWarehouseId] = useState('')
  const [notes, setNotes] = useState('')
  const [lines, setLines] = useState<LineState[]>([])

  // Inicializar líneas cuando se abre el modal
  useEffect(() => {
    if (open && request) {
      setLines(
        request.lines
          .filter(
            (l) =>
              parseFloat(l.quantity) -
                parseFloat(l.quantity_received ?? '0') >
              0,
          )
          .map((l) => {
            const pending =
              parseFloat(l.quantity) -
              parseFloat(l.quantity_received ?? '0')
            return {
              line: l,
              received_quantity: pending.toFixed(4),
              lot_code: '',
              unit_cost: '',
              expiration: '',
            }
          }),
      )
      setWarehouseId('')
      setNotes('')
    }
  }, [open, request])

  if (!request) return null

  const updateLine = (
    lineId: string,
    field: keyof Omit<LineState, 'line'>,
    value: string,
  ) => {
    setLines((prev) =>
      prev.map((l) =>
        l.line.id === lineId ? { ...l, [field]: value } : l,
      ),
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!warehouseId) {
      alert('Selecciona un almacén destino.')
      return
    }

    // Validaciones
    for (const l of lines) {
      const received = parseFloat(l.received_quantity) || 0
      if (received <= 0) {
        alert(
          `Línea "${l.line.resource_name}": la cantidad a recibir debe ser > 0.`,
        )
        return
      }
      if (!l.lot_code.trim()) {
        alert(`Línea "${l.line.resource_name}": el código de lote es obligatorio.`)
        return
      }
      const pending =
        parseFloat(l.line.quantity) -
        parseFloat(l.line.quantity_received ?? '0')
      if (received > pending) {
        alert(
          `Línea "${l.line.resource_name}": recibes ${received} pero solo quedan ${pending.toFixed(4)}.`,
        )
        return
      }
    }

    try {
      const result = await receiveMutation.mutateAsync({
        requestId: request.id,
        payload: {
          warehouse_id: warehouseId,
          notes: notes || null,
          lines: lines.map((l) => ({
            line_id: l.line.id,
            received_quantity: l.received_quantity,
            lot_code: l.lot_code,
            unit_cost: l.unit_cost || null,
            expiration: l.expiration || null,
            notes: null,
          })),
        },
      })
      alert(result.message)
      onClose()
    } catch (err) {
      const apiErr = err as {
        response?: { data?: { detail?: string } }
      }
      alert(
        apiErr.response?.data?.detail ?? 'Error al recibir mercancía',
      )
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`Recibir mercancía - ${request.code}`}
      size="xl"
      footer={
        <>
          <Button
            variant="secondary"
            onClick={onClose}
            disabled={receiveMutation.isPending}
          >
            Cancelar
          </Button>
          <Button
            type="submit"
            form="receive-form"
            disabled={receiveMutation.isPending}
          >
            {receiveMutation.isPending ? 'Recibiendo...' : 'Recibir'}
          </Button>
        </>
      }
    >
      <form
        id="receive-form"
        onSubmit={handleSubmit}
        className="space-y-4"
      >
        {/* Warehouse */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Almacén destino
          </label>
          <select
            value={warehouseId}
            onChange={(e) => setWarehouseId(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            required
          >
            <option value="">— Selecciona —</option>
            {warehouses?.items.map((w) => (
              <option key={w.id} value={w.id}>
                {w.name} ({w.code})
              </option>
            ))}
          </select>
        </div>

        {/* Tabla de líneas */}
        <div>
          <h3 className="text-sm font-semibold text-slate-700 mb-2">
            Líneas a recibir ({lines.length})
          </h3>
          {lines.length === 0 ? (
            <p className="text-sm text-slate-500 italic">
              No hay líneas pendientes de recibir.
            </p>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="text-left px-2 py-2 font-medium text-slate-700">
                    Recurso
                  </th>
                  <th className="text-right px-2 py-2 font-medium text-slate-700">
                    Pendiente
                  </th>
                  <th className="text-right px-2 py-2 font-medium text-slate-700">
                    Recibir
                  </th>
                  <th className="text-left px-2 py-2 font-medium text-slate-700">
                    Lote *
                  </th>
                  <th className="text-right px-2 py-2 font-medium text-slate-700">
                    Costo unit.
                  </th>
                  <th className="text-left px-2 py-2 font-medium text-slate-700">
                    Caducidad
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {lines.map((l) => {
                  const pending =
                    parseFloat(l.line.quantity) -
                    parseFloat(l.line.quantity_received ?? '0')
                  return (
                    <tr key={l.line.id}>
                      <td className="px-2 py-2 font-medium">
                        {l.line.resource_name}
                      </td>
                      <td className="px-2 py-2 text-right text-yellow-600">
                        {pending.toFixed(4)}
                      </td>
                      <td className="px-2 py-2 text-right">
                        <input
                          type="number"
                          min={0.0001}
                          step="any"
                          value={l.received_quantity}
                          onChange={(e) =>
                            updateLine(
                              l.line.id,
                              'received_quantity',
                              e.target.value,
                            )
                          }
                          className="w-24 rounded border border-slate-300 px-2 py-1 text-sm text-right"
                        />
                      </td>
                      <td className="px-2 py-2">
                        <input
                          type="text"
                          value={l.lot_code}
                          onChange={(e) =>
                            updateLine(
                              l.line.id,
                              'lot_code',
                              e.target.value,
                            )
                          }
                          placeholder="LOT-2026-001"
                          className="w-32 rounded border border-slate-300 px-2 py-1 text-sm"
                          required
                        />
                      </td>
                      <td className="px-2 py-2 text-right">
                        <input
                          type="number"
                          min={0}
                          step="any"
                          value={l.unit_cost}
                          onChange={(e) =>
                            updateLine(
                              l.line.id,
                              'unit_cost',
                              e.target.value,
                            )
                          }
                          placeholder="opcional"
                          className="w-24 rounded border border-slate-300 px-2 py-1 text-sm text-right"
                        />
                      </td>
                      <td className="px-2 py-2">
                        <input
                          type="date"
                          value={l.expiration}
                          onChange={(e) =>
                            updateLine(
                              l.line.id,
                              'expiration',
                              e.target.value,
                            )
                          }
                          className="rounded border border-slate-300 px-2 py-1 text-sm"
                        />
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          )}
        </div>

        {/* Notas */}
        <Input
          label="Notas (opcional)"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
      </form>
    </Modal>
  )
}