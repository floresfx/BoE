import { useState } from 'react'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import {
  useAdminAttributes,
  useAdminCategories,
  useAdminCountries,
  useAdminCurrencies,
  useAdminDocumentTypes,
  useAdminFeatures,
  useAdminPlans,
  useAdminServices,
  useAdminTaxes,
  useAdminUnits,
  useAdminVerticals,
} from '../hooks/useAdmin'
import { AdminCrudModal } from './admin/AdminCrudModal'
import {
  ATTRIBUTES_FIELDS,
  CATEGORIES_FIELDS,
  COUNTRIES_FIELDS,
  CURRENCIES_FIELDS,
  DOCUMENT_TYPES_FIELDS,
  FEATURES_FIELDS,
  PLANS_FIELDS,
  SERVICES_FIELDS,
  TAXES_FIELDS,
  UNITS_FIELDS,
  VERTICALS_FIELDS,
} from './admin/fieldConfigs'

type Tab =
  | 'plans' | 'features' | 'verticals' | 'attributes' | 'taxes'
  | 'services' | 'currencies' | 'units' | 'categories'
  | 'countries' | 'document-types'

const TABS: { id: Tab; label: string }[] = [
  { id: 'plans', label: 'Planes' },
  { id: 'features', label: 'Features' },
  { id: 'verticals', label: 'Verticales' },
  { id: 'attributes', label: 'Atributos' },
  { id: 'taxes', label: 'Impuestos' },
  { id: 'services', label: 'Servicios' },
  { id: 'currencies', label: 'Monedas' },
  { id: 'units', label: 'Unidades' },
  { id: 'categories', label: 'Categorías' },
  { id: 'countries', label: 'Países' },
  { id: 'document-types', label: 'Tipos Documento' },
]

