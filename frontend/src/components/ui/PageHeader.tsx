import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from './Button'
import type { BreadcrumbItem } from '@/types/ui'

interface PageHeaderProps {
  title: string
  subtitle?: string
  breadcrumbs?: BreadcrumbItem[]
  actions?: React.ReactNode
  onAdd?: { label: string; onClick: () => void } | { label: string; path: string }
}

export function PageHeader({ title, subtitle, breadcrumbs, actions, onAdd }: PageHeaderProps) {
  const navigate = useNavigate()
  return (
    <div className="mb-4 space-y-2">
      {breadcrumbs && breadcrumbs.length > 0 && (
        <nav className="flex items-center text-xs text-gray-500 gap-1">
          {breadcrumbs.map((b, i) => (
            <React.Fragment key={i}>
              {i > 0 && <span>/</span>}
              {b.path ? (
                <button onClick={() => b.path && navigate(b.path)} className="hover:text-primary-600 transition-colors">{b.label}</button>
              ) : (
                <span className="text-gray-700">{b.label}</span>
              )}
            </React.Fragment>
          ))}
        </nav>
      )}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{title}</h1>
          {subtitle && <p className="text-sm text-gray-500 mt-0.5">{subtitle}</p>}
        </div>
        <div className="flex items-center gap-2">
          {actions}
          {onAdd && (
            <Button onClick={() => 'path' in onAdd ? navigate(onAdd.path) : onAdd.onClick()} icon={<span>+</span>}>
              {onAdd.label}
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
