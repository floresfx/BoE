import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: '🏠', disabled: false },
  { to: '/resources', label: 'Recursos', icon: '🧱', disabled: false },
  { to: '/planificar', label: 'Planificar', icon: '📅', disabled: true },
  { to: '/ejecutar', label: 'Ejecutar', icon: '⚙️', disabled: true },
  { to: '/inventario', label: 'Inventario', icon: '📦', disabled: true },
  { to: '/suministro', label: 'Suministro', icon: '🚚', disabled: true },
  { to: '/revisar', label: 'Revisar', icon: '🔍', disabled: true },
  { to: '/configuracion', label: 'Configuración', icon: '⚙️', disabled: true },
  { to: '/catalogs', label: 'Catálogos', icon: '📚', disabled: false },
  { to: '/admin',label: 'Admin SaaS', icon: '⚙️', disabled: false },
  { to: '/inventory', label: 'Inventario', icon: '📦', disabled: false },
]

export function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900 text-slate-100 min-h-screen flex flex-col">
      <div className="px-6 py-5 border-b border-slate-700">
        <h1 className="text-xl font-bold tracking-tight">BoE MPR</h1>
        <p className="text-xs text-slate-400 mt-1">Planificación y Suministro</p>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              [
                'flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors',
                item.disabled
                  ? 'opacity-40 cursor-not-allowed pointer-events-none'
                  : isActive
                    ? 'bg-slate-700 text-white'
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white',
              ].join(' ')
            }
          >
            <span className="text-base">{item.icon}</span>
            <span>{item.label}</span>
            {item.disabled && (
              <span className="ml-auto text-[10px] uppercase text-slate-500">
                Pronto
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="px-6 py-4 border-t border-slate-700 text-xs text-slate-500">
        v0.1.0
      </div>
    </aside>
  )
}