import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '../components/ui/Button'
import {
  useAvailablePlans,
  useSelectPlan,
} from '../hooks/useSubscription'

export function SelectPlan() {
  const navigate = useNavigate()
  const { data: plans = [], isLoading } = useAvailablePlans()
  const selectPlan = useSelectPlan()
  const [selected, setSelected] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSelect = async (planId: string) => {
    setError(null)
    setSelected(planId)
    try {
      await selectPlan.mutateAsync(planId)
      navigate('/dashboard')
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      setError(
        apiErr.response?.data?.detail ?? 'Error al seleccionar el plan.',
      )
      setSelected(null)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold text-slate-900">
            Elige tu plan
          </h1>
          <p className="text-slate-500 mt-2">
            Comienza con 14 días gratis en los planes MPR. Cancela cuando quieras.
          </p>
        </div>

        {error && (
          <div className="mb-6 max-w-lg mx-auto p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700 text-center">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="text-center text-slate-500">Cargando planes...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {plans.map((plan) => {
              const isMPR = plan.code.startsWith('mpr_')
              const isSelected = selected === plan.id
              const isPending = selectPlan.isPending && isSelected

              return (
                <div
                  key={plan.id}
                  className={`bg-white rounded-lg shadow-md p-6 flex flex-col border-2 ${
                    isMPR ? 'border-blue-500' : 'border-transparent'
                  }`}
                >
                  {isMPR && (
                    <div className="inline-block bg-blue-100 text-blue-700 text-xs font-semibold px-2 py-1 rounded mb-3 self-start">
                      MPR
                    </div>
                  )}

                  <h3 className="text-xl font-bold text-slate-900">
                    {plan.name}
                  </h3>

                  <div className="mt-2 mb-4">
                    <span className="text-3xl font-bold text-slate-900">
                      ${plan.price}
                    </span>
                    <span className="text-slate-500 text-sm">
                      /{plan.interval}
                    </span>
                  </div>

                  {plan.trial_days > 0 && (
                    <p className="text-sm text-green-700 bg-green-50 px-2 py-1 rounded mb-4">
                      🎉 {plan.trial_days} días gratis
                    </p>
                  )}

                  <ul className="space-y-2 mb-6 flex-1">
                    {plan.features.slice(0, 6).map((f) => (
                      <li
                        key={f}
                        className="text-sm text-slate-600 flex items-start gap-2"
                      >
                        <span className="text-green-600 mt-0.5">✓</span>
                        <span>{f}</span>
                      </li>
                    ))}
                  </ul>

                  <div className="text-xs text-slate-500 mb-4 space-y-1">
                    {Object.entries(plan.limits).map(([k, v]) => (
                      <div key={k} className="flex justify-between">
                        <span>{k}</span>
                        <span className="font-medium">
                          {v === null ? '∞' : v}
                        </span>
                      </div>
                    ))}
                  </div>

                  <Button
                    onClick={() => handleSelect(plan.id)}
                    disabled={isPending || selectPlan.isPending}
                    variant={isMPR ? 'primary' : 'secondary'}
                  >
                    {isPending ? 'Activando...' : 'Seleccionar'}
                  </Button>
                </div>
              )
            })}
          </div>
        )}

        <p className="text-center text-xs text-slate-400 mt-8">
          Puedes cambiar de plan en cualquier momento desde tu dashboard.
        </p>
      </div>
    </div>
  )
}