import { Navigate, Route, Routes } from 'react-router-dom'
import { ProtectedRoute } from './components/ProtectedRoute'
import { Layout } from './components/layout/Layout'
import { Dashboard } from './pages/Dashboard'
import { Login } from './pages/Login'
import { NotFound } from './pages/NotFound'
import { Register } from './pages/Register'
import { SelectPlan } from './pages/SelectPlan'
import { ResourcesList } from './pages/resources/ResourcesList'
import { Catalogs } from './pages/Catalogs'
import { Admin } from './pages/Admin'
import { Inventory } from './pages/inventory/Inventory'

export function App() {
  return (
    <Routes>
      {/* Rutas públicas */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Selección de plan (requiere auth, pero sin Layout) */}
      <Route
        path="/select-plan"
        element={
          <ProtectedRoute>
            <SelectPlan />
          </ProtectedRoute>
        }
      />

      {/* Rutas privadas con Layout */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="resources" element={<ResourcesList />} />
        <Route path="catalogs" element={<Catalogs />} />
        <Route path="inventory" element={<Inventory />} />
        <Route path="admin" element={<Admin />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}

export default App