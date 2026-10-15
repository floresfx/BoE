import { useMemo, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Select } from '../../components/ui/Select'
import {
  useCategories,
  useUnits,
} from '../../hooks/useCatalogs'
import {
  useCreateResource,
  useDeleteResource,
  useResources,
  useUpdateResource,
} from '../../hooks/useResources'
import type { Resource, ResourceType } from '../../types/resource'
import { RESOURCE_TYPES } from '../../types/resource'
import { ConfirmDialog } from './ConfirmDialog'
import { ResourceForm, type ResourceFormValues } from './ResourceForm'
import { ResourceAttributesModal } from './ResourceAttributesModal'
import { ResourceTaxesModal } from './ResourceTaxesModal'

const typeLabel = (t: ResourceType) =>
  RESOURCE_TYPES.find((x) => x.value === t)?.label ?? t

export function ResourcesList() {
  const qc = useQueryClient()
  const [search, setSearch] = useState('')
  const [filterType, setFilterType] = useState<ResourceType | ''>('')
  const [filterCategory, setFilterCategory] = useState<string>('')
  const [filterActive, setFilterActive] = useState<'' | 'true' | 'false'>('true')

  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<Resource | null>(null)
  const [deleting, setDeleting] = useState<Resource | null>(null)
  const [managingAttrs, setManagingAttrs] = useState<Resource | null>(null)
  const [managingTaxes, setManagingTaxes] = useState<Resource | null>(null)

  // Datos maestros para mostrar nombres
  const { data: units = [] } = useUnits()
  const { data: categories = [] } = useCategories()

  const unitsMap = useMemo(
    () => Object.fromEntries(units.map((u) => [u.id, u])),
    [units],
  )
  const categoriesMap = useMemo(
    () => Object.fromEntries(categories.map((c) => [c.id, c])),
    [categories],
  )

  const params = useMemo(
    () => ({
      search: search || undefined,
      resource_type: filterType || undefined,
      category_id: filterCategory || undefined,
      is_active:
        filterActive === '' ? undefined : filterActive === 'true',
      limit: 100,
    }),
    [search, filterType, filterCategory, filterActive],
  )

  const { data, isLoading, error } = useResources(params)
  const createMutation = useCreateResource()
  const updateMutation = useUpdateResource()
  const deleteMutation = useDeleteResource()

  const items = data?.items ?? []
  const total = data?.total ?? 0

  const handleNew = () => {
    setEditing(null)
    setFormOpen(true)
  }

  const handleEdit = (r: Resource) => {
    setEditing(r)
    setFormOpen(true)
  }

  const handleSubmit = async (values: ResourceFormValues) => {
    const payload = {
      ...values,
      category_id: values.category_id || null,
      subcategory_id: values.subcategory_id || null,
      cost: values.cost || null,
    }
    try {
      if (editing) {
        await updateMutation.mutateAsync({ id: editing.id, payload })
      } else {
        await createMutation.mutateAsync(payload)
      }
      setFormOpen(false)
      setEditing(null)
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      alert(
        'Error al guardar: ' +
          (apiErr.response?.data?.detail ?? (err as Error).message),
      )
    }
  }

  const handleConfirmDelete = async () => {
    if (!deleting) return
    try {
      await deleteMutation.mutateAsync(deleting.id)
      setDeleting(null)
    } catch (err) {
      alert('Error al desactivar: ' + (err as Error).message)
    }
  }

  const refreshResources = () => {
    qc.invalidateQueries({ queryKey: ['resources'] })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Recursos</h1>
          <p className="text-sm text-slate-500 mt-1">
            Materias primas, servicios, recursos humanos y físicos.
          </p>
        </div>
        <Button onClick={handleNew}>+ Nuevo recurso</Button>
      </div>

      <div className="bg-white rounded-lg shadow p-4 grid grid-cols-1 sm:grid-cols-4 gap-4">
        <Input
          placeholder="Buscar por nombre..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <Select
          value={filterType}
          onChange={(e) =>
            setFilterType(e.target.value as ResourceType | '')
          }
        >
          <option value="">Todos los tipos</option>
          {RESOURCE_TYPES.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </Select>
        <Select
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
        >
          <option value="">Todas las categorías</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </Select>
        <Select
          value={filterActive}
          onChange={(e) =>
            setFilterActive(e.target.value as '' | 'true' | 'false')
          }
        >
          <option value="true">Solo activos</option>
          <option value="false">Solo inactivos</option>
          <option value="">Todos</option>
        </Select>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-slate-500">Cargando...</div>
        ) : error ? (
          <div className="p-8 text-center text-red-600">
            Error al cargar recursos
          </div>
        ) : items.length === 0 ? (
          <div className="p-8 text-center text-slate-500">
            No hay recursos. Crea el primero con el botón de arriba.
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-slate-700">
                  Nombre
                </th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">
                  Tipo
                </th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">
                  Categoría
                </th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">
                  Unidad
                </th>
                <th className="text-right px-4 py-3 font-medium text-slate-700">
                  Costo
                </th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">
                  Estado
                </th>
                <th className="text-right px-4 py-3 font-medium text-slate-700">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((r) => {
                const cat = r.category_id
                  ? categoriesMap[r.category_id]
                  : null
                const unit = unitsMap[r.base_unit_id]
                return (
                  <tr key={r.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 font-medium text-slate-900">
                      {r.name}
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {typeLabel(r.resource_type)}
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {cat?.name ?? '—'}
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {unit ? `${unit.name} (${unit.symbol})` : '—'}
                    </td>
                    <td className="px-4 py-3 text-right text-slate-600">
                      {r.cost ?? '—'}
                    </td>
                    <td className="px-4 py-3">
                      {r.is_active ? (
                        <Badge variant="green">Activo</Badge>
                      ) : (
                        <Badge variant="gray">Inactivo</Badge>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right space-x-2 whitespace-nowrap">
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => setManagingAttrs(r)}
                        title="Gestionar atributos"
                      >
                        Atributos ({r.attributes.length})
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => setManagingTaxes(r)}
                        title="Gestionar impuestos"
                      >
                        Impuestos ({r.taxes.length})
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => handleEdit(r)}
                      >
                        Editar
                      </Button>
                      {r.is_active && (
                        <Button
                          size="sm"
                          variant="danger"
                          onClick={() => setDeleting(r)}
                        >
                          Desactivar
                        </Button>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>

      <p className="text-xs text-slate-500 text-right">
        Mostrando {items.length} de {total}
      </p>

      <ResourceForm
        open={formOpen}
        resource={editing}
        isLoading={createMutation.isPending || updateMutation.isPending}
        onSubmit={handleSubmit}
        onCancel={() => {
          setFormOpen(false)
          setEditing(null)
        }}
      />

      <ConfirmDialog
        open={Boolean(deleting)}
        title="Desactivar recurso"
        message={`¿Desactivar "${deleting?.name}"? No se borrará, solo se marcará como inactivo.`}
        confirmLabel="Desactivar"
        isLoading={deleteMutation.isPending}
        onConfirm={handleConfirmDelete}
        onCancel={() => setDeleting(null)}
      />

      <ResourceAttributesModal
        open={Boolean(managingAttrs)}
        resource={managingAttrs}
        onClose={() => setManagingAttrs(null)}
        onChanged={refreshResources}
      />

      <ResourceTaxesModal
        open={Boolean(managingTaxes)}
        resource={managingTaxes}
        onClose={() => setManagingTaxes(null)}
        onChanged={refreshResources}
      />
    </div>
  )
}