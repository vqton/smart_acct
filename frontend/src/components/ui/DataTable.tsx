import React, { useState } from 'react'
import { clsx } from 'clsx'
import type { TableColumn, SortConfig } from '@/types/ui'

interface DataTableProps<T> {
  columns: TableColumn<T>[]
  data: T[]
  keyExtractor: (row: T) => string | number
  loading?: boolean
  onRowClick?: (row: T) => void
  selectedIds?: Set<string | number>
  onSelect?: (id: string | number) => void
  onSelectAll?: () => void
  sortable?: boolean
  emptyMessage?: string
  page?: number
  pageSize?: number
  total?: number
  onPageChange?: (page: number) => void
}

export function DataTable<T extends Record<string, any>>({
  columns, data, keyExtractor, loading, onRowClick, selectedIds, onSelect, onSelectAll,
  sortable = true, emptyMessage = 'Không có dữ liệu',
  page, pageSize, total, onPageChange,
}: DataTableProps<T>) {
  const [sort, setSort] = useState<SortConfig | null>(null)

  const sorted = React.useMemo(() => {
    if (!sort) return data
    return [...data].sort((a, b) => {
      const aVal = a[sort.key] ?? ''
      const bVal = b[sort.key] ?? ''
      const cmp = String(aVal).localeCompare(String(bVal), 'vi', { numeric: true })
      return sort.direction === 'asc' ? cmp : -cmp
    })
  }, [data, sort])

  const totalPages = total ? Math.ceil(total / (pageSize || 20)) : 1

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div className="overflow-x-auto scrollbar-thin">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {(onSelect || onSelectAll) && (
                <th className="w-10 px-3 py-3">
                  {onSelectAll && (
                    <input type="checkbox" className="rounded border-gray-300" onChange={onSelectAll}
                      checked={selectedIds?.size === data.length && data.length > 0} />
                  )}
                </th>
              )}
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={clsx(
                    'px-4 py-3 text-xs font-semibold text-gray-600 uppercase tracking-wider',
                    col.align === 'right' && 'text-right',
                    col.align === 'center' && 'text-center',
                    sortable && col.sortable !== false && 'cursor-pointer select-none hover:text-gray-900'
                  )}
                  style={col.width ? { width: col.width, minWidth: col.width } : undefined}
                  onClick={() => {
                    if (!sortable || col.sortable === false) return
                    setSort((s) => s?.key === col.key
                      ? { key: col.key, direction: s.direction === 'asc' ? 'desc' : 'asc' }
                      : { key: col.key, direction: 'asc' })
                  }}
                >
                  <span className="inline-flex items-center gap-1">
                    {col.label}
                    {sort?.key === col.key && (
                      <span className="text-primary-500">{sort.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i}>
                  {columns.map((col) => (
                    <td key={col.key} className="px-4 py-3">
                      <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4" />
                    </td>
                  ))}
                </tr>
              ))
            ) : sorted.length === 0 ? (
              <tr>
                <td colSpan={columns.length + (onSelect ? 1 : 0)} className="px-6 py-12 text-center text-gray-400">
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              sorted.map((row) => (
                <tr
                  key={keyExtractor(row)}
                  className={clsx(
                    'transition-colors',
                    onRowClick && 'cursor-pointer hover:bg-blue-50',
                    selectedIds?.has(keyExtractor(row)) && 'bg-blue-50'
                  )}
                  onClick={() => onRowClick?.(row)}
                >
                  {onSelect && (
                    <td className="w-10 px-3 py-3">
                      <input type="checkbox" className="rounded border-gray-300"
                        checked={selectedIds?.has(keyExtractor(row)) || false}
                        onChange={() => onSelect(keyExtractor(row))} />
                    </td>
                  )}
                  {columns.map((col) => (
                    <td
                      key={col.key}
                      className={clsx(
                        'px-4 py-3 text-sm whitespace-nowrap',
                        col.align === 'right' && 'text-right font-mono',
                        col.align === 'center' && 'text-center'
                      )}
                    >
                      {col.render ? col.render(row) : row[col.key] ?? '—'}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      {total !== undefined && totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 bg-gray-50">
          <span className="text-sm text-gray-500">
            {total} bản ghi
          </span>
          <div className="flex gap-1">
            <button
              disabled={!page || page <= 1}
              onClick={() => onPageChange?.((page || 1) - 1)}
              className="px-3 py-1 text-sm rounded border border-gray-300 disabled:opacity-50 hover:bg-gray-100"
            >
              ‹
            </button>
            <span className="px-3 py-1 text-sm text-gray-600">
              {page || 1} / {totalPages}
            </span>
            <button
              disabled={!page || page >= totalPages}
              onClick={() => onPageChange?.((page || 1) + 1)}
              className="px-3 py-1 text-sm rounded border border-gray-300 disabled:opacity-50 hover:bg-gray-100"
            >
              ›
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
