import { clsx } from 'clsx'

interface CardProps {
  title?: string
  subtitle?: string
  children: React.ReactNode
  className?: string
  actions?: React.ReactNode
}

export function Card({ title, subtitle, children, className, actions }: CardProps) {
  return (
    <div className={clsx('bg-white rounded-lg border border-gray-200 shadow-sm', className)}>
      {(title || actions) && (
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
          <div>
            {title && <h3 className="text-sm font-semibold text-gray-900">{title}</h3>}
            {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
          </div>
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </div>
      )}
      <div className="p-4">{children}</div>
    </div>
  )
}

export function StatCard({ label, value, icon, trend, className }: {
  label: string
  value: string
  icon?: React.ReactNode
  trend?: { value: string; positive: boolean }
  className?: string
}) {
  return (
    <div className={clsx('bg-white rounded-lg border border-gray-200 p-4 shadow-sm', className)}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{label}</p>
          <p className="text-xl font-bold text-gray-900 mt-1 font-mono tabular-nums">{value}</p>
          {trend && (
            <p className={clsx('text-xs mt-1', trend.positive ? 'text-success-500' : 'text-danger-500')}>
              {trend.positive ? '↑' : '↓'} {trend.value}
            </p>
          )}
        </div>
        {icon && <div className="text-gray-300 text-2xl">{icon}</div>}
      </div>
    </div>
  )
}
