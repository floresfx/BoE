import { useState } from 'react'
import { Modal } from '../../components/ui/Modal'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Select } from '../../components/ui/Select'
import { useCreateStockReservation } from '../../hooks/useStockReservations'
import { useWarehouses } from '../../hooks/useInventory'
import { useResources } from '../../hooks/useResources'

interface Props {
  open: boolean
  onClose: () => void
}

export function ReservationModal({ open, onClose }: Props) {
  const createMutation = useCreateStockReservation()
  const { data: warehousesData } = useWarehouses()
  const { data: resourcesData } = useResources({ limit: 100 })

  const [warehouseId, setWarehouseId] = useState('')
  const [resourceId, setResourceId] = useState('')
  const [quantity, setQuantity] = useState('')
  const [reference, setReference] = useState('')
  const [neededBy, setNeededBy] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!warehouseId || !resourceId || !quantity) {
      alert('Por favor, completa los campos obligatorios.')
      return
    }

    try {
      await createMutation.mutateAsync({
        warehouse_id: warehouseId,
        resource_id: resourceId,
        quantity: quantity,
        reference: reference || null,
        needed_by: neededBy ? new Date(neededBy).toISOString() : null,
      })
      alert('Reserva creada correctamente.')
      // Limpiar formulario
      setWarehouseId('')
      setResourceId('')
      setQuantity('')
      setReference('')
      setNeededBy('')
      onClose()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error al crear la reserva.')
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Nueva Reserva de Stock"
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={createMutation.isPending}>
            Cancelar
          </Button>
          <Button type="submit" form="reservation-form" disabled={createMutation.isPending}>
            {createMutation.isPending ? 'Creando...' : 'Crear Reserva'}
          </Button>
        </>
      }
    >
      <form id="reservation-form" onSubmit={handleSubmit} className="space-y-4">
        <Select
          label="Almacén"
          value={warehouseId}
          onChange={(e) => setWarehouseId(e.target.value)}
        >
          <option value="">Selecciona un almacén...</option>
          {warehousesData?.items.map((w) => (
            <option key={w.id} value={w.id}>{w.name}</option>
          ))}
        </Select>

        <Select
          label="Recurso"
          value={resourceId}
          onChange={(e) => setResourceId(e.target.value)}
        >
          <option value="">Selecciona un recurso...</option>
          {resourcesData?.items.map((r) => (
            <option key={r.id} value={r.id}>{r.name}</option>
          ))}
        </Select>

        <Input
          label="Cantidad a reservar"
          type="number"
          step="0.01"
          placeholder="Ej: 10.5"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
        />

        <Input
          label="Referencia (opcional)"
          placeholder="Ej: Pedido Cliente #123"
          value={reference}
          onChange={(e) => setReference(e.target.value)}
        />

        <Input
          label="Fecha requerida (opcional)"
          type="date"
          value={neededBy}
          onChange={(e) => setNeededBy(e.target.value)}
        />
      </form>
    </Modal>
  )
}