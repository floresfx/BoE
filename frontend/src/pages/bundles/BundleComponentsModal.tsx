import { useEffect, useState } from 'react'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Modal } from '../../components/ui/Modal'
import { Select } from '../../components/ui/Select'
import { useResources } from '../../hooks/useResources'
import { useBundles } from '../../hooks/useBundles'
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
  const { data: bundlesData } = useBundles({ is_active: true, limit: 500 })
  const addMutation = useAddBundleComponent()
  const removeMutation = useRemoveBundleComponent()
  const updateMutation = useUpdateBundleComponent()
  const queryClient = useQueryClient()

  const [componentType, setComponentType] = useState<'resource' | 'bundle'>('resource')
  const [selectedResource, setSelectedResource] = useState('')
  const [selectedBundle, setSelectedBundle] = useState('')
  const [quantity, setQuantity] = useState('')
  const [wastePercent, setWastePercent] = useState('0')
  const [season, setSeason] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [editing, setEditing] = useState<BundleComponent | null>(null)
  const [editQuantity, setEditQuantity] = useState('')
  const [editWaste, setEditWaste] = useState('')
  const [editSeason, setEditSeason] = useState('')

  useEffect(() => {
    if (open) {
      queryClient.invalidateQueries({ queryKey: ['resources'] })
      queryClient.invalidateQueries({ queryKey: ['bundles'] })
      setComponentType('resource')
      setSelectedResource('')
      setSelectedBundle('')
      setQuantity('')
      setWastePercent('0')
      setSeason('')
      setEditing(null)
      setError(null)
    }
  }, [open, queryClient])

  if (!bundle) return null

  // Recursos ya añadidos como componente tipo resource
  const currentResourceIds = new Set(
    bundle.components
      .filter((c) => c.component_type === 'resource')
      .map((c) => c.resource_id),
  )
  // Bundles ya añadidos como sub-bundle
  const currentSubBundleIds = new Set(
    bundle.components
      .filter((c) => c.component_type === 'bundle')
      .map((c) => c.component_bundle_id),
  )

  const availableResources = (resourcesData?.items ?? []).filter(
    (r) => !currentResourceIds.has(r.id),
  )
  const availableBundles = (bundlesData?.items ?? []).filter(
    (b) => b.id !== bundle.id && !currentSubBundleIds.has(b.id),
  )

  const handleAdd = async () => {
    if (componentType === 'resource' && !selectedResource) return
    if (componentType === 'bundle' && !selectedBundle) return
    if (!quantity) return

    setBusy(true)
    setError(null)
    try {
      await addMutation.mutateAsync({
        bundleId: bundle.id,
        componentType,
        resourceId: componentType === 'resource' ? selectedResource : undefined,
        componentBundleId: componentType === 'bundle' ? selectedBundle : undefined,
        quantity,
        wastePercent,
        season: season || null,
      })
      setSelectedResource('')
      setSelectedBundle('')
      setQuantity('')
      setWastePercent('0')
      setSeason('')
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      setError(apiErr.response?.data?.detail ?? 'Error al añadir componente')
    } finally {
      setBusy(false)
    }
  }

  const handleRemove = async (c: BundleComponent) => {
    setBusy(true)
    setError(null)
    try {
      await removeMutation.mutateAsync({
        bundleId: bundle.id,
        componentType: c.component_type,
        resourceId: c.component_type === 'resource' ? c.resource_id : undefined,
        componentBundleId:
          c.component_type === 'bundle' ? c.component_bundle_id ?? undefined : undefined,
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
    setEditWaste(c.waste_percent)
    setEditSeason(c.season ?? '')
  }

  const handleSaveEdit = async () => {
    if (!editing) return
    setBusy(true)
    setError(null)
    try {
      await updateMutation.mutateAsync({
        bundleId: bundle.id,
        componentType: editing.component_type,
        resourceId:
          editing.component_type === 'resource' ? editing.resource_id : undefined,
        componentBundleId:
          editing.component_type === 'bundle'
            ? editing.component_bundle_id ?? undefined
            : undefined,
        quantity: editQuantity,
        wastePercent: editWaste,
        season: editSeason || null,
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
                <li
                  key={`${c.component_type}-${c.resource_id || c.component_bundle_id}`}
                  className="px-3 py-2"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-xs uppercase font-semibold text-slate-400 mr-2">
                        {c.component_type === 'bundle' ? '[Sub-bundle]' : '[Recurso]'}
                      </span>
                      <span className="font-medium text-slate-900">
                        {c.component_type === 'bundle'
                          ? c.component_bundle_name
                          : c.resource_name}
                      </span>
                      {editing &&
                      editing.component_type === c.component_type &&
                      (editing.resource_id === c.resource_id ||
                        editing.component_bundle_id === c.component_bundle_id) ? (
                        <div className="mt-2 flex flex-col gap-2">
                          <div className="flex gap-2 items-center">
                            <span className="text-xs text-slate-500 w-16">Cant.:</span>
                            <input
                              type="number"
                              step="0.0001"
                              value={editQuantity}
                              onChange={(e) => setEditQuantity(e.target.value)}
                              className="w-24 rounded border border-slate-300 px-2 py-1 text-sm"
                            />
                            <span className="text-xs text-slate-500 w-16">Merma %:</span>
                            <input
                              type="number"
                              step="0.01"
                              value={editWaste}
                              onChange={(e) => setEditWaste(e.target.value)}
                              className="w-20 rounded border border-slate-300 px-2 py-1 text-sm"
                            />
                            <span className="text-xs text-slate-500 w-16">Temp.:</span>
                            <input
                              type="text"
                              value={editSeason}
                              onChange={(e) => setEditSeason(e.target.value)}
                              className="w-24 rounded border border-slate-300 px-2 py-1 text-sm"
                            />
                          </div>
                        </div>
                      ) : (
                        <span className="ml-3 text-slate-600">
                          {c.quantity}{' '}
                          {c.component_type === 'resource'
                            ? c.resource_unit_symbol ?? ''
                            : 'unidades'}
                          {c.waste_percent && Number(c.waste_percent) > 0 && (
                            <span className="text-xs text-orange-600 ml-2">
                              (merma: {c.waste_percent}%)
                            </span>
                          )}
                          {c.season && (
                            <span className="text-xs text-blue-600 ml-2">
                              ({c.season})
                            </span>
                          )}
                        </span>
                      )}
                    </div>
                    <div className="space-x-2">
                      {editing &&
                      editing.component_type === c.component_type &&
                      (editing.resource_id === c.resource_id ||
                        editing.component_bundle_id === c.component_bundle_id) ? (
                        <>
                          <Button size="sm" onClick={handleSaveEdit} disabled={busy}>
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
                            onClick={() => handleRemove(c)}
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

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
            <Select
              label="Tipo"
              value={componentType}
              onChange={(e) => setComponentType(e.target.value as 'resource' | 'bundle')}
              disabled={busy}
            >
              <option value="resource">Recurso</option>
              <option value="bundle">Sub-bundle</option>
            </Select>

            {componentType === 'resource' ? (
              <Select
                label="Recurso"
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
            ) : (
              <Select
                label="Sub-bundle"
                value={selectedBundle}
                onChange={(e) => setSelectedBundle(e.target.value)}
                disabled={busy}
              >
                <option value="">— Selecciona un bundle —</option>
                {availableBundles.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.name}
                  </option>
                ))}
              </Select>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-3">
            <Input
              label="Cantidad"
              type="number"
              step="0.0001"
              placeholder="Ej: 10.5"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              disabled={busy}
            />
            <Input
              label="Merma % (opc.)"
              type="number"
              step="0.01"
              placeholder="0"
              value={wastePercent}
              onChange={(e) => setWastePercent(e.target.value)}
              disabled={busy}
            />
            <Input
              label="Temporada (opc.)"
              type="text"
              placeholder="Ej: invierno"
              value={season}
              onChange={(e) => setSeason(e.target.value)}
              disabled={busy}
            />
          </div>

          <Button
            onClick={handleAdd}
            disabled={
              (componentType === 'resource' ? !selectedResource : !selectedBundle) ||
              !quantity ||
              busy
            }
            className="w-full"
          >
            {busy ? 'Añadiendo...' : '+ Añadir componente'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}