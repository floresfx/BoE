import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Modal } from '../../components/ui/Modal'
import {
  useCreateSupplier,
  useUpdateSupplier,
} from '../../hooks/useSuppliers'
import type { Supplier } from '../../types/supplier'

const schema = z.object({
  code: z.string().min(1, 'Requerido').max(30),
  name: z.string().min(1, 'Requerido').max(255),
  tax_id: z.string().max(50).optional().or(z.literal('')),
  email: z.string().email('Email inválido').optional().or(z.literal('')),
  phone: z.string().max(50).optional().or(z.literal('')),
  address: z.string().optional().or(z.literal('')),
  contact_name: z.string().max(200).optional().or(z.literal('')),
  notes: z.string().optional().or(z.literal('')),
  is_active: z.boolean().optional(),
})

type FormValues = z.infer<typeof schema>

interface Props {
  open: boolean
  supplier: Supplier | null
  onClose: () => void
}

export function SupplierForm({ open, supplier, onClose }: Props) {
  const isEditing = Boolean(supplier)
  const create = useCreateSupplier()
  const update = useUpdateSupplier()

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
      tax_id: '',
      email: '',
      phone: '',
      address: '',
      contact_name: '',
      notes: '',
      is_active: true,
    },
  })

  useEffect(() => {
    if (!open) return
    if (supplier) {
      reset({
        code: supplier.code,
        name: supplier.name,
        tax_id: supplier.tax_id ?? '',
        email: supplier.email ?? '',
        phone: supplier.phone ?? '',
        address: supplier.address ?? '',
        contact_name: supplier.contact_name ?? '',
        notes: supplier.notes ?? '',
        is_active: supplier.is_active,
      })
    } else {
      reset({
        code: '',
        name: '',
        tax_id: '',
        email: '',
        phone: '',
        address: '',
        contact_name: '',
        notes: '',
        is_active: true,
      })
    }
  }, [open, supplier, reset])

  const onSubmit = async (values: FormValues) => {
    const clean = {
      ...values,
      tax_id: values.tax_id || null,
      email: values.email || null,
      phone: values.phone || null,
      address: values.address || null,
      contact_name: values.contact_name || null,
      notes: values.notes || null,
    }
    try {
      if (supplier) {
        const { code: _code, ...payload } = clean
        await update.mutateAsync({ id: supplier.id, payload })
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
      title={isEditing ? 'Editar proveedor' : 'Nuevo proveedor'}
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={create.isPending || update.isPending}>
            Cancelar
          </Button>
          <Button
            type="submit"
            form="supplier-form"
            disabled={create.isPending || update.isPending}
          >
            {create.isPending || update.isPending ? 'Guardando...' : 'Guardar'}
          </Button>
        </>
      }
    >
      <form id="supplier-form" onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Código"
            placeholder="PROV-001"
            {...register('code')}
            error={errors.code?.message}
            disabled={isEditing}
          />
          <Input
            label="Nombre"
            placeholder="Harinas del Centro"
            {...register('name')}
            error={errors.name?.message}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Input label="RIF / NIT (opcional)" {...register('tax_id')} error={errors.tax_id?.message} />
          <Input label="Contacto (opcional)" {...register('contact_name')} error={errors.contact_name?.message} />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Input label="Email (opcional)" type="email" {...register('email')} error={errors.email?.message} />
          <Input label="Teléfono (opcional)" {...register('phone')} error={errors.phone?.message} />
        </div>
        <Input label="Dirección (opcional)" {...register('address')} error={errors.address?.message} />
        <Input label="Notas (opcional)" {...register('notes')} error={errors.notes?.message} />

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