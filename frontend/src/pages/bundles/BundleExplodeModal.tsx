import { useState } from 'react'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Modal } from '../../components/ui/Modal'
import { useExplodeBundle } from '../../hooks/useBundles'
import type { Bundle, BundleExplodeResponse } from '../../types/bundle'

interface Props {
  open: boolean
  bundle: Bundle | null
  onClose: () => void
}

export function BundleExplodeModal({ open, bundle, onClose }: Props) {
  const explodeMutation = useExplodeBundle()
  const [multiplier, setMultiplier] = useState('1')
  const [result, setResult] = useState<BundleExplodeResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  if (!bundle) return null

  const handleExplode = async () => {
    setError(null)
    setResult(null)
    try {
      const data = await explodeMutation.mutateAsync({
        bundleId: bundle.id,
        multiplier,
      })
      setResult(data)
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      setError(apiErr.response?.data?.detail ?? 'Error al explotar')
    }
  }

  return (
    <Modal
      open={open}
      onClose={() => {
        setResult(null)
        setMultiplier('1')
        onClose()
      }}
      title={`Explotar "${bundle.name}"`}
      footer={
        <Button
          variant="secondary"
          onClick={() => {
            setResult(null)
            setMultiplier('1')
            onClose()
          }}
        >
          Cerrar
        </Button>
      }
    >
      <div className="space-y-4">
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="flex gap-2 items-end">
          <div className="flex-1">
            <div>
                <Input
                    label="Multiplicador"
                    type="number"
                    step="0.01"
                    value={multiplier}
                    onChange={(e) => setMultiplier(e.target.value)}
                />
                <p className="text-xs text-slate-500 mt-1">
                    Cuántas veces se multiplica el paquete. Ej: 5 para 500 unidades.
                </p>
            </div>
          </div>
          <Button onClick={handleExplode} disabled={explodeMutation.isPending}>
            {explodeMutation.isPending ? 'Explotando...' : 'Explotar'}
          </Button>
        </div>

        {result && (
          <div>
            <h3 className="text-sm font-semibold text-slate-700 mb-2">
              Recursos requeridos ({result.total_components})
            </h3>
            {result.components.length === 0 ? (
              <p className="text-sm text-slate-500 italic">
                El paquete no tiene componentes.
              </p>
            ) : (
              <table className="w-full text-sm">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th className="text-left px-3 py-2 font-medium text-slate-700">
                      Recurso
                    </th>
                    <th className="text-right px-3 py-2 font-medium text-slate-700">
                      Cantidad
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {result.components.map((c) => (
                    <tr key={c.resource_id}>
                      <td className="px-3 py-2">{c.resource_name}</td>
                      <td className="px-3 py-2 text-right font-mono">
                        {c.required_quantity} {c.resource_unit_symbol ?? ''}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>
    </Modal>
  )
}