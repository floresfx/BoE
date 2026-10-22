import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Modal } from '../../components/ui/Modal'
import { Select } from '../../components/ui/Select'
import {
  useCreateBundle,
  useUpdateBundle,
} from '../../hooks/useBundles'
import type { Bundle } from '../../types/bundle'

// El schema debe estar FUERA de la función
const schema = z.object({
  code: z.string().min(1, 'Requerido').max(50),
  name: z.string().min(1, 'Requerido').max(255),
  description: z.string().optional().or(z.literal('')),
  bundle_type: z.string().min(1, 'Requerido'),
  sale_price: z.string().optional().or(z.literal('')),
  is_active: z.boolean().optional(),
})

type FormValues = z.infer<typeof schema>

interface Props {
  open: boolean
  bundle: Bundle | null
  onClose: () => void
}

export function BundleForm({ open, bundle, onClose }: Props) {
  const isEditing = Boolean(bundle)
  const create = useCreateBundle()
  const update = useUpdateBundle()

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      code: '',
      name: '',
      description: '',
      bundle_type: 'production',
      sale_price: '',
      is_active: true,
    },
  })

  useEffect(() => {
    if (!open) return
    if (bundle) {
      reset({
        code: bundle.code,
        name: bundle.name,
        description: bundle.description ?? '',
        bundle_type: bundle.bundle_type ?? 'production',
        sale_price: bundle.sale_price ?? '',
        is_active: bundle.is_active,
      })
    } else {
      reset({
        code: '',
        name: '',
        description: '',
        bundle_type: 'production',
        sale_price: '',
        is_active: true,
      })
    }
  }, [open, bundle, reset])

  const onSubmit = async (values: FormValues) => {
    const clean = {
      ...values,
      description: values.description || null,
      sale_price: values.sale_price || null,
    }
    try {
      if (bundle) {
        const { code: _code, bundle_type: _bt, ...payload } = clean
        await update.mutateAsync({ id: bundle.id, payload })
      } else {
        await create.mutateAsync(clean)
      }
      onClose()
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      alert(apiErr.response?.data?.detail ?? 'Error al guardar')
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEditing ? 'Editar paquete' : 'Nuevo paquete'}
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={create.isPending || update.isPending}>
            Cancelar
          </Button>
          <Button
            type="submit"
            form="bundle-form"
            disabled={create.isPending || update.isPending}
          >
            {create.isPending || update.isPending ? 'Guardando...' : 'Guardar'}
          </Button>
        </>
      }
    >
      <form id="bundle-form" onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Input
          label="Código"
          placeholder="PAN-100"
          {...register('code')}
          error={errors.code?.message}
          disabled={isEditing}
        />
        <Input
          label="Nombre"
          placeholder="Pan artesanal - lote 100 unidades"
          {...register('name')}
          error={errors.name?.message}
        />
        <Input
          label="Descripción (opcional)"
          {...register('description')}
          error={errors.description?.message}
        />
        <div className="grid grid-cols-2 gap-4">
          <Select
            label="Tipo de paquete"
            {...register('bundle_type')}
            error={errors.bundle_type?.message}
          >
            <option value="production">Producción</option>
            <option value="service">Servicio</option>
            <option value="maintenance">Mantenimiento</option>
          </Select>
          <Input
            label="Precio de venta (opcional)"
            placeholder="100.00"
            {...register('sale_price')}
            error={errors.sale_price?.message}
          />
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-700">
          <input
            type="checkbox"
            {...register('is_active')}
            className="rounded border-slate-300"
          />
          Activo
        </label>
      </form>
    </Modal>
  )
}