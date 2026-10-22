import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import {
  useBundles,
  useDeleteBundle,
} from '../../hooks/useBundles'
import type { Bundle } from '../../types/bundle'
import { ConfirmDialog } from '../resources/ConfirmDialog'
import { BundleComponentsModal } from './BundleComponentsModal'
import { BundleExplodeModal } from './BundleExplodeModal'
import { BundleForm } from './BundleForm'
import { Can } from '../../components/auth/Can'

export function BundlesList() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [filterActive, setFilterActive] = useState<'' | 'true' | 'false'>('true')
  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<Bundle | null>(null)
  const [deleting, setDeleting] = useState<Bundle | null>(null)
  const [managing, setManaging] = useState<Bundle | null>(null)
  const [exploding, setExploding] = useState<Bundle | null>(null)

  const { data, isLoading, error } = useBundles({
    search: search || undefined,
    is_active: filterActive === '' ? undefined : filterActive === 'true',
  })
  const deleteMutation = useDeleteBundle()

  const items = data?.items ?? []
  const total = data?.total ?? 0

  const handleNew = () => {
    setEditing(null)
    setFormOpen(true)
  }

  const handleEdit = (b: Bundle) => {
    setEditing(b)
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
          <h1 className="text-2xl font-bold text-slate-900">Paquetes (Bundles)</h1>
          <p className="text-sm text-slate-500 mt-1">
            Paquetes que agrupan varios recursos con cantidades.
          </p>
        </div>
        <Can module="bundle" action="crear">
          <Button onClick={handleNew}>+ Nuevo paquete</Button>
        </Can>
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
            No hay paquetes. Crea el primero con el botón de arriba.
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Código</th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Nombre</th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Tipo</th>
                <th className="text-right px-4 py-3 font-medium text-slate-700">Precio Venta</th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Componentes</th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Estado</th>
                <th className="text-right px-4 py-3 font-medium text-slate-700">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((b) => (
                <tr key={b.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-mono text-xs text-slate-600">
                    {b.code}
                  </td>
                  <td className="px-4 py-3 font-medium text-slate-900">
                    {b.name}
                  </td>
                  <td className="px-4 py-3 text-slate-600 capitalize">
                    {b.bundle_type}
                  </td>
                  <td className="px-4 py-3 text-right text-slate-600">
                    {b.sale_price ? `$${Number(b.sale_price).toFixed(2)}` : '—'}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {b.components.length} componente(s)
                  </td>
                  <td className="px-4 py-3">
                    {b.is_active ? (
                      <Badge variant="green">Activo</Badge>
                    ) : (
                      <Badge variant="gray">Inactivo</Badge>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right space-x-2 whitespace-nowrap">
                      <Can module="bundle" action="editar">
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => setManaging(b)}
                        >
                          Componentes ({b.components.length})
                        </Button>
                      </Can>

                      <Can module="bundle" action="ver">
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => setExploding(b)}
                        >
                          Explotar
                        </Button>
                      </Can>

                      <Can module="bundle" action="ver">
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => navigate(`/bundles/${b.id}/cost`)}
                        >
                          Ver costos
                        </Button>
                      </Can>

                      <Can module="bundle" action="editar">
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => handleEdit(b)}
                        >
                          Editar
                        </Button>
                      </Can>

                      {b.is_active && (
                        <Can module="bundle" action="eliminar">
                          <Button
                            size="sm"
                            variant="danger"
                            onClick={() => setDeleting(b)}
                          >
                            Desactivar
                          </Button>
                        </Can>
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

      <BundleForm
        open={formOpen}
        bundle={editing}
        onClose={() => {
          setFormOpen(false)
          setEditing(null)
        }}
      />

      <ConfirmDialog
        open={Boolean(deleting)}
        title="Desactivar paquete"
        message={`¿Desactivar "${deleting?.name}"? No se borrará, solo se marcará como inactivo.`}
        confirmLabel="Desactivar"
        isLoading={deleteMutation.isPending}
        onConfirm={handleConfirmDelete}
        onCancel={() => setDeleting(null)}
      />

      <BundleComponentsModal
        open={Boolean(managing)}
        bundle={managing}
        onClose={() => setManaging(null)}
      />

      <BundleExplodeModal
        open={Boolean(exploding)}
        bundle={exploding}
        onClose={() => setExploding(null)}
      />
    </div>
  )
}