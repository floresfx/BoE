import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Select } from '../components/ui/Select'
import { useAuth } from '../hooks/useAuth'
import { api } from '../lib/api'
import { useQuery } from '@tanstack/react-query'

// Cargamos verticales y países disponibles para los selects
function useVerticals() {
  return useQuery({
    queryKey: ['verticals'],
    queryFn: async () => {
      const { data } = await api.get<Array<{ id: string; name: string }>>(
        '/verticals',
      )
      return data
    },
  })
}

function useCountries() {
  return useQuery({
    queryKey: ['countries'],
    queryFn: async () => {
      const { data } = await api.get<Array<{ code: string; name: string }>>(
        '/catalogs/countries',
      )
      return data
    },
  })
}

const schema = z.object({
  company_name: z.string().min(1, 'Requerido').max(100),
  tax_id: z.string().min(1, 'Requerido').max(50),
  tax_id_type: z.string().min(1).max(20),
  vertical_id: z.string().uuid('Selecciona un vertical'),
  country_code: z.string().length(2, 'Requerido'),
  base_currency: z.string().min(1).max(10),
  admin_email: z.string().email('Email inválido'),
  admin_password: z.string().min(8, 'Mínimo 8 caracteres'),
  admin_first_name: z.string().min(1, 'Requerido').max(100),
  admin_last_name: z.string().min(1, 'Requerido').max(100),
  admin_phone: z.string().min(5, 'Requerido').max(20),
})

type FormValues = z.infer<typeof schema>

export function Register() {
  const { register: registerUser } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)

  const { data: verticals = [], isLoading: loadingVerticals } = useVerticals()
  const { data: countries = [], isLoading: loadingCountries } = useCountries()

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      company_name: '',
      tax_id: '',
      tax_id_type: 'RIF',
      vertical_id: '',
      country_code: 'VE',
      base_currency: 'USD',
      admin_email: '',
      admin_password: '',
      admin_first_name: '',
      admin_last_name: '',
      admin_phone: '',
    },
  })

  const onSubmit = async (values: FormValues) => {
    setError(null)
    try {
      await registerUser(values)
      navigate('/login?registered=1')
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      setError(
        apiErr.response?.data?.detail ??
          'Error al registrar. Intenta de nuevo.',
      )
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-white rounded-lg shadow-lg p-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-slate-900">
            Crear cuenta
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Registra tu empresa y comienza a usar BoE MPR.
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Datos de la empresa */}
          <div>
            <h2 className="text-sm font-semibold text-slate-700 mb-3">
              Datos de la empresa
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Nombre de la empresa"
                placeholder="Panadería La Espiga"
                {...register('company_name')}
                error={errors.company_name?.message}
              />
              <Input
                label="RIF / NIT / RUC"
                placeholder="J-12345678-9"
                {...register('tax_id')}
                error={errors.tax_id?.message}
              />
              <Select
                label="Tipo de documento"
                {...register('tax_id_type')}
                error={errors.tax_id_type?.message}
              >
                <option value="RIF">RIF</option>
                <option value="NIT">NIT</option>
                <option value="RUC">RUC</option>
                <option value="RFC">RFC</option>
                <option value="NIF">NIF</option>
              </Select>
              <Select
                label="Vertical"
                {...register('vertical_id')}
                error={errors.vertical_id?.message}
                disabled={loadingVerticals}
              >
                <option value="">— Selecciona —</option>
                {verticals.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.name}
                  </option>
                ))}
              </Select>
              <Select
                label="País"
                {...register('country_code')}
                error={errors.country_code?.message}
                disabled={loadingCountries}
              >
                {countries.map((c) => (
                  <option key={c.code} value={c.code}>
                    {c.name}
                  </option>
                ))}
              </Select>
              <Select
                label="Moneda base"
                {...register('base_currency')}
                error={errors.base_currency?.message}
              >
                <option value="USD">USD - Dólar</option>
                <option value="VES">VES - Bolívar</option>
                <option value="EUR">EUR - Euro</option>
                <option value="COP">COP - Peso colombiano</option>
                <option value="PEN">PEN - Sol peruano</option>
              </Select>
            </div>
          </div>

          {/* Datos del admin */}
          <div>
            <h2 className="text-sm font-semibold text-slate-700 mb-3">
              Datos del administrador
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Nombre"
                {...register('admin_first_name')}
                error={errors.admin_first_name?.message}
              />
              <Input
                label="Apellido"
                {...register('admin_last_name')}
                error={errors.admin_last_name?.message}
              />
              <Input
                label="Email"
                type="email"
                placeholder="admin@empresa.com"
                {...register('admin_email')}
                error={errors.admin_email?.message}
              />
              <Input
                label="Contraseña"
                type="password"
                placeholder="Mínimo 8 caracteres"
                {...register('admin_password')}
                error={errors.admin_password?.message}
              />
              <Input
                label="Teléfono"
                placeholder="+58 412 1234567"
                {...register('admin_phone')}
                error={errors.admin_phone?.message}
              />
            </div>
          </div>

          <div className="flex items-center justify-between pt-4 border-t border-slate-200">
            <Link
              to="/login"
              className="text-sm text-slate-600 hover:text-slate-900"
            >
              ¿Ya tienes cuenta? Inicia sesión
            </Link>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Registrando...' : 'Crear cuenta'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}