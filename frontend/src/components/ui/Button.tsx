import React from 'react'
import { clsx } from 'clsx'

type Variant = 'primary' | 'secondary' | 'success' | 'danger' | 'ghost'
type Size = 'sm' | 'md' | 'lg'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  loading?: boolean
  icon?: React.ReactNode
}

const variantStyles: Record<Variant, string> = {
  primary:   'bg-primary-500 text-white hover:bg-primary-600 active:bg-primary-700 shadow-sm',
  secondary: 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 active:bg-gray-100',
  success:   'bg-success-500 text-white hover:bg-success-600 shadow-sm',
  danger:    'bg-danger-500 text-white hover:bg-danger-600 shadow-sm',
  ghost:     'text-gray-600 hover:bg-gray-100 active:bg-gray-200',
}

const sizeStyles: Record<Size, string> = {
  sm: 'px-2.5 py-1.5 text-xs gap-1',
  md: 'px-4 py-2 text-sm gap-1.5',
  lg: 'px-6 py-2.5 text-base gap-2',
}

export function Button({
  variant = 'primary', size = 'md', loading, icon, children, className, disabled, ...props
}: ButtonProps) {
  return (
    <button
      className={clsx(
        'inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-primary-300 disabled:opacity-50 disabled:cursor-not-allowed',
        variantStyles[variant], sizeStyles[size], className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      ) : icon}
      {children}
    </button>
  )
}
