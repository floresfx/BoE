import { useEffect, useState } from 'react'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Modal } from '../../components/ui/Modal'
import { Select } from '../../components/ui/Select'
import { useCurrencies } from '../../hooks/useCatalogs'
import { useResources } from '../../hooks/useResources'
import {
  useAddSupplierResource,
  useRemoveSupplierResource,
  useUpdateSupplierResource,
} from '../../hooks/useSuppliers'
import type { Supplier, SupplierResource } from '../../types/supplier'

interface Props {
  open: boolean
  supplier: Supplier | null
  onClose: () => void
}

export function SupplierResourcesModal({ open, supplier, onClose }: Props) {
  const { data: resourcesData } = useResources({ is_active: true, limit: 500 })
  const { data: currencies = [] } = useCurrencies()
  const addMutation = useAddSupplierResource()
  const removeMutation = useRemoveSupplierResource()
  const updateMutation = useUpdateSupplierResource()

  const [selectedResource, setSelectedResource] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [editing, setEditing] = useState<SupplierResource | null>(null)
  const [form, setForm] = useState({
    unit_price: '',
    currency_id: '',
    lead_time_days: '',
    min_quantity: '',
    valid_until: '',
    notes: '',
  })

  useEffect(() => {
    if (open) {
      setSelectedResource('')
      setError(null)
      setEditing(null)
      setForm({
        unit_price: '',
        currency_id: '',
        lead_time_days: '',
        min_quantity: '',
        valid_until: '',
        notes: '',
      })
    }
  }, [open])

  if (!supplier) return null

  const currentResourceIds = new Set(supplier.resources.map((r) => r.resource_id))
  const availableResources = (resourcesData?.items ?? []).filter(
    (r) => !currentResourceIds.has(r.id),
  )

  const resetForm = () => {
    setForm({
      unit_price: '',
      currency_id: '',
      lead_time_days: '',
      min_quantity: '',
      valid_until: '',
      notes: '',
    })
    setEditing(null)
  }

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

  const startEdit = (r: SupplierResource) => {
    setEditing(r)
    setForm({
      unit_price: r.unit_price ?? '',
      currency_id: r.currency_id ?? '',
      lead_time_days: r.lead_time_days?.toString() ?? '',
      min_quantity: r.min_quantity ?? '',
      valid_until: r.valid_until ? r.valid_until.slice(0, 10) : '',
      notes: r.notes ?? '',
    })
  }

  const handleSaveEdit = async () => {
    if (!editing) return
    setBusy(true)
    setError(null)
    try {
      await updateMutation.mutateAsync({
        supplierId: supplier.id,
        resourceId: editing.resource_id,
        payload: {
          unit_price: form.unit_price || null,
          currency_id: form.currency_id || null,
          lead_time_days: form.lead_time_days ? Number(form.lead_time_days) : null,
          min_quantity: form.min_quantity || null,
          valid_until: form.valid_until ? `${form.valid_until}T00:00:00Z` : null,
          notes: form.notes || null,
        },
      })
      resetForm()
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      setError(apiErr.response?.data?.detail ?? 'Error al guardar oferta')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`Ofertas de "${supplier.name}"`}
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

        {/* Lista de ofertas */}
        <div>
          <h3 className="text-sm font-semibold text-slate-700 mb-2">
            Recursos ofertados ({supplier.resources.length})
          </h3>
          {supplier.resources.length === 0 ? (
            <p className="text-sm text-slate-500 italic">
              Este proveedor no suministra ningún recurso todavía.
            </p>
          ) : (
            <ul className="divide-y divide-slate-100 border border-slate-200 rounded">
              {supplier.resources.map((r) => (
                <li key={r.resource_id} className="px-3 py-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-slate-900">
                        {r.resource_name}
                      </div>
                      <div className="text-xs text-slate-500 mt-1 space-x-3">
                        {r.unit_price && (
                          <span>
                            💰 {r.unit_price} {r.currency_code ?? ''}
                          </span>
                        )}
                        {r.lead_time_days != null && (
                          <span>⏱ {r.lead_time_days} días</span>
                        )}
                        {r.min_quantity && <span>📦 min {r.min_quantity}</span>}
                        {r.valid_until && (
                          <span>
                            📅 hasta{' '}
                            {new Date(r.valid_until).toLocaleDateString('es-ES')}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="space-x-2">
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => startEdit(r)}
                        disabled={busy}
                      >
                        Editar oferta
                      </Button>
                      <Button
                        size="sm"
                        variant="danger"
                        onClick={() => handleRemove(r.resource_id)}
                        disabled={busy}
                      >
                        Quitar
                      </Button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Editar oferta */}
        {editing && (
          <div className="border border-blue-200 rounded p-4 bg-blue-50">
            <h3 className="text-sm font-semibold text-blue-900 mb-3">
              Editar oferta de: {editing.resource_name}
            </h3>
            <div className="grid grid-cols-2 gap-3">
              <Input
                label="Precio unitario"
                type="number"
                step="0.01"
                value={form.unit_price}
                onChange={(e) => setForm({ ...form, unit_price: e.target.value })}
              />
              <Select
                label="Moneda"
                value={form.currency_id}
                onChange={(e) => setForm({ ...form, currency_id: e.target.value })}
              >
                <option value="">— Sin moneda —</option>
                {currencies.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.code} - {c.name}
                  </option>
                ))}
              </Select>
              <Input
                label="Lead time (días)"
                type="number"
                value={form.lead_time_days}
                onChange={(e) =>
                  setForm({ ...form, lead_time_days: e.target.value })
                }
              />
              <Input
                label="Cantidad mínima"
                type="number"
                step="0.01"
                value={form.min_quantity}
                onChange={(e) =>
                  setForm({ ...form, min_quantity: e.target.value })
                }
              />
              <Input
                label="Válida hasta"
                type="date"
                value={form.valid_until}
                onChange={(e) =>
                  setForm({ ...form, valid_until: e.target.value })
                }
              />
              <Input
                label="Notas"
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
              />
            </div>
            <div className="flex justify-end gap-2 mt-3">
              <Button variant="secondary" size="sm" onClick={resetForm}>
                Cancelar
              </Button>
              <Button size="sm" onClick={handleSaveEdit} disabled={busy}>
                {busy ? 'Guardando...' : 'Guardar oferta'}
              </Button>
            </div>
          </div>
        )}

        {/* Añadir recurso */}
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