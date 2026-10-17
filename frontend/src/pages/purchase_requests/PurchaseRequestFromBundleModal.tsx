import { useEffect, useState } from 'react'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Modal } from '../../components/ui/Modal'
import { Select } from '../../components/ui/Select'
import { useBundles } from '../../hooks/useBundles'
import { useCreateFromBundle } from '../../hooks/usePurchaseRequests'

interface Props {
  open: boolean
  onClose: () => void
}

export function PurchaseRequestFromBundleModal({ open, onClose }: Props) {
  const { data: bundlesData } = useBundles({ is_active: true })
  const create = useCreateFromBundle()

  const [bundleId, setBundleId] = useState('')
  const [multiplier, setMultiplier] = useState('1')
  const [neededBy, setNeededBy] = useState('')
  const [notes, setNotes] = useState('')

  useEffect(() => {
    if (open) {
      setBundleId('')
      setMultiplier('1')
      setNeededBy('')
      setNotes('')
    }
  }, [open])

  const handleSubmit = async () => {
    if (!bundleId) {
      alert('Selecciona un paquete')
      return
    }
    try {
      await create.mutateAsync({
        bundle_id: bundleId,
        multiplier,
        needed_by: neededBy ? `${neededBy}T00:00:00Z` : null,
        notes: notes || null,
      })
      onClose()
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      alert(apiErr.response?.data?.detail ?? 'Error al generar solicitud')
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Solicitud desde paquete"
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={create.isPending}>
            Cancelar
          </Button>
          <Button onClick={handleSubmit} disabled={create.isPending}>
            {create.isPending ? 'Creando...' : 'Crear solicitud'}
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        <Select
          label="Paquete"
          value={bundleId}
          onChange={(e) => setBundleId(e.target.value)}
        >
          <option value="">— Selecciona un paquete —</option>
          {bundlesData?.items.map((b) => (
            <option key={b.id} value={b.id}>
              {b.name} ({b.components.length} componentes)
            </option>
          ))}
        </Select>
        <Input
          label="Multiplicador"
          type="number"
          step="0.01"
          value={multiplier}
          onChange={(e) => setMultiplier(e.target.value)}
        />
        <Input
          label="Fecha requerida (opcional)"
          type="date"
          value={neededBy}
          onChange={(e) => setNeededBy(e.target.value)}
        />
        <Input
          label="Notas (opcional)"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
      </div>
    </Modal>
  )
}