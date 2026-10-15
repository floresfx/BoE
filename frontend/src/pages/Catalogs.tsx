import { useState } from 'react'
import { Badge } from '../components/ui/Badge'
import {
  useAttributes,
  useCategories,
  useSubcategories,
  useTaxes,
  useUnits,
} from '../hooks/useCatalogs'

type Tab = 'units' | 'categories' | 'subcategories' | 'attributes' | 'taxes'

const TABS: { id: Tab; label: string }[] = [
  { id: 'units', label: 'Unidades' },
  { id: 'categories', label: 'Categorías' },
  { id: 'subcategories', label: 'Subcategorías' },
  { id: 'attributes', label: 'Atributos' },
  { id: 'taxes', label: 'Impuestos' },
]

export function Catalogs() {
  const [activeTab, setActiveTab] = useState<Tab>('units')

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Catálogos</h1>
        <p className="text-sm text-slate-500 mt-1">
          Datos maestros globales del sistema. Solo lectura.
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200">
        <nav className="flex gap-2 -mb-px overflow-x-auto">
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

      {/* Contenido */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {activeTab === 'units' && <UnitsTable />}
        {activeTab === 'categories' && <CategoriesTable />}
        {activeTab === 'subcategories' && <SubcategoriesTable />}
        {activeTab === 'attributes' && <AttributesTable />}
        {activeTab === 'taxes' && <TaxesTable />}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Tablas
// ---------------------------------------------------------------------------

function Loading() {
  return <div className="p-8 text-center text-slate-500">Cargando...</div>
}

function Empty({ message }: { message: string }) {
  return <div className="p-8 text-center text-slate-500">{message}</div>
}

function TableShell({
  headers,
  children,
}: {
  headers: string[]
  children: React.ReactNode
}) {
  return (
    <table className="w-full text-sm">
      <thead className="bg-slate-50 border-b border-slate-200">
        <tr>
          {headers.map((h) => (
            <th
              key={h}
              className="text-left px-4 py-3 font-medium text-slate-700"
            >
              {h}
            </th>
          ))}
        </tr>
      </thead>
      <tbody className="divide-y divide-slate-100">{children}</tbody>
    </table>
  )
}

function UnitsTable() {
  const { data = [], isLoading } = useUnits()
  if (isLoading) return <Loading />
  if (!data.length) return <Empty message="No hay unidades" />
  return (
    <TableShell headers={['Código', 'Nombre', 'Símbolo', 'Base']}>
      {data.map((u) => (
        <tr key={u.id} className="hover:bg-slate-50">
          <td className="px-4 py-3 font-mono text-xs text-slate-600">
            {u.code}
          </td>
          <td className="px-4 py-3 font-medium text-slate-900">{u.name}</td>
          <td className="px-4 py-3 text-slate-600">{u.symbol}</td>
          <td className="px-4 py-3">
            {u.is_base ? (
              <Badge variant="green">Sí</Badge>
            ) : (
              <span className="text-slate-400">—</span>
            )}
          </td>
        </tr>
      ))}
    </TableShell>
  )
}

function CategoriesTable() {
  const { data = [], isLoading } = useCategories()
  if (isLoading) return <Loading />
  if (!data.length) return <Empty message="No hay categorías" />
  return (
    <TableShell headers={['Código', 'Nombre']}>
      {data.map((c) => (
        <tr key={c.id} className="hover:bg-slate-50">
          <td className="px-4 py-3 font-mono text-xs text-slate-600">
            {c.code}
          </td>
          <td className="px-4 py-3 font-medium text-slate-900">{c.name}</td>
        </tr>
      ))}
    </TableShell>
  )
}

function SubcategoriesTable() {
  const { data: categories = [] } = useCategories()
  const { data = [], isLoading } = useSubcategories()
  if (isLoading) return <Loading />
  if (!data.length) return <Empty message="No hay subcategorías" />
  const categoriesMap = Object.fromEntries(categories.map((c) => [c.id, c]))
  return (
    <TableShell headers={['Código', 'Nombre', 'Categoría']}>
      {data.map((s) => (
        <tr key={s.id} className="hover:bg-slate-50">
          <td className="px-4 py-3 font-mono text-xs text-slate-600">
            {s.code}
          </td>
          <td className="px-4 py-3 font-medium text-slate-900">{s.name}</td>
          <td className="px-4 py-3 text-slate-600">
            {categoriesMap[s.category_id]?.name ?? '—'}
          </td>
        </tr>
      ))}
    </TableShell>
  )
}

function AttributesTable() {
  const { data = [], isLoading } = useAttributes()
  if (isLoading) return <Loading />
  if (!data.length) return <Empty message="No hay atributos" />
  return (
    <TableShell headers={['Código', 'Nombre']}>
      {data.map((a) => (
        <tr key={a.id} className="hover:bg-slate-50">
          <td className="px-4 py-3 font-mono text-xs text-slate-600">
            {a.code}
          </td>
          <td className="px-4 py-3 font-medium text-slate-900">{a.name}</td>
        </tr>
      ))}
    </TableShell>
  )
}

function TaxesTable() {
  const { data = [], isLoading } = useTaxes()
  if (isLoading) return <Loading />
  if (!data.length) return <Empty message="No hay impuestos" />
  return (
    <TableShell headers={['Código', 'Nombre', 'Tasa', 'Aplica a']}>
      {data.map((t) => (
        <tr key={t.id} className="hover:bg-slate-50">
          <td className="px-4 py-3 font-mono text-xs text-slate-600">
            {t.code}
          </td>
          <td className="px-4 py-3 font-medium text-slate-900">{t.name}</td>
          <td className="px-4 py-3">
            <Badge variant="green">{t.rate}%</Badge>
          </td>
          <td className="px-4 py-3 text-slate-600">{t.applies_to}</td>
        </tr>
      ))}
    </TableShell>
  )
}