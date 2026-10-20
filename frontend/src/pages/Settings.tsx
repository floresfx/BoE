import { useEffect, useState } from 'react'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import {
  useCatalogAttributes,
  useCatalogCategories,
  useCatalogCurrencies,
  useCatalogUnits,
  useTenantSettings,
  useUpdateTenantSettings,
} from '../hooks/useSettings'
import type { CatalogItem, CostingMethod } from '../types/settings'

export function Settings() {
  // 1. Cargar datos
  const { data: settings, isLoading: loadingSettings } = useTenantSettings()
  const { data: currencies } = useCatalogCurrencies()
  const { data: units } = useCatalogUnits()
  const { data: categories } = useCatalogCategories()
  const { data: attributes } = useCatalogAttributes()
  
  const updateMutation = useUpdateTenantSettings()

  // 2. Estados locales
  const [method, setMethod] = useState<CostingMethod>('fifo')
  const [baseCurrencyId, setBaseCurrencyId] = useState<string>('')
  const [selectedUnits, setSelectedUnits] = useState<string[]>([])
  const [selectedCategories, setSelectedCategories] = useState<string[]>([])
  const [selectedAttributes, setSelectedAttributes] = useState<string[]>([])

  // 3. Sincronizar estado cuando llegan los datos
  useEffect(() => {
    if (settings) {
      setMethod(settings.inventory_costing_method)
      setBaseCurrencyId(settings.base_currency_id || '')
      setSelectedUnits(settings.active_unit_ids || [])
      setSelectedCategories(settings.active_category_ids || [])
      setSelectedAttributes(settings.active_attribute_ids || [])
    }
  }, [settings])

  // 4. Funciones de guardado y toggles
  const handleSave = async () => {
    try {
      await updateMutation.mutateAsync({
        inventory_costing_method: method,
        base_currency_id: baseCurrencyId || null,
        active_unit_ids: selectedUnits,
        active_category_ids: selectedCategories,
        active_attribute_ids: selectedAttributes,
      })
      alert('Configuración guardada correctamente.')
    } catch (err) {
      console.error(err)
      alert('Error al guardar la configuración.')
    }
  }

  const toggleSelection = (
    id: string,
    current: string[],
    setter: (val: string[]) => void,
  ) => {
    if (current.includes(id)) {
      setter(current.filter((item) => item !== id))
    } else {
      setter([...current, id])
    }
  }

  if (loadingSettings) {
    return <div className="p-8 text-center text-slate-500">Cargando configuración...</div>
  }

  // 5. Render
  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Configuración de la Fundación</h1>
        <p className="text-sm text-slate-500 mt-1">Define los datos maestros que usará tu empresa.</p>
      </div>

      {/* BLOQUE 1: Moneda Base */}
      <div className="bg-white p-6 rounded-lg shadow space-y-4">
        <h2 className="text-lg font-semibold text-slate-900">Moneda Base</h2>
        <p className="text-sm text-slate-600">La moneda con la que se mostrarán los precios y costos.</p>
        <select
          className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md border"
          value={baseCurrencyId}
          onChange={(e) => setBaseCurrencyId(e.target.value)}
        >
          <option value="">Seleccione una moneda...</option>
          {currencies?.map((c: CatalogItem) => (
            <option key={c.id} value={c.id}>{c.code} - {c.name}</option>
          ))}
        </select>
      </div>

      {/* BLOQUE 2: Costeo */}
      <div className="bg-white p-6 rounded-lg shadow space-y-4">
        <h2 className="text-lg font-semibold text-slate-900">Costeo de inventario</h2>
        <p className="text-sm text-slate-600">Elige el método de costeo para calcular el costo real de las salidas de inventario.</p>
        <div className="space-y-2">
          <label className="flex items-center gap-3 cursor-pointer">
            <input type="radio" name="costing-method" value="fifo" checked={method === 'fifo'} onChange={() => setMethod('fifo')} />
            <div>
              <p className="font-medium">FIFO</p>
              <p className="text-xs text-slate-500">Primero entrado, primero salido. Compatible con IFRS.</p>
            </div>
          </label>
          <label className="flex items-center gap-3 cursor-pointer">
            <input type="radio" name="costing-method" value="lifo" checked={method === 'lifo'} onChange={() => setMethod('lifo')} />
            <div>
              <p className="font-medium flex items-center gap-2">LIFO <Badge variant="yellow">Advertencia</Badge></p>
              <p className="text-xs text-slate-500">Último entrado, primero salido. No permitido bajo IFRS.</p>
            </div>
          </label>
        </div>
        {method === 'lifo' && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800">
            <strong>Advertencia legal:</strong> El método LIFO no está permitido bajo normas IFRS. Si tu empresa reporta bajo IFRS, selecciona FIFO.
          </div>
        )}
      </div>

      {/* BLOQUE 3: Unidades */}
      <div className="bg-white p-6 rounded-lg shadow space-y-4">
        <h2 className="text-lg font-semibold text-slate-900">Unidades de Medida</h2>
        <p className="text-sm text-slate-600">Selecciona las unidades que usa tu empresa.</p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {units?.map((unit: CatalogItem) => (
            <label key={unit.id} className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedUnits.includes(unit.id)}
                onChange={() => toggleSelection(unit.id, selectedUnits, setSelectedUnits)}
                className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <span className="text-sm text-slate-700">{unit.name} ({unit.symbol})</span>
            </label>
          ))}
        </div>
      </div>

      {/* BLOQUE 4: Categorías */}
      <div className="bg-white p-6 rounded-lg shadow space-y-4">
        <h2 className="text-lg font-semibold text-slate-900">Categorías</h2>
        <p className="text-sm text-slate-600">Selecciona las categorías que usas para clasificar tus productos.</p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {categories?.map((cat: CatalogItem) => (
            <label key={cat.id} className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedCategories.includes(cat.id)}
                onChange={() => toggleSelection(cat.id, selectedCategories, setSelectedCategories)}
                className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <span className="text-sm text-slate-700">{cat.name}</span>
            </label>
          ))}
        </div>
      </div>

      {/* BLOQUE 5: Atributos */}
      <div className="bg-white p-6 rounded-lg shadow space-y-4">
        <h2 className="text-lg font-semibold text-slate-900">Atributos</h2>
        <p className="text-sm text-slate-600">Selecciona los atributos que usas para describir tus productos.</p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {attributes?.map((attr: CatalogItem) => (
            <label key={attr.id} className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedAttributes.includes(attr.id)}
                onChange={() => toggleSelection(attr.id, selectedAttributes, setSelectedAttributes)}
                className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <span className="text-sm text-slate-700">{attr.name}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Botón Guardar */}
      <div className="flex justify-end pt-4 border-t border-slate-200">
        <Button onClick={handleSave} disabled={updateMutation.isPending}>
          {updateMutation.isPending ? 'Guardando...' : 'Guardar Configuración'}
        </Button>
      </div>
    </div>
  )
}