import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Modal } from '../../components/ui/Modal'
import { Select } from '../../components/ui/Select'
import { useResources } from '../../hooks/useResources'
import { useSuppliers } from '../../hooks/useSuppliers'
import { useCreatePurchaseRequest } from '../../hooks/usePurchaseRequests'
import type { PurchaseRequestLineInline } from '../../types/purchase_request'

const schema = z.object({
  code: z.string().min(1, 'Requerido').max(50),
  needed_by: z.string().optional().or(z.literal('')),
  notes: z.string().optional().or(z.literal('')),
})

type FormValues = z.infer<typeof schema>

interface Props {
  open: boolean
  onClose: () => void
}

export function PurchaseRequestForm({ open, onClose }: Props) {
  const create = useCreatePurchaseRequest()
  const { data: resourcesData } = useResources({ is_active: true, limit: 500 })
  const { data: suppliersData } = useSuppliers({ is_active: true })

  const [lines, setLines] = useState<PurchaseRequestLineInline[]>([])
  const [selectedResource, setSelectedResource] = useState('')
  const [selectedSupplier, setSelectedSupplier] = useState('')
  const [quantity, setQuantity] = useState('')

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { code: '', needed_by: '', notes: '' },
  })

  useEffect(() => {
    if (open) {
      reset({ code: '', needed_by: '', notes: '' })
      setLines([])
      setSelectedResource('')
      setSelectedSupplier('')
      setQuantity('')
    }
  }, [open, reset])

  const handleAddLine = () => {
    if (!selectedResource || !quantity) return
    if (lines.some((l) => l.resource_id === selectedResource)) {
      alert('Ese recurso ya está en la solicitud')
      return
    }
    setLines([
      ...lines,
      {
        resource_id: selectedResource,
        quantity,
        supplier_id: selectedSupplier || null,
      },
    ])
    setSelectedResource('')
    setSelectedSupplier('')
    setQuantity('')
  }

  const handleRemoveLine = (resourceId: string) => {
    setLines(lines.filter((l) => l.resource_id !== resourceId))
  }

  const onSubmit = async (values: FormValues) => {
    try {
      await create.mutateAsync({
        code: values.code,
        needed_by: values.needed_by
          ? `${values.needed_by}T00:00:00Z`
          : null,
        notes: values.notes || null,
        lines,
      })
      onClose()
    } catch (err) {
      const apiErr = err as { response?: { data?: { detail?: string } } }
      alert(apiErr.response?.data?.detail ?? 'Error al crear')
    }
  }

  const resourceName = (id: string) =>
    resourcesData?.items.find((r) => r.id === id)?.name ?? id.slice(0, 8)

  const supplierName = (id: string | null | undefined) =>
    id
      ? suppliersData?.items.find((s) => s.id === id)?.name ?? '—'
      : '—'

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Nueva solicitud de compra"
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={create.isPending}>
            Cancelar
          </Button>
          <Button
            type="submit"
            form="purchase-request-form"
            disabled={create.isPending}
          >
            {create.isPending ? 'Creando...' : 'Crear'}
          </Button>
        </>
      }
    >
      <form
        id="purchase-request-form"
        onSubmit={handleSubmit(onSubmit)}
        className="space-y-4"
      >
        <Input
          label="Código"
          placeholder="REQ-2026-001"
          {...register('code')}
          error={errors.code?.message}
        />
        <Input
          label="Fecha requerida (opcional)"
          type="date"
          {...register('needed_by')}
          error={errors.needed_by?.message}
        />
        <Input
          label="Notas (opcional)"
          {...register('notes')}
          error={errors.notes?.message}
        />

        <div className="border-t border-slate-200 pt-4">
          <h3 className="text-sm font-semibold text-slate-700 mb-2">
            Líneas ({lines.length})
          </h3>

          {lines.length > 0 && (
            <ul className="divide-y divide-slate-100 border border-slate-200 rounded mb-3">
              {lines.map((l) => (
                <li
                  key={l.resource_id}
                  className="flex items-center justify-between px-3 py-2 text-sm"
                >
                  <div>
                    <span className="font-medium">{resourceName(l.resource_id)}</span>
                    <span className="ml-3 text-slate-600">
                      {l.quantity} — Proveedor: {supplierName(l.supplier_id)}
                    </span>
                  </div>
                  <Button
                    size="sm"
                    variant="danger"
                    onClick={() => handleRemoveLine(l.resource_id)}
                  >
                    Quitar
                  </Button>
                </li>
              ))}
            </ul>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <Select
              value={selectedResource}
              onChange={(e) => setSelectedResource(e.target.value)}
            >
              <option value="">— Recurso —</option>
              {resourcesData?.items
                .filter((r) => !lines.some((l) => l.resource_id === r.id))
                .map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.name}
                  </option>
                ))}
            </Select>
            <Input
              type="number"
              step="0.0001"
              placeholder="Cantidad"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
            />
            <Select
              value={selectedSupplier}
              onChange={(e) => setSelectedSupplier(e.target.value)}
            >
              <option value="">— Proveedor (opc.) —</option>
              {suppliersData?.items.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </Select>
          </div>
          <Button
            type="button"
            onClick={handleAddLine}
            disabled={!selectedResource || !quantity}
            className="w-full mt-3"
          >
            + Añadir línea
          </Button>
        </div>
      </form>
    </Modal>
  )
}