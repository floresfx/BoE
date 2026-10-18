import type { ReactNode } from 'react'
import { usePermissions } from '../../hooks/usePermissions'

interface Props {
  module: string
  action: string
  children: ReactNode
  fallback?: ReactNode
}

/**
 * Renderiza `children` solo si el usuario tiene el permiso.
 *
 * Uso:
 *   <Can module="resource" action="crear">
 *     <Button>+ Nuevo recurso</Button>
 *   </Can>
 */
export function Can({ module, action, children, fallback = null }: Props) {
  const { can, isLoading } = usePermissions()

  if (isLoading) return null
  if (!can(module, action)) return <>{fallback}</>
  return <>{children}</>
}