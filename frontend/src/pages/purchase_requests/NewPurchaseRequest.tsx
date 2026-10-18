import { Link } from 'react-router-dom'

export function NewPurchaseRequest() {
  return (
    <div className="space-y-6">
      <Link
        to="/purchase-requests"
        className="text-sm text-blue-600 hover:underline"
      >
        ← Volver a solicitudes
      </Link>
      <div className="bg-white p-8 rounded-lg shadow text-center">
        <h1 className="text-2xl font-bold text-slate-900 mb-2">
          Nueva solicitud
        </h1>
        <p className="text-slate-500">
          Esta página estará disponible en la Sesión 2.
        </p>
      </div>
    </div>
  )
}