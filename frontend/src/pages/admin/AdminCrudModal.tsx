import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Modal } from '../../components/ui/Modal'
import { Select } from '../../components/ui/Select'

// ---------------------------------------------------------------------------
// Tipos de campo soportados
// ---------------------------------------------------------------------------

export type FieldType = 'text' | 'number' | 'select' | 'checkbox' | 'textarea'

export interface FieldConfig {
  name: string
  label: string
  type: FieldType
  required?: boolean
  placeholder?: string
  options?: { value: string; label: string }[]
  helpText?: string
  editableInEdit?: boolean // si es false, se deshabilita en modo edición (ej: code)
  min?: number
  max?: number
  step?: number
}

export interface AdminCrudModalProps {
  open: boolean
  title: string
  fields: FieldConfig[]
  initialValues?: Record<string, unknown> | null
  isLoading: boolean
  onSubmit: (values: Record<string, unknown>) => void
  onCancel: () => void
}

// ---------------------------------------------------------------------------
// Componente
// ---------------------------------------------------------------------------

export function AdminCrudModal({
  open,
  title,
  fields,
  initialValues,
  isLoading,
  onSubmit,
  onCancel,
}: AdminCrudModalProps) {
  const isEditing = Boolean(initialValues)

  // Construir schema Zod dinámicamente
  const schemaShape: Record<string, z.ZodTypeAny> = {}
  for (const f of fields) {
    if (f.type === 'number') {
      schemaShape[f.name] = f.required
        ? z.coerce.number()
        : z.coerce.number().optional().or(z.literal(''))
    } else if (f.type === 'checkbox') {
      schemaShape[f.name] = z.boolean().optional()
    } else {
      schemaShape[f.name] = f.required
        ? z.string().min(1, 'Requerido')
        : z.string().optional().or(z.literal(''))
    }
  }
  const schema = z.object(schemaShape)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(schema),
    defaultValues: buildDefaults(fields, initialValues),
  })

  useEffect(() => {
    if (!open) return
    reset(buildDefaults(fields, initialValues))
  }, [open, initialValues, fields, reset])

  const onFormSubmit = (values: Record<string, unknown>) => {
    // Convertir valores vacíos a null
    const cleaned: Record<string, unknown> = {}
    for (const f of fields) {
      let v = values[f.name]
      if (v === '' || v === undefined) v = null
      cleaned[f.name] = v
    }
    onSubmit(cleaned)
  }

  return (
    <Modal
      open={open}
      onClose={onCancel}
      title={title}
      footer={
        <>
          <Button variant="secondary" onClick={onCancel} disabled={isLoading}>
            Cancelar
          </Button>
          <Button type="submit" form="admin-crud-form" disabled={isLoading}>
            {isLoading ? 'Guardando...' : isEditing ? 'Guardar' : 'Crear'}
          </Button>
        </>
      }
    >
      <form
        id="admin-crud-form"
        onSubmit={handleSubmit(onFormSubmit)}
        className="space-y-4"
      >
        {fields.map((field) => {
          const error = errors[field.name]?.message as string | undefined
          const disabled =
            isEditing && field.editableInEdit === false

          if (field.type === 'checkbox') {
            return (
              <label
                key={field.name}
                className="flex items-center gap-2 text-sm text-slate-700"
              >
                <input
                  type="checkbox"
                  {...register(field.name)}
                  className="rounded border-slate-300"
                  disabled={disabled}
                />
                {field.label}
              </label>
            )
          }

          if (field.type === 'select') {
            return (
              <Select
                key={field.name}
                label={field.label}
                {...register(field.name)}
                error={error}
                disabled={disabled}
              >
                <option value="">— Selecciona —</option>
                {field.options?.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </Select>
            )
          }

          if (field.type === 'textarea') {
            return (
              <div key={field.name}>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  {field.label}
                </label>
                <textarea
                  {...register(field.name)}
                  placeholder={field.placeholder}
                  disabled={disabled}
                  rows={3}
                  className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {error && (
                  <p className="text-xs text-red-600 mt-1">{error}</p>
                )}
              </div>
            )
          }

          return (
            <Input
              key={field.name}
              label={field.label}
              type={field.type === 'number' ? 'number' : 'text'}
              placeholder={field.placeholder}
              error={error}
              disabled={disabled}
              step={field.step}
              {...register(field.name)}
            />
          )
        })}
      </form>
    </Modal>
  )
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function buildDefaults(
  fields: FieldConfig[],
  initialValues: Record<string, unknown> | null | undefined,
): Record<string, unknown> {
  const defaults: Record<string, unknown> = {}
  for (const f of fields) {
    if (initialValues && initialValues[f.name] !== undefined) {
      defaults[f.name] = initialValues[f.name]
    } else if (f.type === 'checkbox') {
      defaults[f.name] = f.name === 'is_active' ? true : false
    } else {
      defaults[f.name] = ''
    }
  }
  return defaults
}