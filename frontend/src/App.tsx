import { Routes, Route, Navigate } from 'react-router-dom'
import { ProtectedRoute } from './components/ProtectedRoute'
import { Layout } from './components/layout/Layout'
import { Login } from './pages/Login'
import { NotFound } from './pages/NotFound'
import { Register } from './pages/Register'
import { SelectPlan } from './pages/SelectPlan'
import { ResourcesList } from './pages/resources/ResourcesList'
import { Catalogs } from './pages/Catalogs'
import { Admin } from './pages/Admin'
import { Inventory } from './pages/inventory/Inventory'
import { SuppliersList } from './pages/suppliers/SuppliersList'
import { BundlesList } from './pages/bundles/BundlesList'
import { BundleCost } from './pages/bundles/BundleCost'
import { AvailabilityChecker } from './pages/availability/AvailabilityChecker'
import { PurchaseRequestsList } from './pages/purchase_requests/PurchaseRequestsList'
import { PurchaseRequestDetail } from './pages/purchase_requests/PurchaseRequestDetail'
import { NewPurchaseRequest } from './pages/purchase_requests/NewPurchaseRequest'
import { CostingReport } from './pages/inventory/CostingReport'
import { Settings } from './pages/Settings'
import { ProductionKanban } from './pages/production/ProductionKanban'
import { CalendarPage } from './pages/CalendarPage'
import { Dashboard } from './pages/Dashboard' //
import { Opportunities } from './pages/opportunities/Opportunities'


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
        {/* Redirección por defecto: si entras a "/", te manda a "/dashboard" */}
        <Route index element={<Navigate to="/dashboard" replace />} />

        {/* Rutas Hijas */}
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="resources" element={<ResourcesList />} />
        <Route path="catalogs" element={<Catalogs />} />
        <Route path="inventory" element={<Inventory />} />
        <Route path="admin" element={<Admin />} />
        
        {/* Nota: Se ha quitado la barra "/" al inicio de "calendar" para que sea relativa al Layout */}
        <Route path="calendar" element={<CalendarPage />} /> 
        
        <Route path="suppliers" element={<SuppliersList />} />
        <Route path="bundles" element={<BundlesList />} />
        <Route path="bundles/:bundleId/cost" element={<BundleCost />} />
        <Route path="availability" element={<AvailabilityChecker />} />
        <Route path="purchase-requests" element={<PurchaseRequestsList />} />
        <Route path="purchase-requests/new" element={<NewPurchaseRequest />} />
        <Route path="purchase-requests/:requestId" element={<PurchaseRequestDetail />} />
        <Route path="inventory/costing" element={<CostingReport />} />
        <Route path="settings" element={<Settings />} />
        <Route path="production" element={<ProductionKanban />} />
        <Route path="opportunities" element={<Opportunities />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}

export default App