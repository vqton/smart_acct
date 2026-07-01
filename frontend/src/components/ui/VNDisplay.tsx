import { clsx } from 'clsx'
import { fmtVND } from '@/utils/formatters'

interface VNDisplayProps {
  amount: string | number | null | undefined
  className?: string
  currency?: string
}

export function VNDisplay({ amount, className, currency = 'VND' }: VNDisplayProps) {
  const formatted = fmtVND(amount)
  const negative = typeof amount === 'string' ? parseFloat(amount) < 0 : (amount ?? 0) < 0
  return (
    <span className={clsx('font-mono tabular-nums', negative ? 'text-danger-500' : 'text-gray-900', className)}>
      {formatted}
      {amount !== null && amount !== undefined && amount !== '' && (
        <span className="text-gray-400 ml-0.5 text-xs">{currency === 'VND' ? 'đ' : currency}</span>
      )}
    </span>
  )
}
