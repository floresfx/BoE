import { useEffect, useState } from 'react'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { useAuth } from '../hooks/useAuth'
import { useTenantSettings, useUpdateTenantSettings } from '../hooks/useSettings'
import type { CostingMethod } from '../types/settings'

export function Settings() {
  const { user } = useAuth()
  const tenantId = user?.tenant_id ?? null

  const { data: settings, isLoading } = useTenantSettings(tenantId)
  const updateMutation = useUpdateTenantSettings()

  const [method, setMethod] = useState<CostingMethod>('fifo')

  useEffect(() => {
    if (settings?.inventory_costing_method) {
      setMethod(settings.inventory_costing_method)
    }
  }, [settings])

  const handleSave = async () => {
    try {
      await updateMutation.mutateAsync({
        inventory_costing_method: method,
      })
      alert('Configuración guardada.')
    } catch (err) {
      const apiErr = err as {
        response?: { data?: { detail?: string } }
      }
      alert(
        apiErr.response?.data?.detail ??
          'Error al guardar la configuración.',
      )
    }
  }

  if (isLoading) {
    return (
      <div className="p-8 text-center text-slate-500">Cargando...</div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Configuración
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Configuración general de tu empresa.
        </p>
      </div>

      <div className="bg-white p-6 rounded-lg shadow space-y-4">
        <h2 className="text-lg font-semibold text-slate-900">
          Costeo de inventario
        </h2>
        <p className="text-sm text-slate-600">
          Elige el método de costeo para calcular el costo real de las
          salidas de inventario.
        </p>

        <div className="space-y-2">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="radio"
              name="costing-method"
              value="fifo"
              checked={method === 'fifo'}
              onChange={() => setMethod('fifo')}
            />
            <div>
              <p className="font-medium">FIFO</p>
              <p className="text-xs text-slate-500">
                Primero entrado, primero salido. Compatible con IFRS.
              </p>
            </div>
          </label>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="radio"
              name="costing-method"
              value="lifo"
              checked={method === 'lifo'}
              onChange={() => setMethod('lifo')}
            />
            <div>
              <p className="font-medium flex items-center gap-2">
                LIFO
                <Badge variant="yellow">Advertencia</Badge>
              </p>
              <p className="text-xs text-slate-500">
                Último entrado, primero salido. No permitido bajo IFRS.
              </p>
            </div>
          </label>
        </div>

        {method === 'lifo' && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800">
            <strong>Advertencia legal:</strong> El método LIFO no está
            permitido bajo normas IFRS. Si tu empresa reporta bajo IFRS,
            selecciona FIFO. El uso de LIFO es responsabilidad del usuario
            y debe alinearse con su normativa local.
          </div>
        )}

        <div className="flex justify-end pt-4 border-t border-slate-200">
          <Button onClick={handleSave} disabled={updateMutation.isPending}>
            {updateMutation.isPending ? 'Guardando...' : 'Guardar'}
          </Button>
        </div>
      </div>
    </div>
  )
}