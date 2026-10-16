import { useState } from 'react'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import {
  useDeleteSupplier,
  useSuppliers,
} from '../../hooks/useSuppliers'
import type { Supplier } from '../../types/supplier'
import { ConfirmDialog } from '../resources/ConfirmDialog'
import { SupplierForm } from './SupplierForm'
import { SupplierResourcesModal } from './SupplierResourcesModal'

export function SuppliersList() {
  const [search, setSearch] = useState('')
  const [filterActive, setFilterActive] = useState<'' | 'true' | 'false'>('true')
  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<Supplier | null>(null)
  const [deleting, setDeleting] = useState<Supplier | null>(null)
  const [managing, setManaging] = useState<Supplier | null>(null)

  const { data, isLoading, error } = useSuppliers({
    search: search || undefined,
    is_active: filterActive === '' ? undefined : filterActive === 'true',
  })
  const deleteMutation = useDeleteSupplier()

  const items = data?.items ?? []
  const total = data?.total ?? 0

  const handleNew = () => {
    setEditing(null)
    setFormOpen(true)
  }

  const handleEdit = (s: Supplier) => {
    setEditing(s)
    setFormOpen(true)
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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Proveedores</h1>
          <p className="text-sm text-slate-500 mt-1">
            Empresas o personas que suministran recursos.
          </p>
        </div>
        <Button onClick={handleNew}>+ Nuevo proveedor</Button>
      </div>

      <div className="bg-white rounded-lg shadow p-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Input
          placeholder="Buscar por nombre..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          value={filterActive}
          onChange={(e) =>
            setFilterActive(e.target.value as '' | 'true' | 'false')
          }
          className="rounded-md border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="true">Solo activos</option>
          <option value="false">Solo inactivos</option>
          <option value="">Todos</option>
        </select>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-slate-500">Cargando...</div>
        ) : error ? (
          <div className="p-8 text-center text-red-600">Error al cargar</div>
        ) : items.length === 0 ? (
          <div className="p-8 text-center text-slate-500">
            No hay proveedores. Crea el primero con el botón de arriba.
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Código</th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Nombre</th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Contacto</th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Recursos</th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Estado</th>
                <th className="text-right px-4 py-3 font-medium text-slate-700">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((s) => (
                <tr key={s.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-mono text-xs text-slate-600">
                    {s.code}
                  </td>
                  <td className="px-4 py-3 font-medium text-slate-900">
                    {s.name}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {s.contact_name ?? s.email ?? '—'}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {s.resources.length} recurso(s)
                  </td>
                  <td className="px-4 py-3">
                    {s.is_active ? (
                      <Badge variant="green">Activo</Badge>
                    ) : (
                      <Badge variant="gray">Inactivo</Badge>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right space-x-2 whitespace-nowrap">
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => setManaging(s)}
                    >
                      Recursos ({s.resources.length})
                    </Button>
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => handleEdit(s)}
                    >
                      Editar
                    </Button>
                    {s.is_active && (
                      <Button
                        size="sm"
                        variant="danger"
                        onClick={() => setDeleting(s)}
                      >
                        Desactivar
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <p className="text-xs text-slate-500 text-right">
        Mostrando {items.length} de {total}
      </p>

      <SupplierForm
        open={formOpen}
        supplier={editing}
        onClose={() => {
          setFormOpen(false)
          setEditing(null)
        }}
      />

      <ConfirmDialog
        open={Boolean(deleting)}
        title="Desactivar proveedor"
        message={`¿Desactivar "${deleting?.name}"? No se borrará, solo se marcará como inactivo.`}
        confirmLabel="Desactivar"
        isLoading={deleteMutation.isPending}
        onConfirm={handleConfirmDelete}
        onCancel={() => setDeleting(null)}
      />

      <SupplierResourcesModal
        open={Boolean(managing)}
        supplier={managing}
        onClose={() => setManaging(null)}
      />
    </div>
  )
}