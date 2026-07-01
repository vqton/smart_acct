import React from 'react'
import { clsx } from 'clsx'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  icon?: React.ReactNode
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, icon, className, id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-')
    return (
      <div className="space-y-1">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-gray-700">
            {label}
          </label>
        )}
        <div className="relative">
          {icon && <div className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400">{icon}</div>}
          <input
            ref={ref}
            id={inputId}
            className={clsx(
              'block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm placeholder:text-gray-400',
              'focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500',
              'disabled:bg-gray-50 disabled:text-gray-500',
              icon && 'pl-10',
              error && 'border-danger-400 focus:border-danger-500 focus:ring-danger-500',
              className
            )}
            {...props}
          />
        </div>
        {error && <p className="text-xs text-danger-500">{error}</p>}
      </div>
    )
  }
)
Input.displayName = 'Input'
