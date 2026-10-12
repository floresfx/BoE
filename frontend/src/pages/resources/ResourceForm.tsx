import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Modal } from '../../components/ui/Modal'
import { Select } from '../../components/ui/Select'
import type { Resource } from '../../types/resource'
import { RESOURCE_TYPES } from '../../types/resource'

const schema = z.object({
  name: z.string().min(1, 'Requerido').max(255),
  resource_type: z.enum([
    'materia_prima',
    'producto_terminado',
    'subproducto',
    'insumo',
    'servicio_propio',
    'servicio_externo',
    'recurso_humano',
    'recurso_fisico',
  ]),
  category: z.string().max(100).optional().or(z.literal('')),
  base_unit: z.string().min(1, 'Requerido').max(20),
  cost: z
    .string()
    .optional()
    .or(z.literal(''))
    .refine(
      (v) => !v || /^\d+(\.\d{1,2})?$/.test(v),
      'Formato inválido (ej: 2.50)',
    ),
  is_active: z.boolean().optional(),
})

export type ResourceFormValues = z.infer<typeof schema>

interface Props {
  open: boolean
  resource: Resource | null
  isLoading: boolean
  onSubmit: (values: ResourceFormValues) => void
  onCancel: () => void
}

export function ResourceForm({
  open,
  resource,
  isLoading,
  onSubmit,
  onCancel,
}: Props) {
  const isEditing = Boolean(resource)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ResourceFormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: '',
      resource_type: 'materia_prima',
      category: '',
      base_unit: 'kg',
      cost: '',
      is_active: true,
    },
  })

  useEffect(() => {
    if (!open) return
    if (resource) {
      reset({
        name: resource.name,
        resource_type: resource.resource_type,
        category: resource.category ?? '',
        base_unit: resource.base_unit,
        cost: resource.cost ?? '',
        is_active: resource.is_active,
      })
    } else {
      reset({
        name: '',
        resource_type: 'materia_prima',
        category: '',
        base_unit: 'kg',
        cost: '',
        is_active: true,
      })
    }
  }, [open, resource, reset])

  return (
    <Modal
      open={open}
      onClose={onCancel}
      title={isEditing ? 'Editar recurso' : 'Nuevo recurso'}
      footer={
        <>
          <Button
            type="button"
            variant="secondary"
            onClick={onCancel}
            disabled={isLoading}
          >
            Cancelar
          </Button>
          <Button type="submit" form="resource-form" disabled={isLoading}>
            {isLoading ? 'Guardando...' : 'Guardar'}
          </Button>
        </>
      }
    >
      <form
        id="resource-form"
        onSubmit={handleSubmit(onSubmit)}
        className="space-y-4"
      >
        <Input
          label="Nombre"
          placeholder="Harina de trigo"
          {...register('name')}
          error={errors.name?.message}
        />

        <Select
          label="Tipo"
          {...register('resource_type')}
          error={errors.resource_type?.message}
        >
          {RESOURCE_TYPES.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </Select>

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Categoría (opcional)"
            placeholder="harinas"
            {...register('category')}
            error={errors.category?.message}
          />

          <Input
            label="Unidad base"
            placeholder="kg, unidad, hora..."
            {...register('base_unit')}
            error={errors.base_unit?.message}
          />
        </div>

        <Input
          label="Costo por unidad (opcional)"
          placeholder="2.50"
          {...register('cost')}
          error={errors.cost?.message}
        />

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