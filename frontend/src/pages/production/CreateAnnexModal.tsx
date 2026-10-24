import { useEffect, useState } from 'react'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Modal } from '../../components/ui/Modal'
import { useCreateAnnex } from '../../hooks/useProductionAnnexes'

interface Props {
  open: boolean
  onClose: () => void
  order: { id: string; code: string } | null
}

export function CreateAnnexModal({ open, onClose, order }: Props) {
  const createAnnex = useCreateAnnex()
  
  const [annexType, setAnnexType] = useState('extra_resource')
  const [quantity, setQuantity] = useState('')
  const [notes, setNotes] = useState('')

  useEffect(() => {
    if (!open) {
      setAnnexType('extra_resource')
      setQuantity('')
      setNotes('')
    }
  }, [open])

  if (!order) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      await createAnnex.mutateAsync({
        orderId: order.id,
        payload: {
          annex_type: annexType,
          quantity: quantity ? Number(quantity) : undefined,
          notes: notes.trim() || undefined,
        },
      })
      await new Promise((resolve) => setTimeout(resolve, 100))
      onClose()
    } catch (err: any) {
      alert(err.response?.data?.detail ?? 'Error al guardar anexo')
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`Añadir Anexo — ${order.code}`}
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={createAnnex.isPending}>
            Cancelar
          </Button>
          <Button
            type="submit"
            form="annex-form"
            disabled={createAnnex.isPending}
          >
            {createAnnex.isPending ? 'Guardando...' : 'Guardar Anexo'}
          </Button>
        </>
      }
    >
      <form id="annex-form" onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Tipo de Anexo
          </label>
          <select
            value={annexType}
            onChange={(e) => setAnnexType(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            required
          >
            <option value="quantity_adjustment">Ajuste de cantidad</option>
            <option value="extra_resource">Insumo adicional</option>
            <option value="removed_resource">Insumo eliminado</option>
            <option value="supplier_change">Cambio de proveedor</option>
            <option value="waste_change">Cambio de merma</option>
          </select>
        </div>

        <Input
          label="Cantidad (opcional)"
          type="number"
          step="any"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          placeholder="Ej: 5"
        />

        <Input
          label="Notas / Detalles"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Ej: Agregar 5 unidades por pedido urgente"
          required
        />
      </form>
    </Modal>
  )
}