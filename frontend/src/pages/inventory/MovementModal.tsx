import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Modal } from '../../components/ui/Modal'
import { Select } from '../../components/ui/Select'
import { useCreateMovement, useWarehouses } from '../../hooks/useInventory'
import { useResources } from '../../hooks/useResources'

const schema = z.object({
  warehouse_id: z.string().uuid('Selecciona un almacén'),
  resource_id: z.string().uuid('Selecciona un recurso'),
  lot_code: z.string().min(1, 'Requerido').max(50),
  movement_type: z.enum(['in', 'out', 'adjust', 'loss']),
  quantity: z.string().min(1, 'Requerido').refine((v) => !isNaN(Number(v)) && Number(v) > 0, 'Debe ser > 0'),
  unit_cost: z.string().optional().or(z.literal('')),
  expiration: z.string().optional().or(z.literal('')),
  reference: z.string().optional().or(z.literal('')),
  notes: z.string().optional().or(z.literal('')),
})

type FormValues = z.infer<typeof schema>

interface Props {
  open: boolean
  onClose: () => void
}

export function MovementModal({ open, onClose }: Props) {
  const create = useCreateMovement()
  const { data: warehouses } = useWarehouses({ is_active: true })
  const { data: resources } = useResources({ is_active: true, limit: 500 })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      warehouse_id: '',
      resource_id: '',
      lot_code: '',
      movement_type: 'in',
      quantity: '',
      unit_cost: '',
      expiration: '',
      reference: '',
      notes: '',
    },
  })

  useEffect(() => {
    if (!open)
      reset({
        warehouse_id: '',
        resource_id: '',
        lot_code: '',
        movement_type: 'in',
        quantity: '',
        unit_cost: '',
        expiration: '',
        reference: '',
        notes: '',
      })
  }, [open, reset])

  const onSubmit = async (values: FormValues) => {
    try {
      await create.mutateAsync({
        warehouse_id: values.warehouse_id,
        resource_id: values.resource_id,
        lot_code: values.lot_code,
        movement_type: values.movement_type,
        quantity: values.quantity,
        unit_cost: values.unit_cost || null,
        expiration: values.expiration || null,
        reference: values.reference || null,
        notes: values.notes || null,
      })
      onClose()
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      alert(apiErr.response?.data?.detail ?? 'Error al registrar movimiento')
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Registrar movimiento"
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={create.isPending}>
            Cancelar
          </Button>
          <Button type="submit" form="movement-form" disabled={create.isPending}>
            {create.isPending ? 'Registrando...' : 'Registrar'}
          </Button>
        </>
      }
    >
      <form id="movement-form" onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Select label="Almacén" {...register('warehouse_id')} error={errors.warehouse_id?.message}>
          <option value="">— Selecciona —</option>
          {warehouses?.items.map((w) => (
            <option key={w.id} value={w.id}>
              {w.name} ({w.code})
            </option>
          ))}
        </Select>

        <Select label="Recurso" {...register('resource_id')} error={errors.resource_id?.message}>
          <option value="">— Selecciona —</option>
          {resources?.items.map((r) => (
            <option key={r.id} value={r.id}>
              {r.name}
            </option>
          ))}
        </Select>

        <Select label="Tipo de movimiento" {...register('movement_type')} error={errors.movement_type?.message}>
          <option value="in">Entrada (in)</option>
          <option value="out">Salida (out)</option>
          <option value="adjust">Ajuste (adjust)</option>
          <option value="loss">Merma (loss)</option>
        </Select>

        <Input label="Código de lote" placeholder="LOT-2026-001" {...register('lot_code')} error={errors.lot_code?.message} />
        <Input label="Cantidad" type="number" step="0.0001" placeholder="10" {...register('quantity')} error={errors.quantity?.message} />

        <div className="grid grid-cols-2 gap-4">
          <Input label="Costo unitario (opcional)" type="number" step="0.01" {...register('unit_cost')} error={errors.unit_cost?.message} />
          <Input label="Caducidad (opcional)" type="date" {...register('expiration')} error={errors.expiration?.message} />
        </div>

        <Input label="Referencia (opcional)" placeholder="Orden #123" {...register('reference')} error={errors.reference?.message} />
        <Input label="Notas (opcional)" {...register('notes')} error={errors.notes?.message} />
      </form>
    </Modal>
  )
}