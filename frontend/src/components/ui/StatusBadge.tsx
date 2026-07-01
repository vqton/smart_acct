import { clsx } from 'clsx'
import { STATUS_MAP } from '@/utils/constants'

interface StatusBadgeProps {
  status: string
  className?: string
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const cfg = STATUS_MAP[status] || { label: status, color: 'text-gray-600', bg: 'bg-gray-100' }
  return (
    <span className={clsx('inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium', cfg.color, cfg.bg, className)}>
      {cfg.label}
    </span>
  )
}
