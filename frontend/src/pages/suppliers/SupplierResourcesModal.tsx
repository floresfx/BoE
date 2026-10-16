import { useEffect, useState } from 'react'
import { Button } from '../../components/ui/Button'
import { Modal } from '../../components/ui/Modal'
import { Select } from '../../components/ui/Select'
import { useResources } from '../../hooks/useResources'
import {
  useAddSupplierResource,
  useRemoveSupplierResource,
} from '../../hooks/useSuppliers'
import type { Supplier } from '../../types/supplier'

interface Props {
  open: boolean
  supplier: Supplier | null
  onClose: () => void
}

export function SupplierResourcesModal({ open, supplier, onClose }: Props) {
  const { data: resourcesData } = useResources({ is_active: true, limit: 500 })
  const addMutation = useAddSupplierResource()
  const removeMutation = useRemoveSupplierResource()

  const [selectedResource, setSelectedResource] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (open) {
      setSelectedResource('')
      setError(null)
    }
  }, [open])

  if (!supplier) return null

  const currentResourceIds = new Set(supplier.resources.map((r) => r.resource_id))
  const availableResources = (resourcesData?.items ?? []).filter(
    (r) => !currentResourceIds.has(r.id),
  )

  const handleAdd = async () => {
    if (!selectedResource) return
    setBusy(true)
    setError(null)
    try {
      await addMutation.mutateAsync({
        supplierId: supplier.id,
        resourceId: selectedResource,
      })
      setSelectedResource('')
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      setError(apiErr.response?.data?.detail ?? 'Error al añadir recurso')
    } finally {
      setBusy(false)
    }
  }

  const handleRemove = async (resourceId: string) => {
    setBusy(true)
    setError(null)
    try {
      await removeMutation.mutateAsync({
        supplierId: supplier.id,
        resourceId,
      })
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      setError(apiErr.response?.data?.detail ?? 'Error al quitar recurso')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`Recursos de "${supplier.name}"`}
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
            Recursos suministrados ({supplier.resources.length})
          </h3>
          {supplier.resources.length === 0 ? (
            <p className="text-sm text-slate-500 italic">
              Este proveedor no suministra ningún recurso todavía.
            </p>
          ) : (
            <ul className="divide-y divide-slate-100 border border-slate-200 rounded">
              {supplier.resources.map((r) => (
                <li
                  key={r.resource_id}
                  className="flex items-center justify-between px-3 py-2"
                >
                  <span className="font-medium text-slate-900">
                    {r.resource_name}
                  </span>
                  <Button
                    size="sm"
                    variant="danger"
                    onClick={() => handleRemove(r.resource_id)}
                    disabled={busy}
                  >
                    Quitar
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div>
          <h3 className="text-sm font-semibold text-slate-700 mb-2">
            Añadir recurso
          </h3>
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
          <Button
            onClick={handleAdd}
            disabled={!selectedResource || busy}
            className="w-full mt-3"
          >
            {busy ? 'Añadiendo...' : '+ Añadir recurso'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}