import { useEffect, useState } from 'react'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Modal } from '../../components/ui/Modal'
import { Select } from '../../components/ui/Select'
import { api } from '../../lib/api'
import { useAttributes } from '../../hooks/useCatalogs'
import type { Resource, ResourceAttribute } from '../../types/resource'

interface Props {
  open: boolean
  resource: Resource | null
  onClose: () => void
  onChanged: () => void
}

export function ResourceAttributesModal({
  open,
  resource,
  onClose,
  onChanged,
}: Props) {
  const { data: allAttributes = [], isLoading: loadingAttrs } = useAttributes()
  const [items, setItems] = useState<ResourceAttribute[]>([])
  const [selectedId, setSelectedId] = useState('')
  const [value, setValue] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (open && resource) {
      setItems(resource.attributes ?? [])
      setSelectedId('')
      setValue('')
      setError(null)
    }
  }, [open, resource])

  const available = allAttributes.filter(
    (a) => !items.some((i) => i.attribute_id === a.id),
  )

  const handleAdd = async () => {
    if (!resource || !selectedId) return
    setBusy(true)
    setError(null)
    try {
      const { data } = await api.post<{
        attribute_id: string
        value: string | null
      }>(`/resources/${resource.id}/attributes`, {
        attribute_id: selectedId,
        value: value || null,
      })
      const attr = allAttributes.find((a) => a.id === data.attribute_id)
      if (attr) {
        setItems((prev) => [
          ...prev,
          {
            attribute_id: attr.id,
            attribute_code: attr.code,
            attribute_name: attr.name,
            value: data.value,
          },
        ])
      }
      setSelectedId('')
      setValue('')
      onChanged()
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      setError(apiErr.response?.data?.detail ?? 'Error al añadir atributo')
    } finally {
      setBusy(false)
    }
  }

  const handleRemove = async (attributeId: string) => {
    if (!resource) return
    setBusy(true)
    setError(null)
    try {
      await api.delete(`/resources/${resource.id}/attributes/${attributeId}`)
      setItems((prev) => prev.filter((i) => i.attribute_id !== attributeId))
      onChanged()
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      setError(apiErr.response?.data?.detail ?? 'Error al quitar atributo')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`Atributos de "${resource?.name ?? ''}"`}
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

        {/* Lista de atributos actuales */}
        <div>
          <h3 className="text-sm font-semibold text-slate-700 mb-2">
            Atributos asignados ({items.length})
          </h3>
          {items.length === 0 ? (
            <p className="text-sm text-slate-500 italic">
              Este recurso no tiene atributos.
            </p>
          ) : (
            <ul className="divide-y divide-slate-100 border border-slate-200 rounded">
              {items.map((item) => (
                <li
                  key={item.attribute_id}
                  className="flex items-center justify-between px-3 py-2"
                >
                  <div>
                    <span className="font-medium text-slate-900">
                      {item.attribute_name}
                    </span>
                    {item.value && (
                      <Badge variant="blue" className="ml-2">
                        {item.value}
                      </Badge>
                    )}
                  </div>
                  <Button
                    size="sm"
                    variant="danger"
                    onClick={() => handleRemove(item.attribute_id)}
                    disabled={busy}
                  >
                    Quitar
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Añadir nuevo atributo */}
        <div>
          <h3 className="text-sm font-semibold text-slate-700 mb-2">
            Añadir atributo
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
            <Select
              value={selectedId}
              onChange={(e) => setSelectedId(e.target.value)}
              disabled={loadingAttrs || busy}
            >
              <option value="">— Selecciona un atributo —</option>
              {available.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                </option>
              ))}
            </Select>
            <input
              type="text"
              placeholder="Valor (opcional)"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              className="rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={busy}
            />
          </div>
          <Button
            onClick={handleAdd}
            disabled={!selectedId || busy}
            className="w-full"
          >
            {busy ? 'Añadiendo...' : '+ Añadir atributo'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}