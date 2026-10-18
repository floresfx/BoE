import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { useBundleCost } from '../../hooks/useBundleCost'

export function BundleCost() {
  const { bundleId } = useParams<{ bundleId: string }>()
  const [multiplier, setMultiplier] = useState(1)

  const { data, isLoading, error, refetch } = useBundleCost(
    bundleId ?? '',
    multiplier,
  )

  if (!bundleId) {
    return (
      <div className="p-8 text-center text-red-600">
        Bundle no especificado.
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="p-8 text-center text-slate-500">Cargando costos...</div>
    )
  }

  if (error) {
    return (
      <div className="p-8 text-center text-red-600">
        Error al cargar costos: {(error as Error).message}
      </div>
    )
  }

  if (!data) return null

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <Link
            to="/bundles"
            className="text-sm text-blue-600 hover:underline"
          >
            ← Volver a bundles
          </Link>
          <h1 className="text-2xl font-bold text-slate-900 mt-2">
            Costos: {data.bundle_name}
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Análisis de costos del bundle con multiplicador
          </p>
        </div>
      </div>

      {/* Controles */}
      <div className="bg-white p-4 rounded-lg shadow flex items-end gap-4">
        <div className="w-40">
          <Input
            label="Multiplicador"
            type="number"
            min={0.01}
            step="any"
            value={multiplier}
            onChange={(e) => setMultiplier(Number(e.target.value) || 0)}
          />
        </div>
        <Button onClick={() => refetch()}>Recalcular</Button>
      </div>

      {/* Tarjetas de totales */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-slate-500">Materiales</p>
          <p className="text-2xl font-bold">
            {data.breakdown.materials_cost} {data.currency_code}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-slate-500">Merma</p>
          <p className="text-2xl font-bold text-yellow-600">
            {data.breakdown.waste_cost} {data.currency_code}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-slate-500">Mano de obra</p>
          <p className="text-2xl font-bold">
            {data.breakdown.labor_cost} {data.currency_code}
          </p>
        </div>
        <div className="bg-blue-50 p-4 rounded-lg shadow border-2 border-blue-200">
          <p className="text-sm text-blue-700">Costo total</p>
          <p className="text-2xl font-bold text-blue-900">
            {data.total_cost} {data.currency_code}
          </p>
        </div>
      </div>

      {/* Tabla de líneas */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-slate-700">
                Recurso
              </th>
              <th className="text-right px-4 py-3 font-medium text-slate-700">
                Cantidad
              </th>
              <th className="text-right px-4 py-3 font-medium text-slate-700">
                Costo unit.
              </th>
              <th className="text-right px-4 py-3 font-medium text-slate-700">
                Merma %
              </th>
              <th className="text-right px-4 py-3 font-medium text-slate-700">
                Costo con merma
              </th>
              <th className="text-left px-4 py-3 font-medium text-slate-700">
                Proveedor usado
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {data.lines.length === 0 ? (
              <tr>
                <td
                  colSpan={6}
                  className="px-4 py-8 text-center text-slate-500"
                >
                  Este bundle no tiene componentes. Añade componentes para ver
                  los costos.
                </td>
              </tr>
            ) : (
              data.lines.map((line) => (
                <tr key={line.resource_id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium">
                    {line.resource_name}
                  </td>
                  <td className="px-4 py-3 text-right">{line.quantity}</td>
                  <td className="px-4 py-3 text-right">{line.unit_cost}</td>
                  <td className="px-4 py-3 text-right">
                    {line.waste_percent}%
                  </td>
                  <td className="px-4 py-3 text-right font-medium">
                    {line.line_cost}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {line.supplier_used ?? (
                      <span className="text-slate-400 italic">
                        Sin proveedor (costo base)
                      </span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Resumen de cálculo */}
      <div className="bg-slate-50 p-4 rounded-lg text-sm text-slate-600">
        <p>
          <strong>Cómo se calcula:</strong> Para cada componente, se toma la
          oferta más barata del proveedor (o el costo base del recurso si no
          hay oferta), se multiplica por la cantidad y se añade la merma
          configurada. El total se multiplica por el multiplicador.
        </p>
      </div>
    </div>
  )
}