export function Admin() {
  const [activeTab, setActiveTab] = useState<Tab>('plans')

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Panel de Administración
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Gestión de datos maestros globales del SaaS. Solo SuperAdmin.
        </p>
      </div>

      <div className="border-b border-slate-200 overflow-x-auto">
        <nav className="flex gap-2 -mb-px">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 text-sm font-medium border-b-2 whitespace-nowrap ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        {activeTab === 'plans' && <CrudSection
          title="Planes"
          hook={useAdminPlans}
          fields={PLANS_FIELDS}
          columns={[
            { key: 'code', label: 'Código' },
            { key: 'name', label: 'Nombre' },
            { key: 'price', label: 'Precio', prefix: '$' },
            { key: 'interval', label: 'Intervalo' },
            { key: 'trial_days', label: 'Trial' },
            { key: 'is_active', label: 'Estado', isBadge: true },
          ]}
        />}
        {activeTab === 'features' && <CrudSection
          title="Features"
          hook={useAdminFeatures}
          fields={FEATURES_FIELDS}
          columns={[
            { key: 'code', label: 'Código' },
            { key: 'name', label: 'Nombre' },
            { key: 'applies_to', label: 'Aplica a' },
            { key: 'is_active', label: 'Estado', isBadge: true },
          ]}
        />}
        {activeTab === 'verticals' && <CrudSection
          title="Verticales"
          hook={useAdminVerticals}
          fields={VERTICALS_FIELDS}
          columns={[
            { key: 'code', label: 'Código' },
            { key: 'name', label: 'Nombre' },
            { key: 'description', label: 'Descripción' },
            { key: 'is_active', label: 'Estado', isBadge: true },
          ]}
        />}
        {activeTab === 'attributes' && <CrudSection
          title="Atributos"
          hook={useAdminAttributes}
          fields={ATTRIBUTES_FIELDS}
          columns={[
            { key: 'code', label: 'Código' },
            { key: 'name', label: 'Nombre' },
            { key: 'type_code', label: 'Tipo' },
            { key: 'is_active', label: 'Estado', isBadge: true },
          ]}
        />}
        {activeTab === 'taxes' && <CrudSection
          title="Impuestos"
          hook={useAdminTaxes}
          fields={TAXES_FIELDS}
          columns={[
            { key: 'country_code', label: 'País' },
            { key: 'code', label: 'Código' },
            { key: 'name', label: 'Nombre' },
            { key: 'rate', label: 'Tasa', suffix: '%' },
            { key: 'is_active', label: 'Estado', isBadge: true },
          ]}
        />}
        {activeTab === 'services' && <CrudSection
          title="Servicios"
          hook={useAdminServices}
          fields={SERVICES_FIELDS}
          columns={[
            { key: 'code', label: 'Código' },
            { key: 'name', label: 'Nombre' },
            { key: 'description', label: 'Descripción' },
            { key: 'is_active', label: 'Estado', isBadge: true },
          ]}
        />}
        {activeTab === 'currencies' && <CrudSection
          title="Monedas"
          hook={useAdminCurrencies}
          fields={CURRENCIES_FIELDS}
          columns={[
            { key: 'code', label: 'Código' },
            { key: 'name', label: 'Nombre' },
            { key: 'symbol', label: 'Símbolo' },
            { key: 'decimals', label: 'Decimales' },
            { key: 'is_base', label: 'Base', isBadge: true, badgeTrue: 'Sí' },
            { key: 'is_active', label: 'Estado', isBadge: true },
          ]}
        />}
        {activeTab === 'units' && <CrudSection
          title="Unidades"
          hook={useAdminUnits}
          fields={UNITS_FIELDS}
          columns={[
            { key: 'code', label: 'Código' },
            { key: 'name', label: 'Nombre' },
            { key: 'symbol', label: 'Símbolo' },
            { key: 'is_base', label: 'Base', isBadge: true, badgeTrue: 'Sí' },
            { key: 'is_active', label: 'Estado', isBadge: true },
          ]}
        />}
        {activeTab === 'categories' && <CrudSection
          title="Categorías"
          hook={useAdminCategories}
          fields={CATEGORIES_FIELDS}
          columns={[
            { key: 'code', label: 'Código' },
            { key: 'name', label: 'Nombre' },
            { key: 'is_active', label: 'Estado', isBadge: true },
          ]}
        />}
        {activeTab === 'countries' && <CrudSection
          title="Países"
          hook={useAdminCountries}
          fields={COUNTRIES_FIELDS}
          columns={[
            { key: 'code', label: 'Código' },
            { key: 'name', label: 'Nombre' },
            { key: 'phone_prefix', label: 'Prefijo' },
            { key: 'is_active', label: 'Estado', isBadge: true },
          ]}
        />}
        {activeTab === 'document-types' && <CrudSection
          title="Tipos de Documento"
          hook={useAdminDocumentTypes}
          fields={DOCUMENT_TYPES_FIELDS}
          columns={[
            { key: 'code', label: 'Código' },
            { key: 'name', label: 'Nombre' },
            { key: 'format', label: 'Formato' },
            { key: 'is_active', label: 'Estado', isBadge: true },
          ]}
        />}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// CrudSection — sección con tabla + modal
// ---------------------------------------------------------------------------

interface Column {
  key: string
  label: string
  isBadge?: boolean
  badgeTrue?: string
  prefix?: string
  suffix?: string
}

interface CrudSectionProps {
  title: string
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  hook: () => any
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  fields: any[]
  columns: Column[]
}

function CrudSection({ title, hook, fields, columns }: CrudSectionProps) {
  const { query, create, update } = hook()
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Record<string, unknown> | null>(null)

  const handleNew = () => {
    setEditing(null)
    setModalOpen(true)
  }

  const handleEdit = (row: Record<string, unknown>) => {
    setEditing(row)
    setModalOpen(true)
  }

  const handleSubmit = async (values: Record<string, unknown>) => {
    try {
      if (editing) {
        await update.mutateAsync({ id: editing.id as string, payload: values })
      } else {
        await create.mutateAsync(values)
      }
      setModalOpen(false)
      setEditing(null)
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      alert(apiErr.response?.data?.detail ?? 'Error al guardar')
    }
  }

  if (query.isLoading) {
    return <div className="p-8 text-center text-slate-500">Cargando...</div>
  }
  if (query.error) {
    return <div className="p-8 text-center text-red-600">Error al cargar {title}</div>
  }
  if (!query.data?.length) {
    return (
      <div className="p-8 text-center text-slate-500">
        No hay {title.toLowerCase()}.{' '}
        <button onClick={handleNew} className="text-blue-600 underline">
          Crear la primera
        </button>
      </div>
    )
  }

  return (
    <>
      <div className="p-4 border-b border-slate-200 flex items-center justify-between">
        <h2 className="font-semibold text-slate-700">
          {title} ({query.data.length})
        </h2>
        <Button size="sm" onClick={handleNew}>
          + Nuevo
        </Button>
      </div>

      <table className="w-full text-sm">
        <thead className="bg-slate-50 border-b border-slate-200">
          <tr>
            {columns.map((c) => (
              <th
                key={c.key}
                className="text-left px-4 py-3 font-medium text-slate-700"
              >
                {c.label}
              </th>
            ))}
            <th className="text-right px-4 py-3 font-medium text-slate-700">
              Acciones
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {query.data.map((row: Record<string, unknown>) => (
            <tr key={row.id as string} className="hover:bg-slate-50">
              {columns.map((c) => (
                <td key={c.key} className="px-4 py-3 text-slate-700">
                  {c.isBadge ? (
                    row[c.key] ? (
                      <Badge variant="green">{c.badgeTrue ?? 'Activo'}</Badge>
                    ) : (
                      <Badge variant="gray">Inactivo</Badge>
                    )
                  ) : (
                    <span className="font-mono text-xs">
                      {c.prefix ?? ''}
                      {String(row[c.key] ?? '—')}
                      {c.suffix ?? ''}
                    </span>
                  )}
                </td>
              ))}
              <td className="px-4 py-3 text-right">
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => handleEdit(row)}
                >
                  Editar
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <AdminCrudModal
        open={modalOpen}
        title={editing ? `Editar ${title.slice(0, -1)}` : `Nuevo ${title.slice(0, -1)}`}
        fields={fields}
        initialValues={editing}
        isLoading={create.isPending || update.isPending}
        onSubmit={handleSubmit}
        onCancel={() => {
          setModalOpen(false)
          setEditing(null)
        }}
      />
    </>
  )
}