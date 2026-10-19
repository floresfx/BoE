import { useEffect, useState } from 'react'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Modal } from '../../components/ui/Modal'
import { useCreateProductionOrder } from '../../hooks/useProduction'
import { useBundles } from '../../hooks/useBundles'

interface Props {
  open: boolean
  onClose: () => void
}

export function NewProductionOrderModal({ open, onClose }: Props) {
  const { data: bundles } = useBundles({ is_active: true })
  const createMutation = useCreateProductionOrder()

  const [bundleId, setBundleId] = useState('')
  const [quantity, setQuantity] = useState('1')
  const [notes, setNotes] = useState('')

  useEffect(() => {
    if (!open) {
      setBundleId('')
      setQuantity('1')
      setNotes('')
    }
  }, [open])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!bundleId) return
    try {
        await createMutation.mutateAsync({
        bundle_id: bundleId,
        quantity,
        notes: notes || null,
        })
        // Esperar un tick para que TanStack Query invalide y refetchee
        await new Promise((resolve) => setTimeout(resolve, 100))
        onClose()
    } catch (err) {
        const apiErr = err as {
        response?: { data?: { detail?: string } }
        }
        alert(
        apiErr.response?.data?.detail ?? 'Error al crear orden',
        )
    }
    }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Nueva orden de producción"
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
            form="production-order-form"
            disabled={createMutation.isPending}
          >
            {createMutation.isPending ? 'Creando...' : 'Crear'}
          </Button>
        </>
      }
    >
      <form
        id="production-order-form"
        onSubmit={handleSubmit}
        className="space-y-4"
      >
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Bundle
          </label>
          <select
            value={bundleId}
            onChange={(e) => setBundleId(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            required
          >
            <option value="">— Selecciona —</option>
            {bundles?.items.map((b) => (
              <option key={b.id} value={b.id}>
                {b.name}
              </option>
            ))}
          </select>
        </div>

        <Input
          label="Cantidad"
          type="number"
          min={0.01}
          step="any"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          required
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