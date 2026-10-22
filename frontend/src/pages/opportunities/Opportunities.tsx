import { useState } from 'react'
import { Badge } from '../../components/ui/Badge'
import { Input } from '../../components/ui/Input'
import { useOpportunities } from '../../hooks/useOpportunities'

export function Opportunities() {
  const [minCoverage, setMinCoverage] = useState(50)
  const { data, isLoading } = useOpportunities(minCoverage)

  if (isLoading) {
    return <div className="p-8 text-center text-slate-500">Cargando oportunidades...</div>
  }

  const items = data?.items ?? []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Oportunidades</h1>
          <p className="text-sm text-slate-500 mt-1">
            ¿Qué puedes producir con el stock actual?
          </p>
        </div>
        <div className="w-48">
          <Input
            label="Cobertura mínima (%)"
            type="number"
            min={0}
            max={100}
            value={minCoverage}
            onChange={(e) => setMinCoverage(Number(e.target.value))}
          />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        {items.length === 0 ? (
          <div className="p-8 text-center text-slate-500">
            No hay oportunidades con cobertura ≥ {minCoverage}%. Prueba a bajar el filtro.
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Bundle</th>
                <th className="text-right px-4 py-3 font-medium text-slate-700">Cobertura</th>
                <th className="text-right px-4 py-3 font-medium text-slate-700">Producible</th>
                <th className="text-right px-4 py-3 font-medium text-slate-700">Costo</th>
                <th className="text-right px-4 py-3 font-medium text-slate-700">Precio Venta</th>
                <th className="text-right px-4 py-3 font-medium text-slate-700">Margen</th>
                <th className="text-left px-4 py-3 font-medium text-slate-700">Cuello de botella</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((op) => (
                <tr key={op.bundle_id} className="hover:bg-slate-50">
                  <td className="px-4 py-3">
                    <div className="font-medium text-slate-900">{op.bundle_name}</div>
                    <div className="text-xs text-slate-500">{op.bundle_code}</div>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Badge variant={Number(op.coverage_percent) === 100 ? 'green' : 'yellow'}>
                      {Number(op.coverage_percent).toFixed(0)}%
                    </Badge>
                    <div className="text-xs text-slate-500 mt-1">
                      {op.components_covered}/{op.components_total}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-right font-medium">
                    {Number(op.max_producible).toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-right text-slate-600">
                    ${Number(op.estimated_cost).toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-right text-slate-600">
                    {op.sale_price ? `$${Number(op.sale_price).toFixed(2)}` : '—'}
                  </td>
                  <td className="px-4 py-3 text-right">
                    {op.estimated_margin ? (
                      <span className={Number(op.estimated_margin) > 0 ? 'text-green-600 font-medium' : 'text-red-600'}>
                        ${Number(op.estimated_margin).toFixed(2)}
                        {op.estimated_margin_percent && (
                          <div className="text-xs">({Number(op.estimated_margin_percent).toFixed(1)}%)</div>
                        )}
                      </span>
                    ) : '—'}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {op.bottleneck ? (
                      <div>
                        <div className="text-sm">{op.bottleneck.resource_name}</div>
                        <div className="text-xs text-red-600">
                          Falta: {Number(op.bottleneck.missing_quantity).toFixed(2)}
                        </div>
                      </div>
                    ) : (
                      <Badge variant="green">Completo</Badge>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}