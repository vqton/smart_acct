export interface NavItem {
  label: string
  labelEn: string
  icon: string
  path: string
  children?: NavItem[]
  badge?: number
}

export interface SortConfig {
  key: string
  direction: 'asc' | 'desc'
}

export interface TableColumn<T> {
  key: string
  label: string
  labelEn?: string
  sortable?: boolean
  width?: string
  render?: (row: T) => React.ReactNode
  align?: 'left' | 'right' | 'center'
}

export interface FilterConfig {
  key: string
  label: string
  type: 'text' | 'select' | 'date' | 'date-range'
  options?: { value: string; label: string }[]
}

export interface BreadcrumbItem {
  label: string
  path?: string
}
