import type { AvailabilityResponse, AvailabilityStatus } from '../../types/availability'
import { Badge } from '../ui/Badge'

function StatusBadge({ status }: { status: AvailabilityStatus }) {
  if (status === 'covered') return <Badge variant="green">Cubierto</Badge>
  if (status === 'partial') return <Badge variant="yellow">Parcial</Badge>
  return <Badge variant="red">Sin stock</Badge>
}

interface Props {
  result: AvailabilityResponse
}

export function AvailabilityResult({ result }: Props) {
  return (
    <div className="bg-white p-6 rounded-lg shadow space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">{result.resource_name}</h2>
        <StatusBadge status={result.status} />
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <p className="text-sm text-slate-500">Requerido</p>
          <p className="text-xl font-bold">{result.required_quantity}</p>
        </div>
        <div>
          <p className="text-sm text-slate-500">Disponible</p>
          <p className="text-xl font-bold text-green-600">
            {result.available_quantity}
          </p>
        </div>
        <div>
          <p className="text-sm text-slate-500">Faltante</p>
          <p className="text-xl font-bold text-red-600">
            {result.missing_quantity}
          </p>
        </div>
      </div>

      {result.warehouses.length > 0 && (
        <div>
          <h3 className="font-semibold mb-2">Desglose por almacén:</h3>
          <ul className="divide-y divide-slate-100">
            {result.warehouses.map((w) => (
              <li
                key={w.warehouse_id}
                className="py-2 flex items-center justify-between"
              >
                <span>{w.warehouse_name}</span>
                <span className="text-slate-600">{w.available}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {result.suppliers.length > 0 && (
        <div>
          <h3 className="font-semibold mb-2">Proveedores sugeridos:</h3>
          <ul className="divide-y divide-slate-100">
            {result.suppliers.map((s) => (
              <li
                key={s.supplier_id}
                className="py-2 flex items-center justify-between"
              >
                <span className="font-medium">{s.supplier_name}</span>
                <span className="text-sm text-slate-600">
                  {s.unit_price} {s.currency_code} · {s.lead_time_days} días
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}