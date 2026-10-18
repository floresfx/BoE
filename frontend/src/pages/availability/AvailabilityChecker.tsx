import { useState } from 'react'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Select } from '../../components/ui/Select'
import { AvailabilityResult } from '../../components/availability/AvailabilityResult'
import {
  useCheckAvailability,
  useCheckBundleAvailability,
} from '../../hooks/useAvailability'
import { useResources } from '../../hooks/useResources'
import { useBundles } from '../../hooks/useBundles'

type Mode = 'resource' | 'bundle'

export function AvailabilityChecker() {
  const [mode, setMode] = useState<Mode>('resource')

  // Resource mode
  const [resourceId, setResourceId] = useState('')
  const [quantity, setQuantity] = useState(1)

  // Bundle mode
  const [bundleId, setBundleId] = useState('')
  const [multiplier, setMultiplier] = useState(1)

  const { data: resources } = useResources({ is_active: true, limit: 500 })
  const { data: bundles } = useBundles({ is_active: true })

  const checkResource = useCheckAvailability()
  const checkBundle = useCheckBundleAvailability()

  const handleResourceSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!resourceId) return
    checkResource.mutate({ resourceId, quantity })
  }

  const handleBundleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!bundleId) return
    checkBundle.mutate({ bundleId, multiplier })
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Verificar disponibilidad</h1>
        <p className="text-sm text-slate-500 mt-1">
          ¿Cuánto tengo y cuánto me falta para cubrir un requerimiento?
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200">
        <nav className="flex gap-2 -mb-px">
          {[
            { id: 'resource' as Mode, label: 'Recurso suelto' },
            { id: 'bundle' as Mode, label: 'Bundle explotado' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setMode(tab.id)}
              className={`px-4 py-2 text-sm font-medium border-b-2 ${
                mode === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Resource mode */}
      {mode === 'resource' && (
        <>
          <form
            onSubmit={handleResourceSubmit}
            className="bg-white p-6 rounded-lg shadow space-y-4"
          >
            <Select
              label="Recurso"
              value={resourceId}
              onChange={(e) => setResourceId(e.target.value)}
            >
              <option value="">— Selecciona —</option>
              {resources?.items.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name}
                </option>
              ))}
            </Select>

            <Input
              label="Cantidad requerida"
              type="number"
              min={0.01}
              step="any"
              value={quantity}
              onChange={(e) => setQuantity(Number(e.target.value) || 0)}
            />

            <Button type="submit" disabled={checkResource.isPending}>
              {checkResource.isPending ? 'Verificando...' : 'Verificar'}
            </Button>
          </form>

          {checkResource.error && (
            <div className="bg-red-50 text-red-700 p-4 rounded-lg">
              Error: {(checkResource.error as Error).message}
            </div>
          )}

          {checkResource.data && (
            <AvailabilityResult result={checkResource.data} />
          )}
        </>
      )}

      {/* Bundle mode */}
      {mode === 'bundle' && (
        <>
          <form
            onSubmit={handleBundleSubmit}
            className="bg-white p-6 rounded-lg shadow space-y-4"
          >
            <Select
              label="Bundle"
              value={bundleId}
              onChange={(e) => setBundleId(e.target.value)}
            >
              <option value="">— Selecciona —</option>
              {bundles?.items.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </Select>

            <Input
              label="Multiplicador"
              type="number"
              min={0.01}
              step="any"
              value={multiplier}
              onChange={(e) => setMultiplier(Number(e.target.value) || 0)}
            />

            <Button type="submit" disabled={checkBundle.isPending}>
              {checkBundle.isPending ? 'Verificando...' : 'Verificar'}
            </Button>
          </form>

          {checkBundle.error && (
            <div className="bg-red-50 text-red-700 p-4 rounded-lg">
              Error: {(checkBundle.error as Error).message}
            </div>
          )}

          {checkBundle.data && (
            <div className="space-y-4">
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold">
                    {checkBundle.data.bundle_name}
                  </h2>
                  <span className="text-sm text-slate-500">
                    Multiplicador: {checkBundle.data.multiplier}
                  </span>
                </div>
              </div>

              {checkBundle.data.lines.length === 0 ? (
                <div className="bg-yellow-50 text-yellow-800 p-4 rounded-lg">
                  Este bundle no tiene componentes registrados. Edita el bundle y añade
                  componentes para poder verificar su disponibilidad.
                </div>
              ) : (
                checkBundle.data.lines.map((line) => (
                  <AvailabilityResult key={line.resource_id} result={line} />
                ))
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}