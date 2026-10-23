import { useEffect, useState } from 'react'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Modal } from '../../components/ui/Modal'
import { useMarkException } from '../../hooks/useProductionExceptions'

interface Props {
  open: boolean
  onClose: () => void
  order: { id: string; code: string; quantity: number | string } | null
}

export function MarkExceptionModal({ open, onClose, order }: Props) {
  const markException = useMarkException()
  
  const [exceptionType, setExceptionType] = useState('')
  const [actualQuantity, setActualQuantity] = useState('')
  const [notes, setNotes] = useState('')

  useEffect(() => {
    if (!open) {
      setExceptionType('')
      setActualQuantity('')
      setNotes('')
    }
  }, [open])

  if (!order) return null

  const requiresQuantity = exceptionType === 'partial' || exceptionType === 'with_deviation'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!exceptionType) return

    try {
      await markException.mutateAsync({
        orderId: order.id,
        payload: {
          exception_type: exceptionType as any,
          notes: notes.trim() || undefined,
          actual_quantity: requiresQuantity && actualQuantity ? Number(actualQuantity) : undefined,
        },
      })
      await new Promise((resolve) => setTimeout(resolve, 100))
      onClose()
    } catch (err: any) {
      alert(err.response?.data?.detail ?? 'Error al marcar excepción')
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`Marcar excepción — ${order.code}`}
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={markException.isPending}>
            Cancelar
          </Button>
          <Button
            type="submit"
            form="exception-form"
            disabled={!exceptionType || markException.isPending}
          >
            {markException.isPending ? 'Guardando...' : 'Marcar excepción'}
          </Button>
        </>
      }
    >
      <form id="exception-form" onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Tipo de excepción
          </label>
          <select
            value={exceptionType}
            onChange={(e) => setExceptionType(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            required
          >
            <option value="" disabled>— Selecciona —</option>
            <option value="not_executed">No ejecutada</option>
            <option value="partial">Parcial</option>
            <option value="with_deviation">Con desviación</option>
          </select>
        </div>

        {requiresQuantity && (
          <Input
            label="Cantidad real producida"
            type="number"
            step="any"
            value={actualQuantity}
            onChange={(e) => setActualQuantity(e.target.value)}
            placeholder={`Planificado: ${order.quantity}`}
            required
          />
        )}

        <Input
          label="Notas (opcional)"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Motivo de la excepción..."
        />
      </form>
    </Modal>
  )
}