import type { ReactNode } from 'react'

type Variant = 'green' | 'gray' | 'red' | 'blue' | 'yellow'

interface Props {
  variant?: Variant
  className?: string
  children: ReactNode
}

const variantClasses: Record<Variant, string> = {
  green: 'bg-green-100 text-green-800',
  gray: 'bg-slate-100 text-slate-700',
  red: 'bg-red-100 text-red-800',
  blue: 'bg-blue-100 text-blue-800',
  yellow: 'bg-yellow-100 text-yellow-800',
}

export function Badge({
  variant = 'gray',
  className = '',
  children,
}: Props) {
  return (
    <span
      className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${variantClasses[variant]} ${className}`}
    >
      {children}
    </span>
  )
}