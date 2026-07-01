import { useLocation, useNavigate } from 'react-router-dom'
import { clsx } from 'clsx'
import { useUIStore } from '@/stores/uiStore'
import { NAV_ITEMS } from '@/utils/constants'
import { useState } from 'react'
import type { NavItem } from '@/types/ui'

function NavItemComponent({ item, depth = 0, collapsed, onNavigate }: {
  item: NavItem
  depth?: number
  collapsed: boolean
  onNavigate: (path: string) => void
}) {
  const [expanded, setExpanded] = useState(false)
  const location = useLocation()
  const isActive = item.path === '/dashboard'
    ? location.pathname === '/dashboard'
    : location.pathname.startsWith(item.path)
  const hasChildren = item.children && item.children.length > 0

  return (
    <div>
      <button
        onClick={() => {
          if (hasChildren && collapsed) {
            setExpanded(!expanded)
          } else if (hasChildren) {
            setExpanded(!expanded)
          } else {
            onNavigate(item.path)
          }
        }}
        className={clsx(
          'w-full flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-colors',
          isActive ? 'bg-primary-50 text-primary-700 font-medium' : 'text-gray-600 hover:bg-gray-100',
          collapsed && 'justify-center px-2'
        )}
        title={collapsed ? item.label : undefined}
      >
        <span className="text-base flex-shrink-0">{item.icon}</span>
        {!collapsed && (
          <>
            <span className="truncate flex-1 text-left">{item.label}</span>
            {item.badge !== undefined && (
              <span className="bg-danger-500 text-white text-xs rounded-full px-1.5 py-0.5 min-w-[18px] text-center">
                {item.badge}
              </span>
            )}
            {hasChildren && (
              <svg className={clsx('w-4 h-4 text-gray-400 transition-transform', expanded && 'rotate-90')} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            )}
          </>
        )}
      </button>
      {hasChildren && expanded && !collapsed && (
        <div className="ml-6 mt-1 space-y-0.5">
          {item.children!.map((child) => (
            <NavItemComponent key={child.path} item={child} depth={depth + 1} collapsed={false} onNavigate={onNavigate} />
          ))}
        </div>
      )}
    </div>
  )
}

export function Sidebar() {
  const { sidebarOpen, sidebarCollapsed, toggleSidebarCollapse } = useUIStore()
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <>
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/30 z-20 lg:hidden" onClick={() => useUIStore.getState().toggleSidebar()} />
      )}
      <aside className={clsx(
        'fixed lg:static inset-y-0 left-0 z-20 bg-white border-r border-gray-200 flex flex-col transition-all duration-200',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
        sidebarCollapsed ? 'w-16' : 'w-60'
      )}>
        <div className="flex-1 overflow-y-auto scrollbar-thin py-3 px-2 space-y-0.5">
          {NAV_ITEMS.map((item) => (
            <NavItemComponent key={item.path} item={item} collapsed={sidebarCollapsed} onNavigate={navigate} />
          ))}
        </div>

        <div className="border-t border-gray-200 p-2">
          <button
            onClick={toggleSidebarCollapse}
            className="w-full flex items-center justify-center p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
            title={sidebarCollapsed ? 'Mở rộng' : 'Thu gọn'}
          >
            <svg className={clsx('w-4 h-4 transition-transform', sidebarCollapsed && 'rotate-180')} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
            </svg>
          </button>
        </div>
      </aside>
    </>
  )
}
