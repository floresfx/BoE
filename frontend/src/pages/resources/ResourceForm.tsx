import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Modal } from '../../components/ui/Modal'
import { useFilteredCatalogs } from '../../hooks/useTenantCatalogs'
import { Select } from '../../components/ui/Select'
import { useSubcategories } from '../../hooks/useCatalogs'
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
  category_id: z.string().uuid().optional().or(z.literal('')),
  subcategory_id: z.string().uuid().optional().or(z.literal('')),
  base_unit_id: z.string().uuid('Selecciona una unidad'),
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

  // --- NUEVO: Usamos el hook que filtra por tenant ---
  const { 
    units = [], 
    categories = [], 
    isLoading: loadingCatalogs 
  } = useFilteredCatalogs()

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<ResourceFormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: '',
      resource_type: 'materia_prima',
      category_id: '',
      subcategory_id: '',
      base_unit_id: '',
      cost: '',
      is_active: true,
    },
  })

  // Observar category_id para cargar subcategorías
  const selectedCategoryId = watch('category_id')
  const { data: subcategories = [], isLoading: loadingSubcategories } =
    useSubcategories(selectedCategoryId || undefined)

  // Resetear formulario al abrir
  useEffect(() => {
    if (!open) return
    if (resource) {
      reset({
        name: resource.name,
        resource_type: resource.resource_type,
        category_id: resource.category_id ?? '',
        subcategory_id: resource.subcategory_id ?? '',
        base_unit_id: resource.base_unit_id,
        cost: resource.cost ?? '',
        is_active: resource.is_active,
      })
    } else {
      reset({
        name: '',
        resource_type: 'materia_prima',
        category_id: '',
        subcategory_id: '',
        base_unit_id: '',
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
          <Button type="submit" form="resource-form" disabled={isLoading || loadingCatalogs}>
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
          <Select
            label="Categoría (opcional)"
            {...register('category_id')}
            error={errors.category_id?.message}
            disabled={loadingCatalogs}
          >
            <option value="">— Sin categoría —</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </Select>

          <Select
            label="Subcategoría (opcional)"
            {...register('subcategory_id')}
            error={errors.subcategory_id?.message}
            disabled={!selectedCategoryId || loadingSubcategories}
          >
            <option value="">— Sin subcategoría —</option>
            {subcategories.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </Select>
        </div>

        <Select
          label="Unidad base"
          {...register('base_unit_id')}
          error={errors.base_unit_id?.message}
          disabled={loadingCatalogs}
        >
          <option value="">— Selecciona una unidad —</option>
          {units.map((u) => (
            <option key={u.id} value={u.id}>
              {u.name} ({u.symbol})
            </option>
          ))}
        </Select>

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