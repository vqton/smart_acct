import { useUIStore } from '@/stores/uiStore'
import { useAuthStore } from '@/stores/authStore'

export function TopBar() {
  const { sidebarOpen, toggleSidebar, currentLang, setLang, currentPeriod } = useUIStore()
  const { user, logout } = useAuthStore()

  return (
    <header className="h-14 bg-primary-500 text-white flex items-center justify-between px-4 shadow-md z-30 relative">
      <div className="flex items-center gap-3">
        <button onClick={toggleSidebar} className="p-1.5 rounded hover:bg-primary-600 transition-colors">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={sidebarOpen ? 'M6 18L18 6M6 6l12 12' : 'M4 6h16M4 12h16M4 18h16'} />
          </svg>
        </button>
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold tracking-tight">SmartACCT</span>
          <span className="hidden md:inline text-xs bg-primary-400 px-2 py-0.5 rounded">v2.0</span>
        </div>
        {currentPeriod && (
          <span className="hidden sm:inline text-xs bg-white/20 px-2 py-0.5 rounded">
            {currentPeriod}
          </span>
        )}
      </div>

      <div className="flex items-center gap-2">
        <button className="p-2 hover:bg-primary-600 rounded relative" title="Thông báo">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <span className="absolute top-1 right-1 w-2 h-2 bg-danger-400 rounded-full" />
        </button>

        <button
          onClick={() => setLang(currentLang === 'vi' ? 'en' : 'vi')}
          className="px-2 py-1 text-xs font-medium hover:bg-primary-600 rounded"
        >
          {currentLang === 'vi' ? 'EN' : 'VI'}
        </button>

        <div className="flex items-center gap-2 ml-2 pl-2 border-l border-primary-400">
          <div className="w-7 h-7 rounded-full bg-primary-300 flex items-center justify-center text-sm font-medium">
            {user?.username?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div className="hidden sm:block">
            <p className="text-sm leading-tight">{user?.username || 'User'}</p>
            <p className="text-xs text-primary-200">{user?.role || 'Kế toán'}</p>
          </div>
          <button onClick={logout} className="p-1.5 hover:bg-primary-600 rounded ml-1" title="Đăng xuất">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </div>
    </header>
  )
}
