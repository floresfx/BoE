import { useEffect, useState } from 'react'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Modal } from '../../components/ui/Modal'
import { Select } from '../../components/ui/Select'
import { useResources } from '../../hooks/useResources'
import { useQueryClient } from '@tanstack/react-query'
import {
  useAddBundleComponent,
  useRemoveBundleComponent,
  useUpdateBundleComponent,
} from '../../hooks/useBundles'
import type { Bundle, BundleComponent } from '../../types/bundle'

interface Props {
  open: boolean
  bundle: Bundle | null
  onClose: () => void
}

export function BundleComponentsModal({ open, bundle, onClose }: Props) {
  const { data: resourcesData } = useResources({ is_active: true, limit: 500 })
  const addMutation = useAddBundleComponent()
  const removeMutation = useRemoveBundleComponent()
  const updateMutation = useUpdateBundleComponent()
  const queryClient = useQueryClient()

  const [selectedResource, setSelectedResource] = useState('')
  const [quantity, setQuantity] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [editing, setEditing] = useState<BundleComponent | null>(null)
  const [editQuantity, setEditQuantity] = useState('')

  useEffect(() => {
    if (open) {
        // Invalidar caché de recursos para asegurar que veamos los del tenant actual
        queryClient.invalidateQueries({ queryKey: ['resources'] })
        setSelectedResource('')
        setQuantity('')
        setEditing(null)
        setError(null)
    }
  }, [open, queryClient])

  if (!bundle) return null

  const currentResourceIds = new Set(bundle.components.map((c) => c.resource_id))
  const availableResources = (resourcesData?.items ?? []).filter(
    (r) => !currentResourceIds.has(r.id),
  )

  const handleAdd = async () => {
    if (!selectedResource || !quantity) return
    setBusy(true)
    setError(null)
    try {
      await addMutation.mutateAsync({
        bundleId: bundle.id,
        resourceId: selectedResource,
        quantity,
      })
      setSelectedResource('')
      setQuantity('')
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      setError(apiErr.response?.data?.detail ?? 'Error al añadir componente')
    } finally {
      setBusy(false)
    }
  }

  const handleRemove = async (resourceId: string) => {
    setBusy(true)
    setError(null)
    try {
      await removeMutation.mutateAsync({
        bundleId: bundle.id,
        resourceId,
      })
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      setError(apiErr.response?.data?.detail ?? 'Error al quitar componente')
    } finally {
      setBusy(false)
    }
  }

  const startEdit = (c: BundleComponent) => {
    setEditing(c)
    setEditQuantity(c.quantity)
  }

  const handleSaveEdit = async () => {
    if (!editing) return
    setBusy(true)
    setError(null)
    try {
      await updateMutation.mutateAsync({
        bundleId: bundle.id,
        resourceId: editing.resource_id,
        quantity: editQuantity,
      })
      setEditing(null)
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      setError(apiErr.response?.data?.detail ?? 'Error al actualizar')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`Componentes de "${bundle.name}"`}
      footer={
        <Button variant="secondary" onClick={onClose}>
          Cerrar
        </Button>
      }
    >
      <div className="space-y-6">
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
            {error}
          </div>
        )}

        <div>
          <h3 className="text-sm font-semibold text-slate-700 mb-2">
            Componentes ({bundle.components.length})
          </h3>
          {bundle.components.length === 0 ? (
            <p className="text-sm text-slate-500 italic">
              Este paquete no tiene componentes todavía.
            </p>
          ) : (
            <ul className="divide-y divide-slate-100 border border-slate-200 rounded">
              {bundle.components.map((c) => (
                <li key={c.resource_id} className="px-3 py-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="font-medium text-slate-900">
                        {c.resource_name}
                      </span>
                      {editing?.resource_id === c.resource_id ? (
                        <input
                          type="number"
                          step="0.0001"
                          value={editQuantity}
                          onChange={(e) => setEditQuantity(e.target.value)}
                          className="ml-3 w-24 rounded border border-slate-300 px-2 py-1 text-sm"
                        />
                      ) : (
                        <span className="ml-3 text-slate-600">
                          {c.quantity} {c.resource_unit_symbol ?? ''}
                        </span>
                      )}
                    </div>
                    <div className="space-x-2">
                      {editing?.resource_id === c.resource_id ? (
                        <>
                          <Button
                            size="sm"
                            onClick={handleSaveEdit}
                            disabled={busy}
                          >
                            Guardar
                          </Button>
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => setEditing(null)}
                            disabled={busy}
                          >
                            Cancelar
                          </Button>
                        </>
                      ) : (
                        <>
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => startEdit(c)}
                            disabled={busy}
                          >
                            Editar
                          </Button>
                          <Button
                            size="sm"
                            variant="danger"
                            onClick={() => handleRemove(c.resource_id)}
                            disabled={busy}
                          >
                            Quitar
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div>
          <h3 className="text-sm font-semibold text-slate-700 mb-2">
            Añadir componente
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Select
              value={selectedResource}
              onChange={(e) => setSelectedResource(e.target.value)}
              disabled={busy}
            >
              <option value="">— Selecciona un recurso —</option>
              {availableResources.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name}
                </option>
              ))}
            </Select>
            <Input
              type="number"
              step="0.0001"
              placeholder="Cantidad"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              disabled={busy}
            />
          </div>
          <Button
            onClick={handleAdd}
            disabled={!selectedResource || !quantity || busy}
            className="w-full mt-3"
          >
            {busy ? 'Añadiendo...' : '+ Añadir componente'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}