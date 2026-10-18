import { useEffect, useState } from 'react'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { Modal } from '../ui/Modal'
import { useCreateSupplierQuote } from '../../hooks/useSupplierQuotes'
import { useSuppliers } from '../../hooks/useSuppliers'
import type { PurchaseRequestLine } from '../../types/purchase_request'

interface Props {
  open: boolean
  requestId: string
  line: PurchaseRequestLine | null
  onClose: () => void
}

export function CreateQuoteModal({
  open,
  requestId,
  line,
  onClose,
}: Props) {
  const { data: suppliers } = useSuppliers({ is_active: true })
  const createMutation = useCreateSupplierQuote()

  const [supplierId, setSupplierId] = useState('')
  const [unitPrice, setUnitPrice] = useState('')
  const [leadTimeDays, setLeadTimeDays] = useState('0')
  const [validUntil, setValidUntil] = useState('')
  const [notes, setNotes] = useState('')

  useEffect(() => {
    if (!open) {
      setSupplierId('')
      setUnitPrice('')
      setLeadTimeDays('0')
      setValidUntil('')
      setNotes('')
    }
  }, [open])

  if (!line) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!supplierId || !unitPrice) return
    try {
      await createMutation.mutateAsync({
        requestId,
        payload: {
          line_id: line.id,
          supplier_id: supplierId,
          unit_price: unitPrice,
          lead_time_days: parseInt(leadTimeDays) || 0,
          valid_until: validUntil || null,
          notes: notes || null,
        },
      })
      onClose()
    } catch (err) {
      const apiErr = err as {
        response?: { data?: { detail?: string } }
      }
      alert(
        apiErr.response?.data?.detail ?? 'Error al crear cotización',
      )
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`Cotizar: ${line.resource_name}`}
      footer={
        <>
          <Button
            variant="secondary"
            onClick={onClose}
            disabled={createMutation.isPending}
          >
            Cancelar
          </Button>
          <Button
            type="submit"
            form="quote-form"
            disabled={createMutation.isPending}
          >
            {createMutation.isPending ? 'Creando...' : 'Crear cotización'}
          </Button>
        </>
      }
    >
      <form
        id="quote-form"
        onSubmit={handleSubmit}
        className="space-y-4"
      >
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Proveedor
          </label>
          <select
            value={supplierId}
            onChange={(e) => setSupplierId(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            required
          >
            <option value="">— Selecciona —</option>
            {suppliers?.items.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Precio unitario"
            type="number"
            min={0.01}
            step="any"
            value={unitPrice}
            onChange={(e) => setUnitPrice(e.target.value)}
            required
          />
          <Input
            label="Lead time (días)"
            type="number"
            min={0}
            step="1"
            value={leadTimeDays}
            onChange={(e) => setLeadTimeDays(e.target.value)}
          />
        </div>

        <Input
          label="Válido hasta (opcional)"
          type="date"
          value={validUntil}
          onChange={(e) => setValidUntil(e.target.value)}
        />

        <Input
          label="Notas (opcional)"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
      </form>
    </Modal>
  )
}