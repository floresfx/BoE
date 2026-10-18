import { useState } from 'react'
import { Button } from '../ui/Button'
import { Badge } from '../ui/Badge'
import { Can } from '../auth/Can'
import { CreateQuoteModal } from './CreateQuoteModal'
import {
  useSelectSupplierQuote,
  useSupplierQuotes,
} from '../../hooks/useSupplierQuotes'
import type {
  PurchaseRequestLine,
  SupplierQuote,
} from '../../types/purchase_request'

interface Props {
  requestId: string
  lines: PurchaseRequestLine[]
  canCreateQuote: boolean
  canSelectQuote: boolean
}

function QuoteStatusBadge({ quote }: { quote: SupplierQuote }) {
  if (quote.status === 'accepted') {
    return <Badge variant="green">Aceptada</Badge>
  }
  if (quote.status === 'rejected') {
    return <Badge variant="red">Rechazada</Badge>
  }
  return <Badge variant="yellow">Pendiente</Badge>
}

export function QuotesSection({
  requestId,
  lines,
  canCreateQuote,
  canSelectQuote,
}: Props) {
  const [selectedLine, setSelectedLine] =
    useState<PurchaseRequestLine | null>(null)
  const [quoteModalOpen, setQuoteModalOpen] = useState(false)
  const { data, isLoading } = useSupplierQuotes(requestId)
  const selectMutation = useSelectSupplierQuote()

  const quotesByLine = (lineId: string) =>
    (data?.items ?? []).filter((q) => q.line_id === lineId)

  const handleSelect = async (quoteId: string) => {
    if (!confirm('¿Seleccionar esta cotización? Las demás se rechazarán.')) {
      return
    }
    try {
      await selectMutation.mutateAsync({ requestId, quoteId })
    } catch (err) {
      const apiErr = err as {
        response?: { data?: { detail?: string } }
      }
      alert(apiErr.response?.data?.detail ?? 'Error al seleccionar')
    }
  }

  const openQuoteModal = (line: PurchaseRequestLine) => {
    setSelectedLine(line)
    setQuoteModalOpen(true)
  }

  if (isLoading) {
    return (
      <div className="p-4 text-center text-slate-500">
        Cargando cotizaciones...
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h3 className="font-semibold text-slate-900">Cotizaciones</h3>

      {lines.length === 0 ? (
        <p className="text-sm text-slate-500">
          Esta solicitud no tiene líneas para cotizar.
        </p>
      ) : (
        lines.map((line) => {
          const lineQuotes = quotesByLine(line.id)
          return (
            <div
              key={line.id}
              className="border border-slate-200 rounded-lg p-3 space-y-2"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-slate-900">
                    {line.resource_name}
                  </p>
                  <p className="text-xs text-slate-500">
                    Solicitado: {line.quantity}
                  </p>
                </div>
                {canCreateQuote && (
                  <Can module="supplier_quote" action="crear">
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => openQuoteModal(line)}
                    >
                      + Cotizar
                    </Button>
                  </Can>
                )}
              </div>

              {lineQuotes.length === 0 ? (
                <p className="text-xs text-slate-500 italic">
                  Sin cotizaciones.
                </p>
              ) : (
                <table className="w-full text-xs">
                  <thead className="border-b border-slate-200 text-slate-600">
                    <tr>
                      <th className="text-left py-1">Proveedor</th>
                      <th className="text-right py-1">Precio</th>
                      <th className="text-right py-1">Lead time</th>
                      <th className="text-left py-1">Estado</th>
                      <th className="text-right py-1">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {lineQuotes.map((quote) => (
                      <tr key={quote.id} className="border-b border-slate-100">
                        <td className="py-1">{quote.supplier_name}</td>
                        <td className="text-right py-1">
                          {quote.unit_price} {quote.currency_code}
                        </td>
                        <td className="text-right py-1">
                          {quote.lead_time_days}d
                        </td>
                        <td className="py-1">
                          <QuoteStatusBadge quote={quote} />
                        </td>
                        <td className="text-right py-1">
                          {quote.status === 'pending' &&
                            canSelectQuote && (
                              <Can
                                module="supplier_quote"
                                action="seleccionar"
                              >
                                <Button
                                  size="sm"
                                  variant="secondary"
                                  onClick={() => handleSelect(quote.id)}
                                  disabled={selectMutation.isPending}
                                >
                                  Seleccionar
                                </Button>
                              </Can>
                            )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )
        })
      )}

      <CreateQuoteModal
        open={quoteModalOpen}
        requestId={requestId}
        line={selectedLine}
        onClose={() => {
          setQuoteModalOpen(false)
          setSelectedLine(null)
        }}
      />
    </div>
  )
}