import { useState } from 'react'
import { Badge } from '../../components/ui/Badge'
import { Input } from '../../components/ui/Input'
import { useCostingReport } from '../../hooks/useCosting'

export function CostingReport() {
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState('')

  const { data, isLoading, error } = useCostingReport({
    from_date: fromDate || undefined,
    to_date: toDate || undefined,
  })

  if (isLoading) {
    return (
      <div className="p-8 text-center text-slate-500">
        Cargando reporte...
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8 text-center text-red-600">
        Error al cargar el reporte.
      </div>
    )
  }

  if (!data) return null

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Reporte de costeo
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Costo real de ventas (COGS) según el método de costeo del tenant.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-500">Método:</span>
          <Badge variant={data.method === 'fifo' ? 'blue' : 'yellow'}>
            {data.method.toUpperCase()}
          </Badge>
        </div>
      </div>

      {data.method === 'lifo' && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800">
          <strong>Advertencia:</strong> El método LIFO no está permitido
          bajo normas IFRS. Si su empresa reporta bajo IFRS, cambie a FIFO.
          El uso de LIFO es responsabilidad del usuario y debe alinearse con
          su normativa local.
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Input
          label="Desde"
          type="date"
          value={fromDate}
          onChange={(e) => setFromDate(e.target.value)}
        />
        <Input
          label="Hasta"
          type="date"
          value={toDate}
          onChange={(e) => setToDate(e.target.value)}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-slate-500">Total consumido</p>
          <p className="text-2xl font-bold">{data.total_quantity}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-slate-500">Costo total (COGS)</p>
          <p className="text-2xl font-bold text-blue-600">
            {data.total_cost} USD
          </p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-slate-700">
                Recurso
              </th>
              <th className="text-right px-4 py-3 font-medium text-slate-700">
                Cantidad consumida
              </th>
              <th className="text-right px-4 py-3 font-medium text-slate-700">
                Costo promedio
              </th>
              <th className="text-right px-4 py-3 font-medium text-slate-700">
                Costo total
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {data.lines.length === 0 ? (
              <tr>
                <td
                  colSpan={4}
                  className="px-4 py-8 text-center text-slate-500"
                >
                  No hay consumos en el período seleccionado.
                </td>
              </tr>
            ) : (
              data.lines.map((line) => (
                <tr key={line.resource_id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium">
                    {line.resource_name}
                  </td>
                  <td className="px-4 py-3 text-right">
                    {line.total_quantity}
                  </td>
                  <td className="px-4 py-3 text-right text-slate-600">
                    {line.avg_unit_cost}
                  </td>
                  <td className="px-4 py-3 text-right font-medium">
                    {line.total_cost}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}