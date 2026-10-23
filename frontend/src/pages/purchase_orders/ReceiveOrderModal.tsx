import { useState } from 'react'
import { Modal } from '../../components/ui/Modal'
import { Button } from '../../components/ui/Button'
import { Select } from '../../components/ui/Select'
import { useReceiveOrder } from '../../hooks/usePurchaseOrders'
import { useWarehouses } from '../../hooks/useInventory'

interface Props {
  open: boolean
  orderId: string
  onClose: () => void
}

export function ReceiveOrderModal({ open, orderId, onClose }: Props) {
  const { data: warehousesData } = useWarehouses()
  const receiveMutation = useReceiveOrder()
  const [warehouseId, setWarehouseId] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!warehouseId) return
    try {
      await receiveMutation.mutateAsync({ orderId, warehouseId })
      alert('Mercancía recibida correctamente.')
      setWarehouseId('')
      onClose()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error al recibir la mercancía.')
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Recibir Mercancía"
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={receiveMutation.isPending}>
            Cancelar
          </Button>
          <Button type="submit" form="receive-order-form" disabled={receiveMutation.isPending || !warehouseId}>
            {receiveMutation.isPending ? 'Recibiendo...' : 'Recibir'}
          </Button>
        </>
      }
    >
      <form id="receive-order-form" onSubmit={handleSubmit} className="space-y-4">
        <Select
          label="Almacén de destino"
          value={warehouseId}
          onChange={(e) => setWarehouseId(e.target.value)}
        >
          <option value="">Selecciona un almacén...</option>
          {warehousesData?.items.map((w) => (
            <option key={w.id} value={w.id}>{w.name}</option>
          ))}
        </Select>
        <p className="text-sm text-slate-500">
          Se crearán movimientos de entrada en el inventario para todas las líneas de la orden.
        </p>
      </form>
    </Modal>
  )
}