import { Badge } from '../ui/Badge'
import type { PurchaseRequestStatus } from '../../types/purchase_request'

interface Props {
  status: PurchaseRequestStatus
}

const STATUS_LABELS: Record<PurchaseRequestStatus, string> = {
  draft: 'Borrador',
  pending: 'Enviada',
  quoted: 'Cotizada',
  approved: 'Aprobada',
  ordered: 'Ordenada',
  partially_received: 'Parcial',
  completed: 'Completada',
  cancelled: 'Cancelada',
}

const STATUS_VARIANTS: Record<
  PurchaseRequestStatus,
  'gray' | 'blue' | 'yellow' | 'green' | 'red'
> = {
  draft: 'gray',
  pending: 'blue',
  quoted: 'yellow',
  approved: 'green',
  ordered: 'blue',
  partially_received: 'yellow',
  completed: 'green',
  cancelled: 'red',
}

export function StatusBadge({ status }: Props) {
  return (
    <Badge variant={STATUS_VARIANTS[status] ?? 'gray'}>
      {STATUS_LABELS[status] ?? status}
    </Badge>
  )
}