import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Modal } from '../../components/ui/Modal'
import { useCreateWarehouse } from '../../hooks/useInventory'

const schema = z.object({
  name: z.string().min(1, 'Requerido').max(100),
  code: z.string().min(1, 'Requerido').max(20),
  address: z.string().optional().or(z.literal('')),
})

type FormValues = z.infer<typeof schema>

interface Props {
  open: boolean
  onClose: () => void
}

export function WarehouseForm({ open, onClose }: Props) {
  const create = useCreateWarehouse()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { name: '', code: '', address: '' },
  })

  useEffect(() => {
    if (!open) reset({ name: '', code: '', address: '' })
  }, [open, reset])

  const onSubmit = async (values: FormValues) => {
    try {
      await create.mutateAsync({
        name: values.name,
        code: values.code,
        address: values.address || null,
      })
      onClose()
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      alert(apiErr.response?.data?.detail ?? 'Error al crear almacén')
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Nuevo almacén"
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={create.isPending}>
            Cancelar
          </Button>
          <Button type="submit" form="warehouse-form" disabled={create.isPending}>
            {create.isPending ? 'Creando...' : 'Crear'}
          </Button>
        </>
      }
    >
      <form id="warehouse-form" onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Input label="Nombre" placeholder="Bodega principal" {...register('name')} error={errors.name?.message} />
        <Input label="Código" placeholder="BOD-01" {...register('code')} error={errors.code?.message} />
        <Input label="Dirección (opcional)" {...register('address')} error={errors.address?.message} />
      </form>
    </Modal>
  )
}