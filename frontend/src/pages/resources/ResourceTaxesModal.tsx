import { useEffect, useState } from 'react'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Modal } from '../../components/ui/Modal'
import { Select } from '../../components/ui/Select'
import { api } from '../../lib/api'
import { useTaxes } from '../../hooks/useCatalogs'
import type { Resource, ResourceTax } from '../../types/resource'

interface Props {
  open: boolean
  resource: Resource | null
  onClose: () => void
  onChanged: () => void
}

export function ResourceTaxesModal({
  open,
  resource,
  onClose,
  onChanged,
}: Props) {
  const { data: allTaxes = [], isLoading: loadingTaxes } = useTaxes()
  const [items, setItems] = useState<ResourceTax[]>([])
  const [selectedId, setSelectedId] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (open && resource) {
      setItems(resource.taxes ?? [])
      setSelectedId('')
      setError(null)
    }
  }, [open, resource])

  const available = allTaxes.filter(
    (t) => !items.some((i) => i.tax_id === t.id),
  )

  const handleAdd = async () => {
    if (!resource || !selectedId) return
    setBusy(true)
    setError(null)
    try {
      const { data } = await api.post<{ tax_id: string }>(
        `/resources/${resource.id}/taxes`,
        { tax_id: selectedId },
      )
      const tax = allTaxes.find((t) => t.id === data.tax_id)
      if (tax) {
        setItems((prev) => [
          ...prev,
          {
            tax_id: tax.id,
            tax_code: tax.code,
            tax_name: tax.name,
            tax_rate: tax.rate,
          },
        ])
      }
      setSelectedId('')
      onChanged()
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      setError(apiErr.response?.data?.detail ?? 'Error al añadir impuesto')
    } finally {
      setBusy(false)
    }
  }

  const handleRemove = async (taxId: string) => {
    if (!resource) return
    setBusy(true)
    setError(null)
    try {
      await api.delete(`/resources/${resource.id}/taxes/${taxId}`)
      setItems((prev) => prev.filter((i) => i.tax_id !== taxId))
      onChanged()
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      setError(apiErr.response?.data?.detail ?? 'Error al quitar impuesto')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`Impuestos de "${resource?.name ?? ''}"`}
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

        {/* Lista de impuestos actuales */}
        <div>
          <h3 className="text-sm font-semibold text-slate-700 mb-2">
            Impuestos asignados ({items.length})
          </h3>
          {items.length === 0 ? (
            <p className="text-sm text-slate-500 italic">
              Este recurso no tiene impuestos.
            </p>
          ) : (
            <ul className="divide-y divide-slate-100 border border-slate-200 rounded">
              {items.map((item) => (
                <li
                  key={item.tax_id}
                  className="flex items-center justify-between px-3 py-2"
                >
                  <div>
                    <span className="font-medium text-slate-900">
                      {item.tax_name}
                    </span>
                    <Badge variant="green" className="ml-2">
                      {item.tax_rate}%
                    </Badge>
                  </div>
                  <Button
                    size="sm"
                    variant="danger"
                    onClick={() => handleRemove(item.tax_id)}
                    disabled={busy}
                  >
                    Quitar
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Añadir nuevo impuesto */}
        <div>
          <h3 className="text-sm font-semibold text-slate-700 mb-2">
            Añadir impuesto
          </h3>
          <Select
            value={selectedId}
            onChange={(e) => setSelectedId(e.target.value)}
            disabled={loadingTaxes || busy}
          >
            <option value="">— Selecciona un impuesto —</option>
            {available.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name} ({t.rate}%)
              </option>
            ))}
          </Select>
          <Button
            onClick={handleAdd}
            disabled={!selectedId || busy}
            className="w-full mt-3"
          >
            {busy ? 'Añadiendo...' : '+ Añadir impuesto'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}